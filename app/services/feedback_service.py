"""Validated, throttled user feedback and beta-reward eligibility."""

from datetime import datetime, timezone
from typing import NamedTuple

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app import models
from app.services import auth_rate_limit_service, growth_service
from app.services.ai_usage_service import get_positive_int_setting


CATEGORIES = frozenset({"bug", "idea", "result_quality", "interface", "other"})
STATUSES = frozenset({"new", "in_progress", "resolved", "rejected"})
REPORT_QUESTION_KEY = "report_helpfulness_v1"


class Submission(NamedTuple):
    feedback: models.UserFeedback
    created: bool


def report_answer(db, user_id):
    return db.query(models.UserFeedback).filter_by(
        user_id=user_id, question_key=REPORT_QUESTION_KEY,
    ).one_or_none()


def has_report_answer(db, user_id):
    return report_answer(db, user_id) is not None


def submit(db, request, *, user, category, rating, message, page_path,
           allow_email_reply, project_id=None, report_question=False):
    if category not in CATEGORIES:
        raise HTTPException(400, "Выберите категорию обращения.")
    if rating is not None and (isinstance(rating, bool) or rating not in range(1, 6)):
        raise HTTPException(400, "Оценка должна быть от 1 до 5.")
    if report_question and (category != "result_quality" or rating is None or project_id is None):
        raise HTTPException(400, "Выберите оценку отчёта от 1 до 5.")
    message = message.strip()
    if report_question and not message:
        message = "Оценка итогового отчёта."
    if not (1 if report_question else 10) <= len(message) <= 2000:
        detail = ("Комментарий должен содержать не более 2000 символов."
                  if report_question else "Сообщение должно содержать от 10 до 2000 символов.")
        raise HTTPException(400, detail)
    if not page_path.startswith("/") or "://" in page_path or len(page_path) > 500:
        page_path = "/feedback"
    project = None
    if project_id is not None:
        project = db.query(models.Project).filter_by(id=project_id, owner_id=user.id).one_or_none()
        if project is None:
            raise HTTPException(404, "Проект не найден.")
    if report_question:
        page_path = f"/projects/{project.id}/report"
        previous = report_answer(db, user.id)
        if previous is not None:
            return Submission(previous, False)
    auth_rate_limit_service.consume(
        db, scope="feedback_user", identity=str(user.id),
        limit=get_positive_int_setting("FEEDBACK_USER_LIMIT", 5), seconds=3600,
    )
    if report_question:
        # The rate limiter commits separately. Lock/recheck AFTER it, so two
        # tabs cannot create two answers. The unique key also covers SQLite.
        db.query(models.User).filter_by(id=user.id).with_for_update().one()
        previous = report_answer(db, user.id)
        if previous is not None:
            return Submission(previous, False)
    feedback = models.UserFeedback(
        user_id=user.id, project_id=project.id if project else None,
        category=category, rating=rating, message=message, page_path=page_path,
        question_key=REPORT_QUESTION_KEY if report_question else None,
        allow_email_reply=bool(allow_email_reply), status="new",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    db.add(feedback)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        previous = report_answer(db, user.id) if report_question else None
        if previous is None:
            raise
        return Submission(previous, False)
    db.refresh(feedback)
    growth_service.update_beta_reward_eligibility(db, user)
    return Submission(feedback, True)


def update_status(db, *, feedback_id, status, admin_note):
    if status not in STATUSES:
        raise HTTPException(400, "Некорректный статус обращения.")
    feedback = db.get(models.UserFeedback, feedback_id)
    if feedback is None:
        raise HTTPException(404, "Обращение не найдено.")
    note = admin_note.strip()
    if len(note) > 2000:
        raise HTTPException(400, "Комментарий слишком длинный.")
    feedback.status = status
    feedback.admin_note = note or None
    feedback.updated_at = datetime.now(timezone.utc)
    feedback.resolved_at = feedback.updated_at if status in {"resolved", "rejected"} else None
    db.commit()
    db.refresh(feedback)
    return feedback

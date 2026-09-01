"""Validated, throttled user feedback and beta-reward eligibility."""

from datetime import datetime, timezone

from fastapi import HTTPException

from app import models
from app.services import auth_rate_limit_service, growth_service
from app.services.ai_usage_service import get_positive_int_setting


CATEGORIES = frozenset({"bug", "idea", "result_quality", "interface", "other"})
STATUSES = frozenset({"new", "in_progress", "resolved", "rejected"})


def submit(db, request, *, user, category, rating, message, page_path,
           allow_email_reply, project_id=None):
    auth_rate_limit_service.consume(
        db, scope="feedback_user", identity=str(user.id),
        limit=get_positive_int_setting("FEEDBACK_USER_LIMIT", 5), seconds=3600,
    )
    if category not in CATEGORIES:
        raise HTTPException(400, "Выберите категорию обращения.")
    if rating is not None and (isinstance(rating, bool) or rating not in range(1, 6)):
        raise HTTPException(400, "Оценка должна быть от 1 до 5.")
    message = message.strip()
    if not 10 <= len(message) <= 2000:
        raise HTTPException(400, "Сообщение должно содержать от 10 до 2000 символов.")
    if not page_path.startswith("/") or "://" in page_path or len(page_path) > 500:
        page_path = "/feedback"
    project = None
    if project_id is not None:
        project = db.query(models.Project).filter_by(id=project_id, owner_id=user.id).one_or_none()
        if project is None:
            raise HTTPException(404, "Проект не найден.")
    feedback = models.UserFeedback(
        user_id=user.id, project_id=project.id if project else None,
        category=category, rating=rating, message=message, page_path=page_path,
        allow_email_reply=bool(allow_email_reply), status="new",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    growth_service.update_beta_reward_eligibility(db, user)
    return feedback


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

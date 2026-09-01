"""Privacy-minimised product events and monetisation experiment state."""

import json
import os
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app import models


EVENTS = frozenset({
    "trial_ai_project_started", "result_calculated", "report_generated",
    "second_project_created", "pricing_viewed", "paid_offer_viewed",
    "project_99_selected", "pro_299_selected", "free_beta_selected",
})
PLANS = frozenset({"project_99", "pro_299", "free_beta"})
SOURCES = frozenset({"pricing", "report", "second_project_ai"})
EVENT_FOR_PLAN = {
    "project_99": "project_99_selected",
    "pro_299": "pro_299_selected",
    "free_beta": "free_beta_selected",
}
SAFE_METADATA = {
    "paid_offer_viewed": {"source"},
    "project_99_selected": {"source"},
    "pro_299_selected": {"source"},
    "free_beta_selected": {"source"},
}


def _number_set(name):
    return {int(value.strip()) for value in os.getenv(name, "").split(",")
            if value.strip().isdigit()}


def _email_set(name):
    return {value.strip().casefold() for value in os.getenv(name, "").split(",")
            if value.strip()}


def is_marketing_excluded(user):
    if user is None:
        return False
    excluded_ids = _number_set("ADMIN_USER_IDS") | _number_set("MARKETING_EXCLUDED_USER_IDS")
    return user.id in excluded_ids or user.email.casefold() in _email_set("MARKETING_TEST_EMAILS")


def excluded_user_ids(db):
    configured = _number_set("ADMIN_USER_IDS") | _number_set("MARKETING_EXCLUDED_USER_IDS")
    emails = _email_set("MARKETING_TEST_EMAILS")
    if emails:
        configured.update(user_id for (user_id,) in db.query(models.User.id).filter(
            func.lower(models.User.email).in_(emails)
        ))
    return configured


def _metadata(event_name, metadata):
    allowed = SAFE_METADATA.get(event_name, set())
    cleaned = {}
    for key, value in (metadata or {}).items():
        if key not in allowed:
            continue
        if isinstance(value, str) and len(value) <= 50:
            cleaned[key] = value
        elif isinstance(value, (bool, int)) and not isinstance(value, float):
            cleaned[key] = value
    return json.dumps(cleaned, ensure_ascii=False, separators=(",", ":"))


def record_event(db, event_name, *, user=None, user_id=None, project_id=None,
                 metadata=None, dedupe_key=None, now=None):
    if event_name not in EVENTS:
        raise ValueError("Неизвестное продуктовое событие.")
    if user is None and user_id is not None:
        user = db.get(models.User, user_id)
    if is_marketing_excluded(user):
        return None
    event = models.ProductEvent(
        user_id=user.id if user is not None else user_id,
        project_id=project_id,
        event_name=event_name,
        metadata_json=_metadata(event_name, metadata),
        dedupe_key=dedupe_key,
        created_at=now or datetime.now(timezone.utc),
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if dedupe_key:
            return db.query(models.ProductEvent).filter_by(dedupe_key=dedupe_key).one_or_none()
        raise
    db.refresh(event)
    return event


def record_trial_ai_project(db, *, user_id, project_id):
    user = db.get(models.User, user_id)
    return record_event(
        db, "trial_ai_project_started", user=user, project_id=project_id,
        dedupe_key=f"trial_ai_project_started:user:{user_id}",
    )


def first_trial_project_id(db, user_id):
    return db.query(models.ProductEvent.project_id).filter_by(
        user_id=user_id, event_name="trial_ai_project_started",
    ).order_by(models.ProductEvent.created_at, models.ProductEvent.id).scalar()


def has_event(db, event_name, *, user_id, project_id=None):
    query = db.query(models.ProductEvent.id).filter_by(user_id=user_id, event_name=event_name)
    if project_id is not None:
        query = query.filter(models.ProductEvent.project_id == project_id)
    return query.first() is not None


def record_project_value(db, *, user, project_id, results, report=False):
    if not results or first_trial_project_id(db, user.id) != project_id:
        return None
    name = "report_generated" if report else "result_calculated"
    event = record_event(
        db, name, user=user, project_id=project_id,
        dedupe_key=f"{name}:user:{user.id}:project:{project_id}",
    )
    if not report and event is not None:
        update_beta_reward_eligibility(db, user)
    return event


def record_second_project(db, *, user, project_id):
    project_count = db.query(func.count(models.Project.id)).filter_by(owner_id=user.id).scalar() or 0
    if project_count < 2 or has_event(
        db, "second_project_created", user_id=user.id,
    ):
        return None
    return record_event(
        db, "second_project_created", user=user, project_id=project_id,
        dedupe_key=f"second_project_created:user:{user.id}",
    )


def should_offer_for_second_project(db, *, user_id, project_id):
    trial_id = first_trial_project_id(db, user_id)
    return bool(
        trial_id and trial_id != project_id
        and has_event(db, "result_calculated", user_id=user_id, project_id=trial_id)
        and preference_for(db, user_id) is None
        and not has_event(
            db, "paid_offer_viewed", user_id=user_id, project_id=project_id,
        )
    )


def preference_for(db, user_id):
    return db.query(models.MonetizationPreference).filter_by(user_id=user_id).one_or_none()


def save_preference(db, *, user, selected_plan, source):
    if selected_plan not in PLANS or source not in SOURCES:
        raise ValueError("Некорректный вариант тарифа.")
    current = datetime.now(timezone.utc)
    preference = preference_for(db, user.id)
    if preference is None:
        preference = models.MonetizationPreference(user_id=user.id, created_at=current)
        db.add(preference)
    preference.selected_plan = selected_plan
    preference.notify_on_launch = selected_plan != "free_beta"
    preference.source = source
    preference.updated_at = current
    db.commit()
    db.refresh(preference)
    record_event(
        db, EVENT_FOR_PLAN[selected_plan], user=user,
        metadata={"source": source},
    )
    return preference


def update_beta_reward_eligibility(db, user):
    if user.beta_reward_eligible or user.beta_reward_granted or not user.email_verified:
        return user.beta_reward_eligible
    completed = has_event(db, "result_calculated", user_id=user.id)
    feedback_exists = db.query(models.UserFeedback.id).filter_by(user_id=user.id).first() is not None
    if completed and feedback_exists:
        user.beta_reward_eligible = True
        user.beta_reward_eligible_at = datetime.now(timezone.utc)
        user.beta_reward_reason = "verified_result_and_feedback"
        db.commit()
        db.refresh(user)
    return user.beta_reward_eligible

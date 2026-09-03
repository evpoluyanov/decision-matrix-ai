"""Read-only aggregates. No prompts, passwords, email lists or API keys."""

import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from sqlalchemy import func, select

from app import models
from app.auth_dependencies import require_user
from app.services import growth_service
from app.services.ai_budget_service import (
    AIBudgetConfigurationError, BUDGET_TIMEZONE, daily_limit_microrub, get_pricing,
)


def is_admin(user):
    values = os.getenv("ADMIN_USER_IDS", "").split(",")
    return user.email_verified and str(user.id) in {v.strip() for v in values if v.strip().isdigit()}


def require_admin(user=Depends(require_user)):
    if not is_admin(user):
        raise HTTPException(403, "Доступ только для администратора.")
    return user


def statistics(db, days, now=None, feedback_category=None, feedback_status=None):
    current = now or datetime.now(timezone.utc)
    today = current.astimezone(BUDGET_TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
    start = (
        datetime(1970, 1, 1, tzinfo=timezone.utc)
        if days == "all"
        else (today - timedelta(days=int(days) - 1)).astimezone(timezone.utc)
    )
    users = models.User
    logs = models.AIRequestLog
    calls = models.AIProviderCall
    scope = (logs.created_at >= start, logs.created_at <= current)
    call_scope = (calls.created_at >= start, calls.created_at <= current)
    count = lambda query: db.scalar(query) or 0
    budget = db.get(models.AIDailyBudget, today.date())
    allocated = budget.allocated_microrub if budget else 0
    try:
        limit = daily_limit_microrub()
    except AIBudgetConfigurationError:
        limit = None
    pricing = None
    configuration_error = None
    try:
        pricing = get_pricing()
    except AIBudgetConfigurationError as exc:
        configuration_error = str(exc)
    features = db.execute(select(
        logs.feature, logs.status, func.count(logs.id),
    ).where(*scope).group_by(logs.feature, logs.status).order_by(logs.feature, logs.status)).all()
    excluded = growth_service.excluded_user_ids(db)
    marketing_user = ~users.id.in_(excluded) if excluded else True
    events = models.ProductEvent
    event_scope = (events.created_at >= start, events.created_at <= current)
    offer_users = select(events.user_id).where(*event_scope,
        events.event_name == "paid_offer_viewed", events.user_id.is_not(None)).distinct()
    if excluded:
        offer_users = offer_users.where(~events.user_id.in_(excluded))

    def current_choice(plan):
        return count(select(func.count(models.MonetizationPreference.user_id)).where(
            models.MonetizationPreference.user_id.in_(offer_users),
            models.MonetizationPreference.selected_plan == plan,
        ))

    def unique_event(name):
        query = select(func.count(func.distinct(events.user_id))).where(
            *event_scope, events.event_name == name, events.user_id.is_not(None),
        )
        if excluded:
            query = query.where(~events.user_id.in_(excluded))
        return count(query)

    registered = count(select(func.count(users.id)).where(
        users.created_at >= start, users.created_at <= current, marketing_user,
    ))
    verified = count(select(func.count(users.id)).where(
        users.created_at >= start, users.created_at <= current,
        users.email_verified.is_(True), marketing_user,
    ))
    project_query = select(func.count(func.distinct(models.Project.owner_id))).join(
        users, users.id == models.Project.owner_id,
    ).where(models.Project.created_at >= start, models.Project.created_at <= current, marketing_user)
    project_users = count(project_query)
    funnel = {
        "registered": registered,
        "verified": verified,
        "project_created": project_users,
        "trial_ai": unique_event("trial_ai_project_started"),
        "result": unique_event("result_calculated"),
        "report": unique_event("report_generated"),
        "second_project": unique_event("second_project_created"),
        "offer": unique_event("paid_offer_viewed"),
        "project_99": current_choice("project_99"),
        "pro_299": current_choice("pro_299"),
        "free_beta": current_choice("free_beta"),
    }
    for key in ("project_99", "pro_299", "free_beta"):
        funnel[f"{key}_conversion"] = (
            funnel[key] * 100 / funnel["offer"] if funnel["offer"] else 0
        )
    funnel["no_choice"] = max(0, funnel["offer"] - sum(funnel[key] for key in ("project_99", "pro_299", "free_beta")))
    completed = select(events.project_id, events.user_id).where(
        *event_scope, events.event_name == "result_calculated", events.project_id.is_not(None),
    )
    if excluded:
        completed = completed.where(~events.user_id.in_(excluded))
    completed = completed.distinct().subquery()
    completed_projects = count(select(func.count(func.distinct(completed.c.project_id))))
    completed_cost = count(select(func.sum(calls.estimated_microrub)).join(
        logs, logs.id == calls.request_log_id,
    ).join(completed, completed.c.project_id == logs.project_id)) / 1_000_000
    funnel["average_completed_cost"] = (
        completed_cost / completed_projects if completed_projects else 0
    )

    activated_ids = {row[0] for row in db.execute(select(events.user_id).where(
        *event_scope, events.event_name == "result_calculated", events.user_id.is_not(None),
    )).all() if row[0] not in excluded}
    source_rows = {}
    attribution_query = select(models.UserAttribution).where(
        models.UserAttribution.created_at >= start,
        models.UserAttribution.created_at <= current,
    )
    if excluded:
        attribution_query = attribution_query.where(~models.UserAttribution.user_id.in_(excluded))
    for attribution in db.scalars(attribution_query):
        source = attribution.utm_source or attribution.referrer or "Прямой/неизвестный"
        item = source_rows.setdefault(source, {"source": source, "users": 0, "activated": 0})
        item["users"] += 1
        item["activated"] += int(attribution.user_id in activated_ids)

    feedback_query = db.query(models.UserFeedback, models.User).join(
        models.User, models.User.id == models.UserFeedback.user_id,
    ).filter(models.UserFeedback.created_at >= start, models.UserFeedback.created_at <= current)
    if feedback_category:
        feedback_query = feedback_query.filter(models.UserFeedback.category == feedback_category)
    if feedback_status:
        feedback_query = feedback_query.filter(models.UserFeedback.status == feedback_status)
    feedback_rows = feedback_query.order_by(models.UserFeedback.created_at.desc()).limit(200).all()
    latest_reconciliation = db.query(models.MWSBillingReconciliation).order_by(
        models.MWSBillingReconciliation.created_at.desc(),
    ).first()
    return {
        "days": days, "start": start.astimezone(BUDGET_TIMEZONE),
        "updated_at": current.astimezone(BUDGET_TIMEZONE),
        "accounts": count(select(func.count(users.id))),
        "verified_accounts": count(select(func.count(users.id)).where(users.email_verified.is_(True))),
        "new_accounts": count(select(func.count(users.id)).where(users.created_at >= start, users.created_at <= current)),
        "active_ai_accounts": count(select(func.count(func.distinct(logs.user_id))).where(*scope)),
        "requests": count(select(func.count(logs.id)).where(*scope)),
        "input_tokens": count(select(func.sum(calls.input_tokens)).where(*call_scope)),
        "output_tokens": count(select(func.sum(calls.output_tokens)).where(*call_scope)),
        "reasoning_tokens": count(select(func.sum(calls.reasoning_tokens)).where(*call_scope)),
        "estimated": count(select(func.sum(calls.estimated_microrub)).where(*call_scope)) / 1_000_000,
        "uncertain_calls": count(select(func.count(calls.id)).where(*call_scope, calls.status != "reported")),
        "uncertain_reserve": count(select(func.sum(calls.charged_microrub)).where(
            *call_scope, calls.status != "reported")) / 1_000_000,
        "today_allocated": allocated / 1_000_000,
        "today_remaining": max(0, limit - allocated) / 1_000_000 if limit is not None else None,
        "daily_limit": limit / 1_000_000 if limit is not None else None,
        "pricing": pricing,
        "configuration_error": configuration_error,
        "features": features,
        "recent_calls": db.query(calls, logs).outerjoin(logs, logs.id == calls.request_log_id).filter(*call_scope).order_by(calls.id.desc()).limit(30).all(),
        "ai_enabled": os.getenv("AI_ENABLED", "true").lower() == "true",
        "pricing_confirmed": os.getenv("AI_PRICING_CONFIRMED", "false").lower() == "true",
        "funnel": funnel,
        "sources": sorted(source_rows.values(), key=lambda row: (-row["users"], row["source"])),
        "feedback_rows": feedback_rows,
        "new_feedback": count(select(func.count(models.UserFeedback.id)).where(
            models.UserFeedback.status == "new",
        )),
        "feedback_category": feedback_category,
        "feedback_status": feedback_status,
        "latest_reconciliation": latest_reconciliation,
    }

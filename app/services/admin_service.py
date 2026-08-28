"""Read-only aggregates. No prompts, passwords, email lists or API keys."""

import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from sqlalchemy import func, select

from app import models
from app.auth_dependencies import require_user
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


def statistics(db, days, now=None):
    current = now or datetime.now(timezone.utc)
    today = current.astimezone(BUDGET_TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
    start = (today - timedelta(days=days - 1)).astimezone(timezone.utc)
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
        "ai_enabled": os.getenv("AI_ENABLED", "true").lower() == "true",
        "pricing_confirmed": os.getenv("AI_PRICING_CONFIRMED", "false").lower() == "true",
    }

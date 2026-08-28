"""Database-backed, bounded-window throttles, applied before password hashing/mail."""

import hashlib
import hmac
import ipaddress
import math
import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from sqlalchemy import case, delete, or_, select

from app import models
from app.services.ai_usage_service import get_positive_int_setting
from app.services.db_counters import insert_for


def client_address(request: Request) -> str:
    # This header is authoritative only when the app runs behind Vercel itself.
    # Never trust arbitrary client-supplied X-Forwarded-For on local/other hosts.
    vercel = os.getenv("VERCEL") == "1"
    raw = request.headers.get("x-vercel-forwarded-for", "") if vercel else (
        request.client.host if request.client else "unknown"
    )
    try:
        address = ipaddress.ip_address(raw.strip())
    except ValueError:
        if vercel:
            raise HTTPException(503, "Не удалось проверить источник запроса.")
        return "local-unknown"
    if address.version == 6:
        return str(ipaddress.ip_network(f"{address}/64", strict=False))
    return str(address)


def consume(db, *, scope: str, identity: str, limit: int, seconds: int, now=None):
    current = now or datetime.now(timezone.utc)
    if current.utcoffset() is None:
        raise ValueError("Требуется время с часовым поясом.")
    current = current.astimezone(timezone.utc)
    secret = os.environ["SESSION_SECRET"].encode()
    key = hmac.new(secret, f"{scope}:{identity}".encode(), hashlib.sha256).hexdigest()
    table = models.AuthRateLimit
    expired = table.expires_at <= current
    # Retain no per-attempt journal and remove old counters opportunistically.
    db.execute(delete(table).where(table.expires_at < current - timedelta(days=1)))
    statement = insert_for(db, table).values(
        key=key, attempts=1, expires_at=current + timedelta(seconds=seconds),
    ).on_conflict_do_update(
        index_elements=[table.key],
        set_={
            "attempts": case((expired, 1), else_=table.attempts + 1),
            "expires_at": case(
                (expired, current + timedelta(seconds=seconds)), else_=table.expires_at,
            ),
        },
        where=or_(expired, table.attempts < limit),
    ).returning(table.key)
    accepted = db.execute(statement).scalar_one_or_none()
    if accepted is None:
        expires = db.scalar(select(table.expires_at).where(table.key == key))
        db.commit()
        if expires.tzinfo is None:  # SQLite returns naive UTC datetimes.
            expires = expires.replace(tzinfo=timezone.utc)
        retry = max(1, math.ceil((expires - current).total_seconds()))
        raise HTTPException(
            429, "Слишком много попыток. Подождите и попробуйте снова.",
            headers={"Retry-After": str(retry)},
        )
    db.commit()  # No lock is held while hashing, sending mail, or rendering.


def enforce(db, request, action, *, email="", user_id=None):
    ip = client_address(request)
    if action == "login":
        rules = [
            ("login_ip", ip, "AUTH_LOGIN_IP_LIMIT", 30, 900),
            ("login_account", email.strip().casefold(), "AUTH_LOGIN_ACCOUNT_LIMIT", 10, 900),
        ]
    elif action == "register":
        rules = [("register_ip", ip, "AUTH_REGISTER_IP_LIMIT", 5, 3600)]
    elif action == "resend":
        rules = [
            ("resend_ip", ip, "AUTH_RESEND_IP_LIMIT", 10, 3600),
            ("resend_user", str(user_id), "AUTH_RESEND_USER_LIMIT", 3, 3600),
        ]
    elif action == "password":
        rules = [("password_user", str(user_id), "AUTH_PASSWORD_LIMIT", 10, 900)]
    else:
        raise ValueError("Неизвестное действие авторизации.")
    for scope, identity, setting, default, seconds in rules:
        consume(db, scope=scope, identity=identity,
                limit=get_positive_int_setting(setting, default), seconds=seconds)

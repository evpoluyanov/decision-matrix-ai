"""Server-verifiable choice for optional analytics cookies."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from urllib.parse import urlsplit

from itsdangerous import BadData, URLSafeTimedSerializer


COOKIE_NAME = "dmatrix_cookie_consent"
CONSENT_VERSION = "2026-09-19"
CONSENT_MAX_AGE_SECONDS = 180 * 24 * 60 * 60
ANALYTICS_COOKIE_NAMES = (
    "_ym_d",
    "_ym_isad",
    "_ym_uid",
    "_ym_visorc",
    "_ym_wv2rf",
    "yabs-sid",
    "yandexuid",
    "yuidss",
)


def _serializer() -> URLSafeTimedSerializer:
    secret = os.getenv("SESSION_SECRET")
    if not secret:
        raise RuntimeError("Не задана переменная SESSION_SECRET")
    return URLSafeTimedSerializer(secret, salt="decision-matrix-cookie-consent")


def encode_choice(choice: str) -> str:
    if choice not in {"yes", "no"}:
        raise ValueError("Некорректный выбор настроек cookie.")
    return _serializer().dumps({
        "version": CONSENT_VERSION,
        "analytics": choice == "yes",
        "decided_at": datetime.now(timezone.utc).isoformat(),
    })


def read_choice(request) -> str | None:
    value = request.cookies.get(COOKIE_NAME)
    if not value:
        return None
    try:
        data = _serializer().loads(
            value,
            max_age=CONSENT_MAX_AGE_SECONDS,
        )
    except BadData:
        return None
    if not isinstance(data, dict) or data.get("version") != CONSENT_VERSION:
        return None
    if data.get("analytics") is True:
        return "yes"
    if data.get("analytics") is False:
        return "no"
    return None


def analytics_allowed(request) -> bool:
    return read_choice(request) == "yes"


def _secure_cookie(request) -> bool:
    return (
        request.url.scheme == "https"
        or os.getenv("SESSION_HTTPS_ONLY", "false").lower() == "true"
        or os.getenv("VERCEL") == "1"
    )


def _delete_cookie(response, request, name: str, domain: str | None = None):
    response.delete_cookie(
        name,
        path="/",
        domain=domain,
        secure=_secure_cookie(request),
        httponly=False,
        samesite="lax",
    )


def clear_first_party_analytics_cookies(response, request):
    """Expire known Metrica cookies that are controllable by this site."""
    hostname = (request.url.hostname or "").casefold()
    domains = [None]
    if hostname and hostname not in {"localhost", "testserver"}:
        domains.extend((hostname, f".{hostname.removeprefix('www.')}"))
    for name in ANALYTICS_COOKIE_NAMES:
        for domain in dict.fromkeys(domains):
            _delete_cookie(response, request, name, domain)


def set_choice(response, request, choice: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=encode_choice(choice),
        max_age=CONSENT_MAX_AGE_SECONDS,
        path="/",
        secure=_secure_cookie(request),
        httponly=True,
        samesite="lax",
    )
    if choice == "no":
        clear_first_party_analytics_cookies(response, request)


def safe_return_path(value: str | None) -> str:
    if not value:
        return "/"
    parsed = urlsplit(value)
    if (
        parsed.scheme
        or parsed.netloc
        or not parsed.path.startswith("/")
        or parsed.path.startswith("//")
        or parsed.path == "/cookie-consent"
    ):
        return "/"
    result = parsed.path
    if parsed.query:
        result += f"?{parsed.query}"
    return result[:2000]

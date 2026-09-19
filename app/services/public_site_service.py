import os
from urllib.parse import urlsplit

from app.services import cookie_consent_service


def public_site_url():
    # Separate from APP_BASE_URL: indexing is opt-in after the domain is ready.
    value = os.getenv("PUBLIC_SITE_URL", "").rstrip("/")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.path
            or parsed.query or parsed.fragment or parsed.username or parsed.password):
        return None
    if os.getenv("VERCEL") == "1" and os.getenv("VERCEL_ENV") != "production":
        return None
    return value


def metrika_id():
    value = os.getenv("YANDEX_METRIKA_ID", "")
    if not public_site_url() or not value.isascii() or not value.isdigit() or len(value) > 12:
        return None
    return int(value) or None


def cookie_context(request):
    public = public_site_url()
    matches_host = bool(
        public and request.url.hostname == urlsplit(public).hostname
    )
    counter_id = metrika_id() if matches_host else None
    choice = cookie_consent_service.read_choice(request) if counter_id else None
    query = request.url.query
    return_path = request.url.path + (f"?{query}" if query else "")
    return {
        "cookie_settings_available": counter_id is not None,
        "cookie_consent_required": counter_id is not None and choice is None,
        "cookie_consent_choice": choice,
        "cookie_consent_version": cookie_consent_service.CONSENT_VERSION,
        "cookie_return_path": return_path[:2000],
    }


def page_context(request):
    public = public_site_url()
    # Do not attach analytics to alternate hosts, private pages or logged-in users.
    matches_host = public and request.url.hostname == urlsplit(public).hostname
    cookies = cookie_context(request)
    allowed = cookies["cookie_consent_choice"] == "yes"
    return {
        "canonical_url": public,
        "metrika_counter_id": (
            metrika_id()
            if matches_host and allowed and not request.session.get("user_id")
            else None
        ),
        **cookies,
    }


def product_analytics_context(request):
    public = public_site_url()
    matches_host = public and request.url.hostname == urlsplit(public).hostname
    cookies = cookie_context(request)
    return {
        "product_analytics_counter_id": (
            metrika_id()
            if matches_host and cookies["cookie_consent_choice"] == "yes"
            else None
        ),
        **cookies,
    }

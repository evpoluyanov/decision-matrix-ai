import os
from urllib.parse import urlsplit


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


def page_context(request):
    public = public_site_url()
    # Do not attach analytics to alternate hosts, private pages or logged-in users.
    matches_host = public and request.url.hostname == urlsplit(public).hostname
    return {
        "canonical_url": public,
        "metrika_counter_id": metrika_id() if matches_host and not request.session.get("user_id") else None,
    }

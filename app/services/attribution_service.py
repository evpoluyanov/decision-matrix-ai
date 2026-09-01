"""First-touch attribution stored without URL query strings or personal text."""

from urllib.parse import urlsplit

from app import models


SESSION_KEY = "first_touch_attribution"
UTM_NAMES = ("utm_source", "utm_medium", "utm_campaign", "utm_content")


def _clean(value, limit=200):
    if not isinstance(value, str):
        return None
    value = " ".join(value.strip().split())
    return value[:limit] or None


def _referrer(value, current_host):
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    if parsed.hostname.casefold() == (current_host or "").casefold():
        return None
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{parsed.hostname}{port}{parsed.path}"[:1000]


def capture_first_touch(request):
    if SESSION_KEY in request.session:
        return
    data = {name: _clean(request.query_params.get(name)) for name in UTM_NAMES}
    data["referrer"] = _referrer(request.headers.get("referer", ""), request.url.hostname)
    # An empty record is still a first touch (direct traffic) and prevents a
    # later campaign visit from replacing the original source.
    request.session[SESSION_KEY] = data


def link_to_user(db, request, user):
    if db.query(models.UserAttribution.id).filter_by(user_id=user.id).first():
        return None
    data = request.session.get(SESSION_KEY)
    if not isinstance(data, dict):
        return None
    attribution = models.UserAttribution(
        user_id=user.id,
        **{name: _clean(data.get(name)) for name in UTM_NAMES},
        referrer=_clean(data.get("referrer"), 1000),
    )
    db.add(attribution)
    db.commit()
    db.refresh(attribution)
    return attribution

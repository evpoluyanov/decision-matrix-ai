"""Same-origin browser writes, secure headers and private-response caching.

Unsafe requests require Origin (or a same-origin Referer for older browsers).
Missing/null/foreign origins fail closed, including login and registration.
The public, stateless /calculate API does not use cookies or mutate stored data.
"""

import os
from urllib.parse import urlsplit

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.services.public_site_service import public_site_url
from app.services import attribution_service


def origin_of(value):
    try:
        url = urlsplit(value)
        if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
            return None
        port = url.port or (443 if url.scheme == "https" else 80)
        return url.scheme, url.hostname.lower(), port
    except ValueError:
        return None


class BrowserSecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        unsafe = request.method not in {"GET", "HEAD", "OPTIONS"}
        if unsafe and request.url.path != "/calculate":
            scheme = "https" if os.getenv("VERCEL") == "1" else request.url.scheme
            expected = origin_of(f"{scheme}://{request.headers.get('host', '')}")
            origin = request.headers.get("origin")
            source = origin if origin is not None else request.headers.get("referer", "")
            if (not expected or origin_of(source) != expected
                    or request.headers.get("sec-fetch-site") == "cross-site"):
                response = JSONResponse(status_code=403, content={
                    "status": "csrf_rejected",
                    "message": "Откройте сайт заново и повторите действие с его страницы.",
                })
            else:
                response = await call_next(request)
        else:
            response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        # no-referrer makes native form POSTs send Origin: null, so they fail
        # the CSRF check above. Keep the origin, never URL paths/query tokens.
        response.headers["Referrer-Policy"] = "strict-origin"
        response.headers["Cache-Control"] = "private, no-store"
        if (os.getenv("VERCEL") == "1" and os.getenv("VERCEL_ENV") != "production") or (
            request.url.path == "/" and not public_site_url()
        ):
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        elif request.url.path not in {
            "/", "/pricing", "/privacy", "/terms",
            "/robots.txt", "/sitemap.xml", "/static/og-decision-matrix.png",
        }:
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response


class FirstTouchAttributionMiddleware(BaseHTTPMiddleware):
    """Capture only sanitised first-touch campaign fields in the signed session."""

    async def dispatch(self, request, call_next):
        if request.method in {"GET", "HEAD"}:
            attribution_service.capture_first_touch(request)
        return await call_next(request)

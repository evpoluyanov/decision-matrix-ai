"""Same-origin browser writes, secure headers and private-response caching.

Unsafe requests require Origin (or a same-origin Referer for older browsers).
Missing/null/foreign origins fail closed, including login and registration.
The public, stateless /calculate API does not use cookies or mutate stored data.
"""

import os
from urllib.parse import urlsplit

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, RedirectResponse
from app.services.public_site_service import INDEXABLE_PUBLIC_PATHS, public_site_url
from app.services import attribution_service, cookie_consent_service, public_site_service


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
        public = public_site_url()
        public_url = urlsplit(public) if public else None
        request_host = request.url.hostname.casefold() if request.url.hostname else None
        canonical_host = public_url.hostname.casefold() if public_url and public_url.hostname else None
        if (
            request.method in {"GET", "HEAD"}
            and canonical_host
            and request_host == f"www.{canonical_host}"
        ):
            target = f"{public.rstrip('/')}{request.url.path}"
            if request.url.query:
                target = f"{target}?{request.url.query}"
            response = RedirectResponse(target, status_code=308)
        else:
            response = None

        unsafe = request.method not in {"GET", "HEAD", "OPTIONS"}
        if response is not None:
            pass
        elif unsafe and request.url.path != "/calculate":
            https_only = (
                os.getenv("VERCEL") == "1"
                or os.getenv("SESSION_HTTPS_ONLY", "false").lower() == "true"
            )
            scheme = "https" if https_only else request.url.scheme
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
        public_assets = {
            "/favicon.svg", "/favicon-120.png", "/favicon.ico", "/apple-touch-icon.png",
            "/static/operations.css", "/static/operations.js",
            "/robots.txt", "/sitemap.xml", "/static/og-decision-matrix.png",
        }
        is_nonproduction = (
            os.getenv("VERCEL") == "1" and os.getenv("VERCEL_ENV") != "production"
        )
        if is_nonproduction or (
            request.url.path in INDEXABLE_PUBLIC_PATHS and not public
        ):
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        elif request.url.path not in INDEXABLE_PUBLIC_PATHS | public_assets:
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response


class FirstTouchAttributionMiddleware(BaseHTTPMiddleware):
    """Capture only sanitised first-touch campaign fields in the signed session."""

    async def dispatch(self, request, call_next):
        if (
            request.method == "GET"
            and request.url.path in public_site_service.ATTRIBUTION_PATHS
            and cookie_consent_service.analytics_allowed(request)
        ):
            attribution_service.capture_first_touch(request)
        return await call_next(request)

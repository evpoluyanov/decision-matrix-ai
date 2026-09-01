from xml.sax.saxutils import escape

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

from app.services.public_site_service import public_site_url

router = APIRouter()


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    site = public_site_url()
    if not site:
        return "User-agent: *\nDisallow: /\n"
    return (
        "User-agent: *\nDisallow: /\n"
        "Allow: /$\nAllow: /pricing$\nAllow: /privacy$\nAllow: /terms$\n"
        f"Sitemap: {site}/sitemap.xml\n"
    )


@router.get("/sitemap.xml")
def sitemap():
    site = public_site_url()
    entries = ""
    if site:
        entries = "".join(
            f"<url><loc>{escape(site)}{path}</loc></url>"
            for path in ("/", "/pricing", "/privacy", "/terms")
        )
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'{entries}</urlset>', media_type="application/xml",
    )

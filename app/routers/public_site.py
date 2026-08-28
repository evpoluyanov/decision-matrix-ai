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
    return f"User-agent: *\nDisallow: /\nAllow: /$\nSitemap: {site}/sitemap.xml\n"


@router.get("/sitemap.xml")
def sitemap():
    site = public_site_url()
    entry = f"<url><loc>{escape(site)}/</loc></url>" if site else ""
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'{entry}</urlset>', media_type="application/xml",
    )

from xml.sax.saxutils import escape
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, PlainTextResponse, Response

from app.services.public_site_service import public_site_url

router = APIRouter()

ICON_FILES = {"favicon.svg": "image/svg+xml", "favicon-120.png": "image/png",
              "favicon.ico": "image/vnd.microsoft.icon", "apple-touch-icon.png": "image/png"}


def icon_response(name):
    return FileResponse(Path(__file__).resolve().parents[1] / "static" / name, media_type=ICON_FILES[name])


@router.api_route("/favicon.svg", methods=["GET", "HEAD"])
def favicon_svg():
    return icon_response("favicon.svg")


@router.api_route("/favicon-120.png", methods=["GET", "HEAD"])
def favicon_png():
    return icon_response("favicon-120.png")


@router.api_route("/favicon.ico", methods=["GET", "HEAD"])
def favicon_ico():
    return icon_response("favicon.ico")


@router.api_route("/apple-touch-icon.png", methods=["GET", "HEAD"])
def apple_icon():
    return icon_response("apple-touch-icon.png")


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    site = public_site_url()
    if not site:
        return "User-agent: *\nDisallow: /\n"
    return (
        "User-agent: *\nDisallow: /\n"
        "Allow: /$\nAllow: /pricing$\n"
        "Allow: /favicon.svg$\nAllow: /favicon-120.png$\nAllow: /favicon.ico$\n"
        "Allow: /apple-touch-icon.png$\nAllow: /static/\n"
        f"Sitemap: {site}/sitemap.xml\n"
    )


@router.get("/sitemap.xml")
def sitemap():
    site = public_site_url()
    entries = ""
    if site:
        entries = "".join(
            f"<url><loc>{escape(site)}{path}</loc></url>"
            for path in ("/", "/pricing")
        )
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'{entries}</urlset>', media_type="application/xml",
    )

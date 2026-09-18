from xml.sax.saxutils import escape
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.legal_documents import LEGAL_DOCUMENTS
from app.legal_documents import LEGAL_DOCUMENT_DATE
from app.services import legal_document_service
from app.services.public_site_service import public_site_url

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

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


def legal_page(request, db, document_key, legacy_template_name):
    version = legal_document_service.current_version(db, document_key)
    if version is None:
        return templates.TemplateResponse(
            request=request,
            name=legacy_template_name,
            context={
                "canonical_url": public_site_url(),
                "document_date": LEGAL_DOCUMENT_DATE,
            },
        )
    definition = LEGAL_DOCUMENTS[document_key]
    return templates.TemplateResponse(
        request=request,
        name="legal_document.html",
        context={
            "canonical_url": public_site_url(),
            "definition": definition,
            "document": version,
            "rendered_content": legal_document_service.render_markdown(version.content),
            "historical": False,
        },
    )


@router.get("/privacy")
def privacy(request: Request, db: Session = Depends(get_db)):
    return legal_page(request, db, "privacy", "privacy.html")


@router.get("/terms")
def terms(request: Request, db: Session = Depends(get_db)):
    return legal_page(request, db, "terms", "terms.html")


@router.get("/consent")
def consent(request: Request, db: Session = Depends(get_db)):
    return legal_page(request, db, "consent", "consent.html")


@router.get("/legal/{document_key}/{version}")
def legal_version(
    document_key: str,
    version: str,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        definition = LEGAL_DOCUMENTS[document_key]
    except KeyError as exc:
        raise HTTPException(404, "Документ не найден.") from exc
    document = legal_document_service.version_by_name(db, document_key, version)
    if document is None:
        raise HTTPException(404, "Версия документа не найдена.")
    return templates.TemplateResponse(
        request=request,
        name="legal_document.html",
        context={
            "canonical_url": None,
            "definition": definition,
            "document": document,
            "rendered_content": legal_document_service.render_markdown(document.content),
            "historical": document.status == "archived",
        },
    )


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

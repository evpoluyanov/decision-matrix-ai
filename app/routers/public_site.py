from xml.sax.saxutils import escape
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import (
    FileResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.legal_documents import (
    LEGAL_DOCUMENTS,
    LEGAL_DOCUMENT_DATE,
    LEGAL_DOCUMENT_VERSION,
    default_legal_document_content,
)
from app.services import (
    attribution_service,
    cookie_consent_service,
    legal_document_service,
    public_site_service,
)
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


def legal_page(request, db, document_key):
    version = legal_document_service.current_version(db, document_key)
    definition = LEGAL_DOCUMENTS[document_key]
    if version is None:
        return templates.TemplateResponse(
            request=request,
            name="legal_document_fallback.html",
            context={
                "canonical_url": public_site_url(),
                "document_date": LEGAL_DOCUMENT_DATE,
                "document_version": LEGAL_DOCUMENT_VERSION,
                "definition": definition,
                "rendered_content": legal_document_service.render_markdown(
                    default_legal_document_content(document_key)
                ),
                **public_site_service.cookie_context(request),
            },
        )
    return templates.TemplateResponse(
        request=request,
        name="legal_document.html",
        context={
            "canonical_url": public_site_url(),
            "definition": definition,
            "document": version,
            "rendered_content": legal_document_service.render_markdown(version.content),
            "historical": False,
            **public_site_service.cookie_context(request),
        },
    )


@router.get("/privacy")
def privacy(request: Request, db: Session = Depends(get_db)):
    return legal_page(request, db, "privacy")


@router.get("/terms")
def terms(request: Request, db: Session = Depends(get_db)):
    return legal_page(request, db, "terms")


@router.get("/consent")
def consent(request: Request, db: Session = Depends(get_db)):
    return legal_page(request, db, "consent")


@router.get("/cookies")
def cookies_policy(request: Request):
    context = public_site_service.cookie_context(request)
    # The page itself contains the complete settings form; do not duplicate
    # the compact banner there.
    context["cookie_consent_required"] = False
    return templates.TemplateResponse(
        request=request,
        name="cookies.html",
        context={
            "canonical_url": public_site_url(),
            "document_date": LEGAL_DOCUMENT_DATE,
            **context,
        },
    )


def seo_page(request: Request, template_name: str, page_key: str):
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "seo_page_key": page_key,
            **public_site_service.page_context(request),
        },
    )


@router.api_route(
    "/vybor-postavshchika",
    methods=["GET", "HEAD"],
)
def supplier_selection(request: Request):
    return seo_page(request, "seo_supplier_selection.html", "supplier")


@router.api_route(
    "/vybor-podryadchika",
    methods=["GET", "HEAD"],
)
def contractor_selection(request: Request):
    return seo_page(request, "seo_contractor_selection.html", "contractor")


@router.api_route(
    "/vzveshennaya-matritsa-resheniy",
    methods=["GET", "HEAD"],
)
def weighted_decision_matrix(request: Request):
    return seo_page(request, "seo_weighted_matrix.html", "weighted")


@router.post("/cookie-consent")
def set_cookie_consent(
    request: Request,
    analytics: str = Form(...),
    next_path: str | None = Form(None),
    db: Session = Depends(get_db),
):
    if analytics not in {"yes", "no"}:
        raise HTTPException(400, "Выберите, разрешать ли аналитические cookie.")
    if analytics == "no":
        request.session.pop(attribution_service.SESSION_KEY, None)
        visitor_id = request.session.pop("product_visitor_id", None)
        if isinstance(visitor_id, str):
            db.query(models.ProductEvent).filter_by(
                dedupe_key=f"pricing_viewed:visitor:{visitor_id}"
            ).delete(synchronize_session=False)
        user_id = request.session.get("user_id")
        if isinstance(user_id, int):
            db.query(models.UserAttribution).filter_by(user_id=user_id).delete(
                synchronize_session=False
            )
        db.commit()
    response = RedirectResponse(
        cookie_consent_service.safe_return_path(next_path),
        status_code=303,
    )
    cookie_consent_service.set_choice(response, request, analytics)
    return response


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
            **public_site_service.cookie_context(request),
        },
    )


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    site = public_site_url()
    if not site:
        return "User-agent: *\nDisallow: /\n"
    allowed_pages = "".join(
        f"Allow: {path}$\n" for path, _title in public_site_service.INDEXABLE_PUBLIC_PAGES
        if path != "/"
    )
    return (
        "User-agent: *\nDisallow: /\n"
        f"Allow: /$\n{allowed_pages}"
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
            for path, _title in public_site_service.INDEXABLE_PUBLIC_PAGES
        )
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'{entries}</urlset>', media_type="application/xml",
    )

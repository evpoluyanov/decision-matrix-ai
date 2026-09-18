from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.auth_dependencies import require_authenticated_user
from app.database import get_db
from app.legal_documents import LEGAL_DOCUMENTS
from app.services import legal_document_service


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _document_views(versions):
    return [
        {
            "version": version,
            "definition": LEGAL_DOCUMENTS[version.document_key],
            "rendered_content": legal_document_service.render_markdown(
                version.content
            ),
        }
        for version in versions
    ]


@router.get("/legal/updates", response_class=HTMLResponse)
def legal_updates(
    request: Request,
    next: str | None = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_authenticated_user),
):
    target = legal_document_service.safe_next_path(next)
    pending = legal_document_service.pending_versions(db, user.id)
    if not pending:
        return RedirectResponse(target, status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="legal_updates.html",
        context={
            "documents": _document_views(pending),
            "next_path": target,
            "error": None,
        },
        headers={"Cache-Control": "private, no-store"},
    )


@router.post("/legal/updates", response_class=HTMLResponse)
def confirm_legal_updates(
    request: Request,
    document_version_ids: list[int] = Form([]),
    next: str | None = Form(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_authenticated_user),
):
    target = legal_document_service.safe_next_path(next)
    try:
        legal_document_service.record_acceptances(
            db,
            user_id=user.id,
            version_ids=document_version_ids,
        )
    except legal_document_service.ConfirmationsChangedError as exc:
        pending = legal_document_service.pending_versions(db, user.id)
        return templates.TemplateResponse(
            request=request,
            name="legal_updates.html",
            context={
                "documents": _document_views(pending),
                "next_path": target,
                "error": str(exc),
            },
            status_code=409,
            headers={"Cache-Control": "private, no-store"},
        )
    return RedirectResponse(target, status_code=303)

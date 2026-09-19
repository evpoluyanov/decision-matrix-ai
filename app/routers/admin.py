from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.legal_documents import (
    LEGAL_DOCUMENTS,
    default_legal_document_content,
    legal_document_definition,
)
from app.services import (
    admin_service,
    feedback_service,
    legal_document_service,
    mws_reconciliation_service,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def legal_editor_response(request, db, document_key, *, error=None, status_code=200):
    try:
        definition = legal_document_definition(document_key)
    except ValueError as exc:
        raise HTTPException(404, "Документ не найден.") from exc
    draft = legal_document_service.latest_draft(db, document_key)
    return templates.TemplateResponse(
        request=request,
        name="admin_legal_document_edit.html",
        context={
            "definition": definition,
            "current": legal_document_service.current_version(db, document_key),
            "draft": draft,
            "history": legal_document_service.version_history(db, document_key),
            "suggested_version": (
                draft.version if draft else legal_document_service.suggest_version(
                    db, document_key,
                )
            ),
            "suggested_content": (
                draft.content
                if draft
                else default_legal_document_content(document_key)
            ),
            "error": error,
        },
        status_code=status_code,
        headers={"Cache-Control": "private, no-store", "X-Robots-Tag": "noindex, nofollow"},
    )


@router.get("/admin")
def dashboard(request: Request, days: str = "1", category: str | None = None,
              status: str | None = None,
              db: Session = Depends(get_db), user=Depends(admin_service.require_admin)):
    if days not in {"1", "7", "30", "all"}:
        raise HTTPException(422, "Некорректный период.")
    if category and category not in feedback_service.CATEGORIES:
        raise HTTPException(422, "Некорректная категория.")
    if status and status not in feedback_service.STATUSES:
        raise HTTPException(422, "Некорректный статус.")
    return templates.TemplateResponse(
        request=request, name="admin.html",
        context={"stats": admin_service.statistics(
            db, days, feedback_category=category, feedback_status=status,
        )},
        headers={"Cache-Control": "private, no-store", "X-Robots-Tag": "noindex, nofollow"},
    )


@router.post("/admin/feedback/{feedback_id}")
def update_feedback(feedback_id: int, status: str = Form(...), admin_note: str = Form(""),
                    db: Session = Depends(get_db), user=Depends(admin_service.require_admin)):
    feedback_service.update_status(
        db, feedback_id=feedback_id, status=status, admin_note=admin_note,
    )
    return RedirectResponse("/admin", status_code=303)


@router.post("/admin/mws-reconciliation")
def add_reconciliation(
    period_start: str = Form(...), period_end: str = Form(...),
    input_tokens: int = Form(...), output_tokens: int = Form(...),
    actual_base_cost_rub: str = Form(...), discount_or_grant_rub: str = Form(...),
    amount_due_rub: str = Form(...), application_estimated_cost_rub: str = Form(...),
    source: str = Form(...), db: Session = Depends(get_db),
    user=Depends(admin_service.require_admin),
):
    try:
        start = datetime.fromisoformat(period_start)
        end = datetime.fromisoformat(period_end)
    except ValueError as exc:
        raise HTTPException(400, "Некорректный период сверки.") from exc
    mws_reconciliation_service.add_manual(
        db, period_start=start, period_end=end, input_tokens=input_tokens,
        output_tokens=output_tokens, actual_base_cost_rub=actual_base_cost_rub,
        discount_or_grant_rub=discount_or_grant_rub, amount_due_rub=amount_due_rub,
        application_estimated_cost_rub=application_estimated_cost_rub, source=source,
    )
    return RedirectResponse("/admin", status_code=303)


@router.get("/admin/legal-documents", response_class=HTMLResponse)
def legal_documents_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(admin_service.require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="admin_legal_documents.html",
        context={
            "documents": legal_document_service.dashboard_documents(db),
            "definitions": LEGAL_DOCUMENTS,
        },
        headers={"Cache-Control": "private, no-store", "X-Robots-Tag": "noindex, nofollow"},
    )


@router.get("/admin/legal-documents/{document_key}", response_class=HTMLResponse)
def edit_legal_document(
    document_key: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(admin_service.require_admin),
):
    return legal_editor_response(request, db, document_key)


@router.post("/admin/legal-documents/{document_key}/draft")
def save_legal_document_draft(
    document_key: str,
    request: Request,
    version: str = Form(..., max_length=32),
    change_summary: str = Form("", max_length=500),
    content: str = Form(..., max_length=legal_document_service.MAX_DOCUMENT_LENGTH),
    db: Session = Depends(get_db),
    user=Depends(admin_service.require_admin),
):
    try:
        legal_document_service.save_draft(
            db,
            document_key=document_key,
            version=version,
            content=content,
            change_summary=change_summary,
            admin_user_id=user.id,
        )
    except (ValueError, legal_document_service.LegalDocumentError) as exc:
        return legal_editor_response(
            request, db, document_key, error=str(exc), status_code=400,
        )
    return RedirectResponse(
        f"/admin/legal-documents/{document_key}", status_code=303,
    )


@router.get("/admin/legal-documents/{document_key}/preview", response_class=HTMLResponse)
def preview_legal_document(
    document_key: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(admin_service.require_admin),
):
    try:
        definition = legal_document_definition(document_key)
    except ValueError as exc:
        raise HTTPException(404, "Документ не найден.") from exc
    draft = legal_document_service.latest_draft(db, document_key)
    if draft is None:
        raise HTTPException(404, "Сначала сохраните черновик.")
    return templates.TemplateResponse(
        request=request,
        name="admin_legal_preview.html",
        context={
            "definition": definition,
            "draft": draft,
            "rendered_content": legal_document_service.render_markdown(draft.content),
        },
        headers={"Cache-Control": "private, no-store", "X-Robots-Tag": "noindex, nofollow"},
    )


@router.post("/admin/legal-documents/{document_key}/publish")
def publish_legal_document(
    document_key: str,
    request: Request,
    draft_id: int = Form(...),
    publish_confirm: str | None = Form(None),
    db: Session = Depends(get_db),
    user=Depends(admin_service.require_admin),
):
    if publish_confirm != "yes":
        return legal_editor_response(
            request,
            db,
            document_key,
            error="Подтвердите публикацию новой версии.",
            status_code=400,
        )
    try:
        legal_document_service.publish_draft(
            db,
            document_key=document_key,
            draft_id=draft_id,
            admin_user_id=user.id,
        )
    except (ValueError, legal_document_service.LegalDocumentError) as exc:
        return legal_editor_response(
            request, db, document_key, error=str(exc), status_code=400,
        )
    return RedirectResponse("/admin/legal-documents", status_code=303)

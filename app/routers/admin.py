from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import admin_service, feedback_service, mws_reconciliation_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


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

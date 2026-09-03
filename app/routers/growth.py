import secrets

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.auth_dependencies import require_user
from app.database import get_db
from app.services import feedback_service, growth_service, public_site_service


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def optional_user(request, db):
    user_id = request.session.get("user_id")
    return db.get(models.User, user_id) if isinstance(user_id, int) else None


def analytics_context(request):
    return public_site_service.product_analytics_context(request)


@router.get("/pricing", response_class=HTMLResponse)
def pricing(request: Request, db: Session = Depends(get_db), saved: int = 0):
    user = optional_user(request, db)
    visitor = request.session.get("product_visitor_id")
    if not isinstance(visitor, str):
        visitor = secrets.token_urlsafe(12)
        request.session["product_visitor_id"] = visitor
    identity = f"user:{user.id}" if user else f"visitor:{visitor}"
    growth_service.record_event(
        db, "pricing_viewed", user=user,
        dedupe_key=f"pricing_viewed:{identity}",
    )
    if user:
        growth_service.record_event(db, "paid_offer_viewed", user=user, metadata={"source": "pricing"},
            dedupe_key=f"paid_offer_viewed:user:{user.id}:source:pricing:project:0")
    return templates.TemplateResponse(
        request=request, name="pricing.html",
        context={
            "user": user,
            "preference": growth_service.preference_for(db, user.id) if user else None,
            "saved": bool(saved),
            "canonical_url": public_site_service.public_site_url(),
            **analytics_context(request),
        },
    )


@router.post("/monetization/preference")
def save_preference(
    request: Request,
    selected_plan: str = Form(...),
    source: str = Form(...),
    return_to: str = Form("/pricing"),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_user),
):
    preference = growth_service.save_preference(
        db, user=user, selected_plan=selected_plan, source=source,
    )
    if request.headers.get("x-requested-with") == "fetch":
        return JSONResponse({
            "status": "ok", "selected_plan": preference.selected_plan,
            "notify_on_launch": preference.notify_on_launch,
        })
    if not return_to.startswith("/") or "://" in return_to:
        return_to = "/pricing"
    separator = "&" if "?" in return_to else "?"
    return RedirectResponse(f"{return_to}{separator}saved=1", status_code=303)


@router.post("/product-events/paid-offer-viewed")
def paid_offer_viewed(
    source: str = Form(...),
    project_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_user),
):
    if source not in growth_service.SOURCES:
        return JSONResponse({"status": "invalid_source"}, status_code=400)
    growth_service.record_event(
        db, "paid_offer_viewed", user=user, project_id=project_id,
        metadata={"source": source},
        dedupe_key=f"paid_offer_viewed:user:{user.id}:source:{source}:project:{project_id or 0}",
    )
    return {"status": "ok"}


@router.get("/feedback", response_class=HTMLResponse)
def feedback_form(
    request: Request,
    project_id: int | None = None,
    submitted: int = 0,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_user),
):
    if project_id is not None and db.query(models.Project.id).filter_by(
        id=project_id, owner_id=user.id,
    ).first() is None:
        project_id = None
    referer = request.headers.get("referer", "")
    page_path = "/feedback"
    if referer.startswith(str(request.base_url)):
        page_path = "/" + referer[len(str(request.base_url)):].split("?", 1)[0].lstrip("/")
    return templates.TemplateResponse(
        request=request, name="feedback.html",
        context={
            "user": user, "project_id": project_id, "page_path": page_path,
            "submitted": bool(submitted),
            **analytics_context(request),
        },
    )


@router.post("/feedback")
def submit_feedback(
    request: Request,
    category: str = Form(...),
    message: str = Form(""),
    quick: bool = Form(False),
    rating: int | None = Form(None),
    page_path: str = Form("/feedback"),
    project_id: int | None = Form(None),
    allow_email_reply: bool = Form(False),
    return_to: str = Form("/feedback"),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_user),
):
    submission = feedback_service.submit(
        db, request, user=user, category=category, rating=rating,
        message=message, page_path=page_path, project_id=project_id,
        allow_email_reply=allow_email_reply,
        report_question=quick,
    )
    if request.headers.get("x-requested-with") == "fetch":
        return {"status": "ok", "feedback_id": submission.feedback.id, "created": submission.created}
    if quick:
        return_to = f"/projects/{project_id}/report"
    if not return_to.startswith("/") or "://" in return_to:
        return_to = "/feedback"
    separator = "&" if "?" in return_to else "?"
    if not submission.created:
        return RedirectResponse(return_to, status_code=303)
    return RedirectResponse(
        f"{return_to}{separator}feedback_submitted=1"
        f"&feedback_category={category}&feedback_has_rating={int(rating is not None)}",
        status_code=303,
    )


@router.get("/feedback/report-question/state")
def report_question_state(db: Session = Depends(get_db), user: models.User = Depends(require_user)):
    return {"answered": feedback_service.has_report_answer(db, user.id)}

import json
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.auth_dependencies import require_user
from app.services import decision_service as service, public_site_service, user_service, admin_service
from app.services import cookie_consent_service, growth_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def context(request, db):
    uid = request.session.get("user_id")
    user = db.get(models.User, uid) if isinstance(uid, int) else None
    return {"user": user, "is_admin": bool(user and admin_service.is_admin(user)),
            **public_site_service.page_context(request), **public_site_service.product_analytics_context(request),
            "journey_analytics": cookie_consent_service.analytics_allowed(request)}


@router.api_route("/", methods=["GET", "HEAD"])
@router.get("/start")
def landing(request: Request, db: Session = Depends(get_db)):
    service.cleanup(db)
    service.guest_token(request)
    cohort = service.journey(db, request, fresh=bool(request.session.pop("decision_submitted", False)))
    if cohort:
        service.event(db, cohort.id, "landing_viewed")
    return templates.TemplateResponse(request=request, name="decision_landing.html", context=context(request, db))


@router.post("/start")
def create(request: Request, background: BackgroundTasks,
           decision_question: str = Form(..., min_length=1, max_length=200),
           decision_details: str = Form("", max_length=5000),
           allow_suggestions: str = Form("no"), db: Session = Depends(get_db)):
    if not decision_question.strip():
        raise HTTPException(422, "Опишите, что хотите выбрать.")
    # Identical double submission reuses the same durable operation.
    previous = request.session.get("last_decision")
    brief = db.get(models.DecisionBrief, previous) if isinstance(previous, str) else None
    if brief and brief.question == decision_question.strip() and brief.details == decision_details.strip() \
            and brief.allow_suggestions == (allow_suggestions == "yes") and brief.state in {"preparing", "understanding"}:
        return {"url": "/decisions/" + brief.id}
    cohort = service.journey(db, request)
    brief = models.DecisionBrief(id=__import__('secrets').token_hex(16),
        access_digest=service.digest(service.guest_token(request)), question=decision_question.strip(),
        details=decision_details.strip(), allow_suggestions=allow_suggestions == "yes", state="draft", revision=0,
        journey_id=cohort.id if cohort else None, created_at=service.now(), updated_at=service.now(),
        expires_at=service.now()+timedelta(days=7))
    db.add(brief)
    db.commit()
    request.session["last_decision"] = brief.id
    request.session["decision_submitted"] = True
    service.track(db, request, brief, "task_submitted")
    log_id, key = service.begin(db, request, brief, "preparing")
    background.add_task(service.worker, db.get_bind(), brief.id, log_id, key, "preparing")
    return {"url": "/decisions/" + brief.id}


@router.get("/decisions/active")
def active(request: Request, db: Session = Depends(get_db)):
    bid = request.session.get("last_decision")
    if not isinstance(bid, str):
        return {"url": None}
    try:
        brief = service.access(db, request, bid)
    except HTTPException:
        return {"url": None}
    return {"url": "/decisions/" + brief.id, "question": brief.question,
            "details": brief.details, "allow_suggestions": brief.allow_suggestions}


@router.get("/decisions/mine")
def mine(request: Request, db: Session = Depends(get_db), user=Depends(require_user)):
    return templates.TemplateResponse(request=request, name="decision_mine.html", context={
        "briefs": db.scalars(select(models.DecisionBrief).where(models.DecisionBrief.owner_id == user.id)
                            .order_by(models.DecisionBrief.created_at.desc())).all(),
        **context(request, db)})


@router.get("/decisions/{bid}")
def page(bid: str, request: Request, db: Session = Depends(get_db)):
    brief = service.access(db, request, bid)
    return templates.TemplateResponse(request=request, name="decision_workspace.html", context={
        "brief": brief, **context(request, db)})


@router.get("/decisions/{bid}/status")
def status(bid: str, request: Request, db: Session = Depends(get_db)):
    brief = service.access(db, request, bid)
    return {"state": brief.state, "revision": brief.revision, "question": brief.question, "details": brief.details,
        "allow_suggestions": brief.allow_suggestions, "saved": brief.owner_id is not None,
        "understanding": json.loads(brief.understanding_json) if brief.understanding_json else None,
        "result": json.loads(brief.result_json) if brief.result_json else None,
        "error_code": brief.error_code}


@router.post("/decisions/{bid}/compare")
async def compare(bid: str, request: Request, background: BackgroundTasks, db: Session = Depends(get_db)):
    brief = service.access(db, request, bid)
    if brief.state in {"preparing", "comparing", "unknown"}:
        raise HTTPException(409, "Предыдущая операция ещё не завершена.")
    data = await request.json()
    try:
        understanding = service.Understanding.model_validate(data).model_dump()
        answers = data.get("answers", [])
        if not isinstance(answers, list) or not all(isinstance(v, str) for v in answers):
            raise ValueError()
        understanding["answers"] = answers
        question = str(data.get("question", brief.question)).strip()
        details = str(data.get("details", brief.details)).strip()
        if not question or len(question) > 200 or len(details) > 5000:
            raise ValueError()
        if len(json.dumps(understanding, ensure_ascii=False)) + len(details) > 26000:
            raise HTTPException(413, "Объём данных слишком большой для одного разбора. Сократите текст, сохранив существенные условия.")
        understanding["options"] = list(dict.fromkeys(v.strip() for v in understanding["options"] if v.strip()))
        if not understanding["options"]:
            raise HTTPException(422, "Добавьте хотя бы один вариант для сравнения.")
        # Names define comparison columns: merge duplicate conditions deterministically.
        merged = {}
        for c in understanding["conditions"]:
            name = c["name"].strip()
            if name:
                merged[name] = {"name": name, "required": c["required"] or merged.get(name, {}).get("required", False)}
        understanding["conditions"] = list(merged.values())
        if not merged:
            raise HTTPException(422, "Добавьте хотя бы одно условие или предпочтение.")
    except (ValueError, TypeError):
        raise HTTPException(422, "Проверьте варианты и условия.")
    if data.get("revision") != brief.revision:
        raise HTTPException(409, "Разбор изменён в другой вкладке. Обновите страницу перед сохранением.")
    log_id, key = service.begin(db, request, brief, "comparing", changes={
        "understanding_json": json.dumps(understanding, ensure_ascii=False),
        "question": question, "details": details, "allow_suggestions": data.get("allow_suggestions") is True})
    service.track(db, request, brief, "comparison_requested")
    background.add_task(service.worker, db.get_bind(), brief.id, log_id, key, "comparing")
    return {"state": "comparing"}


@router.post("/decisions/{bid}/prepare")
async def retry_prepare(bid: str, request: Request, background: BackgroundTasks, db: Session = Depends(get_db)):
    brief = service.access(db, request, bid)
    data = await request.json()
    changes = {}
    if data:
        if data.get("revision") != brief.revision:
            raise HTTPException(409, "Разбор изменён в другой вкладке.")
        question, details = str(data.get("question", "")).strip(), str(data.get("details", "")).strip()
        if not question or len(question) > 200 or len(details) > 5000:
            raise HTTPException(422, "Проверьте вопрос и условия.")
        if brief.state in {"preparing", "comparing", "unknown"}:
            raise HTTPException(409, "Предыдущая операция ещё не завершена.")
        changes = {"question": question, "details": details, "allow_suggestions": data.get("allow_suggestions") is True}
    log_id, key = service.begin(db, request, brief, "preparing", changes=changes)
    background.add_task(service.worker, db.get_bind(), bid, log_id, key, "preparing")
    return {"state": "preparing"}


@router.post("/decisions/{bid}/save")
def save(bid: str, request: Request, db: Session = Depends(get_db)):
    brief = service.access(db, request, bid)
    if not brief.result_json:
        raise HTTPException(409, "Сначала получите результат.")
    service.track(db, request, brief, "save_requested")
    request.session["save_decision_id"] = bid
    uid = request.session.get("user_id")
    user = db.get(models.User, uid) if isinstance(uid, int) else None
    if user:
        service.attach_pending(db, request, user)
        destination = service.claim(db, request, user)
        return RedirectResponse(destination or "/account", status_code=303)
    return RedirectResponse("/login?from=save", status_code=303)


@router.post("/decisions/events")
async def record_event(request: Request, db: Session = Depends(get_db)):
    if not cookie_consent_service.analytics_allowed(request):
        return {"recorded": False}
    data = await request.json()
    name = data.get("event")
    # Server truth (generated, saved, authenticated) cannot be forged by browser events.
    if name not in {"landing_viewed", "input_started", "example_selected", "understanding_viewed",
                    "result_viewed", "conditions_changed", "details_opened"}:
        raise HTTPException(422, "Неизвестное событие.")
    bid = data.get("brief")
    if bid:
        brief = service.access(db, request, str(bid))
        if name == "result_viewed" and not brief.result_json:
            raise HTTPException(409, "Результат ещё не готов.")
        if name == "understanding_viewed" and not brief.understanding_json:
            raise HTTPException(409, "Разбор ещё не готов.")
        service.track(db, request, brief, name)
    else:
        cohort = service.journey(db, request)
        service.event(db, cohort.id if cohort else None, name)
    return {"recorded": True}


@router.api_route("/pricing", methods=["GET", "HEAD"])
def pricing():
    return RedirectResponse("/", status_code=303)

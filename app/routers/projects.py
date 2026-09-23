from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.auth_dependencies import require_user
from app.database import get_db
from app.services import growth_service, project_service
from app.services import public_site_service
from app.services import legal_document_service
from app.llm.safety import (
    MAX_PROJECT_DESCRIPTION_LENGTH,
    MAX_PROJECT_NAME_LENGTH,
)

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

DECISION_TEMPLATES = (
    {
        "key": "contractor",
        "title": "Подрядчик или поставщик",
        "example": "Какого подрядчика выбрать для разработки сайта?",
        "hint": "Цена, сроки, опыт, качество и риски.",
    },
    {
        "key": "software",
        "title": "Программа или сервис",
        "example": "Какую CRM выбрать для отдела продаж?",
        "hint": "Функции, стоимость, внедрение и поддержка.",
    },
    {
        "key": "equipment",
        "title": "Оборудование",
        "example": "Какое оборудование выбрать для офиса?",
        "hint": "Цена, надёжность, обслуживание и срок службы.",
    },
    {
        "key": "management",
        "title": "Управленческое решение",
        "example": "Какой вариант запуска нового направления выбрать?",
        "hint": "Эффект, ресурсы, сроки и возможные риски.",
    },
    {
        "key": "custom",
        "title": "Свой вариант",
        "example": "Что вы хотите выбрать?",
        "hint": "Опишите задачу своими словами.",
    },
)
DECISION_TEMPLATE_KEYS = {item["key"] for item in DECISION_TEMPLATES}
START_DETAILS_MAX_LENGTH = 1800


def _project_redirect(project_id: int, second_project: bool = False) -> str:
    query = "created=1"
    if second_project:
        query += "&second_project_event=1"
    return f"/projects/{project_id}?{query}"


@router.api_route(
    "/",
    methods=["GET", "HEAD"],
    response_class=HTMLResponse,
)
def index(
    request: Request,
    db: Session = Depends(get_db),
):
    user = None

    user_id = request.session.get(
        "user_id"
    )

    if isinstance(user_id, int):
        user = db.get(
            models.User,
            user_id,
        )

    if user is not None:
        return RedirectResponse(url="/start", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": user,
            **public_site_service.page_context(request),
        },
    )


@router.get(
    "/start",
    response_class=HTMLResponse,
)
def start_decision(
    request: Request,
    db: Session = Depends(get_db),
):
    user = None
    user_id = request.session.get("user_id")
    if isinstance(user_id, int):
        user = db.get(models.User, user_id)

    draft = request.session.get("decision_draft")
    if not isinstance(draft, dict):
        draft = {}

    return templates.TemplateResponse(
        request=request,
        name="start_decision.html",
        context={
            "user": user,
            "decision_templates": DECISION_TEMPLATES,
            "draft": draft,
            **public_site_service.page_context(request),
        },
    )


@router.post(
    "/start",
    response_class=HTMLResponse,
)
def submit_start_decision(
    request: Request,
    decision_question: str = Form(
        ...,
        min_length=1,
        max_length=MAX_PROJECT_NAME_LENGTH,
    ),
    decision_details: str | None = Form(
        None,
        max_length=START_DETAILS_MAX_LENGTH,
    ),
    template_key: str = Form("custom"),
    db: Session = Depends(get_db),
):
    normalized_question = decision_question.strip()
    normalized_details = (decision_details or "").strip()
    normalized_template = (
        template_key if template_key in DECISION_TEMPLATE_KEYS else "custom"
    )
    draft = {
        "question": normalized_question,
        "details": normalized_details,
        "template_key": normalized_template,
    }

    user = None
    user_id = request.session.get("user_id")
    if isinstance(user_id, int):
        user = db.get(models.User, user_id)

    if user is None:
        request.session["decision_draft"] = draft
        return RedirectResponse(url="/register?from=start", status_code=303)

    if legal_document_service.pending_versions(db, user.id):
        request.session["decision_draft"] = draft
        return RedirectResponse(
            url="/legal/updates?next=%2Fstart",
            status_code=303,
        )

    project = project_service.create_project(
        db=db,
        project_name=normalized_question,
        project_description=normalized_details or None,
        owner_id=user.id,
    )
    second_project_event = growth_service.record_second_project(
        db, user=user, project_id=project.id,
    )
    request.session.pop("decision_draft", None)
    return RedirectResponse(
        url=_project_redirect(project.id, second_project_event is not None),
        status_code=303,
    )


@router.get(
    "/projects",
    response_class=HTMLResponse,
)
def list_projects(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_user),
):
    projects = project_service.get_projects(
        db=db,
        owner_id=current_user.id,
    )

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "projects": projects,
        },
    )


@router.post(
    "/projects",
    response_class=HTMLResponse,
)
def create_project(
    request: Request,
    project_name: str = Form(
        ...,
        min_length=1,
        max_length=MAX_PROJECT_NAME_LENGTH,
    ),
    project_description: str | None = Form(
        None,
        max_length=MAX_PROJECT_DESCRIPTION_LENGTH,
    ),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_user),
):
    project = project_service.create_project(
        db=db,
        project_name=project_name,
        project_description=project_description,
        owner_id=current_user.id,
    )
    second_project_event = growth_service.record_second_project(
        db, user=current_user, project_id=project.id,
    )

    return RedirectResponse(
        url=_project_redirect(project.id, second_project_event is not None),
        status_code=303,
    )

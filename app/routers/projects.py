from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.auth_dependencies import require_user
from app.database import get_db
from app.services import project_service
from app.llm.safety import (
    MAX_PROJECT_DESCRIPTION_LENGTH,
    MAX_PROJECT_NAME_LENGTH,
)

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get(
    "/",
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

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": user,
        },
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

    return templates.TemplateResponse(
        request=request,
        name="project.html",
        context={
            "project": project,
        },
    )
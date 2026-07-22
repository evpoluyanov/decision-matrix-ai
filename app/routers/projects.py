from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import project_service


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.get("/projects", response_class=HTMLResponse)
def list_projects(
    request: Request,
    db: Session = Depends(get_db),
):
    projects = project_service.get_projects(db)

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={"projects": projects},
    )


@router.post("/projects", response_class=HTMLResponse)
def create_project(
    request: Request,
    project_name: str = Form(...),
    db: Session = Depends(get_db),
):
    project = project_service.create_project(
        db=db,
        project_name=project_name,
    )

    return templates.TemplateResponse(
        request=request,
        name="project.html",
        context={"project": project},
    )
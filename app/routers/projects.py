from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db


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
    projects = db.scalars(
        select(models.Project).order_by(models.Project.id)
    ).all()

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
    project = models.Project(name=project_name)

    db.add(project)
    db.commit()
    db.refresh(project)

    return templates.TemplateResponse(
        request=request,
        name="project.html",
        context={"project": project},
    )
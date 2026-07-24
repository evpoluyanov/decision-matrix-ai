from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.services import (
    alternative_service,
    criterion_service,
    project_service,
)

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    weight_error: int | None = None,
):
    project = db.get(models.Project, project_id)

    alternatives = alternative_service.get_alternatives(
        db,
        project_id,
    )

    criteria = criterion_service.get_criteria(
        db,
        project_id,
    )

    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={
            "project": project,
            "alternatives": alternatives,
            "criteria": criteria,
            "weight_error": weight_error,
        },
    )


@router.post("/projects/{project_id}/alternatives")
def create_alternative(
    project_id: int,
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    alternative_service.create_alternative(
        db,
        project_id,
        name,
    )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )
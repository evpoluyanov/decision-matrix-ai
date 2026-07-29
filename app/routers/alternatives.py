from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.services import (
    alternative_service,
    criterion_service,
    project_service,
    score_service,
    calculation_service,
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

    scores = score_service.get_scores(
        db,
        project_id,
    )

    results = calculation_service.calculate_results(
        db=db,
        project_id=project_id,
    )

    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={
            "project": project,
            "alternatives": alternatives,
            "criteria": criteria,
            "scores": scores,
            "results": results,
            "weight_error": weight_error,
        },
    )

@router.post("/projects/{project_id}/edit")
def edit_project(
    project_id: int,
    project_name: str = Form(...),
    db: Session = Depends(get_db),
):
    project = project_service.update_project(
        db=db,
        project_id=project_id,
        project_name=project_name,
    )

    if project is None:
        return RedirectResponse(
            url="/projects",
            status_code=303,
        )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )

@router.post("/projects/{project_id}/delete")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project_service.delete_project(
        db=db,
        project_id=project_id,
    )

    return RedirectResponse(
        url="/projects",
        status_code=303,
    )

@router.post("/projects/{project_id}/copy")
def copy_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    new_project = project_service.copy_project(
        db=db,
        project_id=project_id,
    )

    if new_project is None:
        raise HTTPException(
            status_code=404,
            detail="Проект не найден",
        )

    return RedirectResponse(
        url="/projects",
        status_code=303,
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


@router.post("/alternatives/{alternative_id}/delete")
def delete_alternative(
    alternative_id: int,
    db: Session = Depends(get_db),
):
    alternative = db.get(models.Alternative, alternative_id)

    if alternative is None:
        return RedirectResponse(
            "/projects",
            status_code=303,
        )

    project_id = alternative.project_id

    alternative_service.delete_alternative(
        db=db,
        alternative_id=alternative_id,
    )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )


@router.post("/alternatives/{alternative_id}/edit")
def edit_alternative(
    alternative_id: int,
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    alternative = db.get(
        models.Alternative,
        alternative_id,
    )

    if alternative is None:
        return RedirectResponse(
            url="/projects",
            status_code=303,
        )

    project_id = alternative.project_id

    alternative_service.update_alternative(
        db=db,
        alternative_id=alternative_id,
        name=name,
    )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )
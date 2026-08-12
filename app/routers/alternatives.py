from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.auth_dependencies import (
    require_alternative_owner,
    require_project_owner,
)
from app.database import get_db
from app.services import (
    alternative_service,
    calculation_service,
    criterion_service,
    project_service,
    score_service,
)


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get(
    "/projects/{project_id}",
    response_class=HTMLResponse,
)
def project_detail(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
    weight_error: int | None = None,
):
    alternatives = alternative_service.get_alternatives(
        db,
        project.id,
    )

    criteria = criterion_service.get_criteria(
        db,
        project.id,
    )

    scores = score_service.get_scores(
        db,
        project.id,
    )

    results = calculation_service.calculate_results(
        db=db,
        project_id=project.id,
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


@router.post(
    "/projects/{project_id}/edit",
)
def edit_project(
    project_id: int,
    project_name: str = Form(...),
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    project_service.update_project(
        db=db,
        project=project,
        project_name=project_name,
    )

    return RedirectResponse(
        url=f"/projects/{project.id}",
        status_code=303,
    )


@router.post(
    "/projects/{project_id}/delete",
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    project_service.delete_project(
        db=db,
        project=project,
    )

    return RedirectResponse(
        url="/projects",
        status_code=303,
    )


@router.post(
    "/projects/{project_id}/copy",
)
def copy_project(
    project_id: int,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    project_service.copy_project(
        db=db,
        source_project=project,
    )

    return RedirectResponse(
        url="/projects",
        status_code=303,
    )


@router.post(
    "/projects/{project_id}/alternatives",
)
def create_alternative(
    project_id: int,
    name: str = Form(...),
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    alternative_service.create_alternative(
        db=db,
        project_id=project.id,
        name=name,
    )

    return RedirectResponse(
        url=f"/projects/{project.id}",
        status_code=303,
    )


@router.post(
    "/alternatives/{alternative_id}/delete",
)
def delete_alternative(
    db: Session = Depends(get_db),
    alternative: models.Alternative = Depends(
        require_alternative_owner
    ),
):
    project_id = alternative.project_id

    alternative_service.delete_alternative(
        db=db,
        alternative_id=alternative.id,
    )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )


@router.post(
    "/alternatives/{alternative_id}/edit",
)
def edit_alternative(
    name: str = Form(...),
    db: Session = Depends(get_db),
    alternative: models.Alternative = Depends(
        require_alternative_owner
    ),
):
    project_id = alternative.project_id

    alternative_service.update_alternative(
        db=db,
        alternative_id=alternative.id,
        name=name,
    )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )
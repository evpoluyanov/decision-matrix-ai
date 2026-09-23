from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import models
from app.auth_dependencies import (
    require_criterion_owner,
    require_project_owner,
)
from app.database import get_db
from app.services import criterion_service

from app.llm.safety import (
    MAX_ENTITY_NAME_LENGTH,
)

router = APIRouter()


@router.post(
    "/projects/{project_id}/criteria",
)
def create_criterion(
    project_id: int,
    name: str = Form(
        ...,
        min_length=1,
        max_length=MAX_ENTITY_NAME_LENGTH,
    ),
    weight_percent: float | None = Form(None),
    importance: str | None = Form(None),
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    try:
        if importance is not None:
            criterion_service.create_simple_criterion(
                db=db,
                project_id=project.id,
                name=name,
                importance=importance,
            )
        else:
            if weight_percent is None:
                raise ValueError("Не указан вес")
            criterion_service.create_criterion(
                db=db,
                project_id=project.id,
                name=name,
                weight_percent=weight_percent,
            )
    except ValueError:
        return RedirectResponse(
            url=(
                f"/projects/{project.id}"
                "?weight_error=1"
            ),
            status_code=303,
        )

    return RedirectResponse(
        url=f"/projects/{project.id}",
        status_code=303,
    )


@router.post("/criteria/{criterion_id}/importance")
def set_criterion_importance(
    importance: str = Form(...),
    db: Session = Depends(get_db),
    criterion: models.Criterion = Depends(require_criterion_owner),
):
    criterion_service.set_simple_importance(
        db=db,
        criterion=criterion,
        importance=importance,
    )
    return RedirectResponse(
        url=f"/projects/{criterion.project_id}#priorities",
        status_code=303,
    )


@router.post(
    "/criteria/{criterion_id}/delete",
)
def delete_criterion(
    db: Session = Depends(get_db),
    criterion: models.Criterion = Depends(
        require_criterion_owner
    ),
):
    project_id = criterion.project_id

    criterion_service.delete_criterion(
        db=db,
        criterion_id=criterion.id,
    )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )


@router.post(
    "/criteria/{criterion_id}/edit",
)
def edit_criterion(
    name: str = Form(
        ...,
        min_length=1,
        max_length=MAX_ENTITY_NAME_LENGTH,
    ),
    weight_percent: float = Form(...),
    db: Session = Depends(get_db),
    criterion: models.Criterion = Depends(
        require_criterion_owner
    ),
):
    project_id = criterion.project_id

    try:
        criterion_service.update_criterion(
            db=db,
            criterion_id=criterion.id,
            name=name,
            weight_percent=weight_percent,
        )

    except ValueError:
        return RedirectResponse(
            url=(
                f"/projects/{project_id}"
                "?weight_error=1"
            ),
            status_code=303,
        )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )

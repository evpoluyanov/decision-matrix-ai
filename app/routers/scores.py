from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import models
from app.auth_dependencies import require_project_owner
from app.database import get_db
from app.services import (
    alternative_service,
    criterion_service,
    score_service,
)


router = APIRouter()


@router.post(
    "/projects/{project_id}/scores",
)
async def save_scores(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    form_data = await request.form()

    alternatives = alternative_service.get_alternatives(
        db=db,
        project_id=project.id,
    )

    criteria = criterion_service.get_criteria(
        db=db,
        project_id=project.id,
    )

    valid_alternative_ids = {
        alternative.id
        for alternative in alternatives
    }

    valid_criterion_ids = {
        criterion.id
        for criterion in criteria
    }

    for field_name, raw_value in form_data.items():
        if not field_name.startswith("score_"):
            continue

        if raw_value == "":
            continue

        parts = field_name.split("_")

        if len(parts) != 3:
            continue

        try:
            alternative_id = int(parts[1])
            criterion_id = int(parts[2])
            value = float(raw_value)
        except ValueError:
            continue

        if alternative_id not in valid_alternative_ids:
            continue

        if criterion_id not in valid_criterion_ids:
            continue

        if value < 0 or value > 10:
            continue

        score_service.set_score(
            db=db,
            alternative_id=alternative_id,
            criterion_id=criterion_id,
            value=value,
        )

    return RedirectResponse(
        url=f"/projects/{project.id}",
        status_code=303,
    )
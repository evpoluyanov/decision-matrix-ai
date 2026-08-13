from pydantic import BaseModel, Field

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import models
from app.auth_dependencies import (
    require_project_owner,
)
from app.database import get_db
from app.services import (
    ai_alternative_service,
    alternative_service,
)


router = APIRouter()


class AcceptedAlternative(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    explanation: str = Field(
        min_length=1,
        max_length=180,
    )


class AcceptAlternativesRequest(
    BaseModel
):
    items: list[
        AcceptedAlternative
    ]


@router.post(
    "/projects/{project_id}/ai/alternatives"
)
def suggest_alternatives(
    project_id: int,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    alternatives = (
        alternative_service
        .get_alternatives(
            db,
            project.id,
        )
    )

    try:
        result = (
            ai_alternative_service
            .generate_alternative_suggestions(
                project=project,
                existing_alternatives=(
                    alternatives
                ),
            )
        )

    except RuntimeError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": (
                    "Не удалось получить "
                    "предложения ИИ. "
                    "Попробуйте ещё раз."
                ),
            },
        )

    return result


@router.post(
    "/projects/{project_id}/ai/"
    "alternatives/accept"
)
def accept_alternatives(
    project_id: int,
    request: AcceptAlternativesRequest,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    suggestions = [
        {
            "name": item.name,
            "explanation": (
                item.explanation
            ),
        }
        for item in request.items
    ]

    created = (
        alternative_service
        .create_ai_alternatives(
            db=db,
            project_id=project.id,
            suggestions=suggestions,
        )
    )

    return {
        "status": "ok",
        "created": len(created),
    }
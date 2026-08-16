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
    ai_criterion_service,
    criterion_service,
    ai_score_service,
    score_service,
    ai_result_service,
    calculation_service,
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

class AcceptedCriterion(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    weight_percent: float = Field(
        ge=0,
        le=100,
    )

    ai_suggested_weight_percent: float = Field(
        ge=0,
        le=100,
    )

    criterion_explanation: str = Field(
        min_length=1,
        max_length=180,
    )

    weight_explanation: str = Field(
        min_length=1,
        max_length=180,
    )


class AcceptCriteriaRequest(BaseModel):
    items: list[AcceptedCriterion]

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

@router.post(
    "/projects/{project_id}/ai/criteria"
)
def suggest_criteria(
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

    criteria = (
        criterion_service
        .get_criteria(
            db,
            project.id,
        )
    )

    try:
        result = (
            ai_criterion_service
            .generate_criterion_suggestions(
                project=project,
                alternatives=alternatives,
                existing_criteria=criteria,
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
    "criteria/accept"
)
def accept_criteria(
    project_id: int,
    request: AcceptCriteriaRequest,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    suggestions = [
        {
            "name": item.name,
            "weight_percent": (
                item.weight_percent
            ),
            "ai_suggested_weight_percent": (
                item.ai_suggested_weight_percent
            ),
            "criterion_explanation": (
                item.criterion_explanation
            ),
            "weight_explanation": (
                item.weight_explanation
            ),
        }
        for item in request.items
    ]

    try:
        created = (
            criterion_service
            .create_ai_criteria(
                db=db,
                project_id=project.id,
                suggestions=suggestions,
            )
        )

    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={
                "status": "weight_error",
                "message": str(exc),
            },
        )

    return {
        "status": "ok",
        "created": len(created),
    }

@router.post(
    "/projects/{project_id}/ai/scores"
)
def suggest_scores(
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

    criteria = (
        criterion_service
        .get_criteria(
            db,
            project.id,
        )
    )

    try:
        result = (
            ai_score_service
            .generate_score_suggestions(
                project=project,
                alternatives=alternatives,
                criteria=criteria,
            )
        )

    except RuntimeError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": (
                    "Не удалось получить "
                    "оценки ИИ. "
                    "Попробуйте ещё раз."
                ),
            },
        )

    if result["status"] != "ok":
        return result

    updated = (
        score_service
        .set_ai_scores(
            db=db,
            suggestions=(
                result["items"]
            ),
        )
    )

    return {
        **result,
        "updated": updated,
    }

@router.post(
    "/projects/{project_id}/ai/result-explanation"
)
def explain_result(
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

    criteria = (
        criterion_service
        .get_criteria(
            db,
            project.id,
        )
    )

    scores = (
        score_service
        .get_scores(
            db,
            project.id,
        )
    )

    score_summary = (
        score_service
        .get_score_summary(
            scores=scores,
            alternatives_count=len(
                alternatives
            ),
            criteria_count=len(
                criteria
            ),
        )
    )

    results = (
        calculation_service
        .calculate_results(
            db=db,
            project_id=project.id,
        )
    )

    try:
        result = (
            ai_result_service
            .generate_result_explanation(
                project=project,
                alternatives=alternatives,
                criteria=criteria,
                scores=scores,
                results=results,
                score_summary=score_summary,
            )
        )

    except RuntimeError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": (
                    "Не удалось подготовить "
                    "объяснение результата. "
                    "Попробуйте ещё раз."
                ),
            },
        )

    return result
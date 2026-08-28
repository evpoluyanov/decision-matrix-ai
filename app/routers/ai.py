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
from app.llm import safety as ai_safety
from app.services import (
    ai_alternative_service,
    alternative_service,
    ai_criterion_service,
    criterion_service,
    ai_score_service,
    score_service,
    ai_result_service,
    calculation_service,
    ai_decision_risk_service,
    project_ai_analysis_service,
    ai_usage_service,
    ai_budget_service,
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
    ] = Field(
        min_length=1,
        max_length=(
            ai_safety
            .MAX_AI_ITEMS_PER_REQUEST
        ),
    )

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
    items: list[
        AcceptedCriterion
    ] = Field(
        min_length=1,
        max_length=(
            ai_safety
            .MAX_AI_ITEMS_PER_REQUEST
        ),
    )
def get_ai_scope_error_response(
    *,
    project: models.Project,
    alternatives_count: int = 0,
    criteria_count: int = 0,
    check_matrix_size: bool = False,
) -> JSONResponse | None:
    message = ai_safety.get_ai_scope_error(
        project_name=project.name,
        project_description=project.description,
        alternatives_count=alternatives_count,
        criteria_count=criteria_count,
        check_matrix_size=check_matrix_size,
    )

    if message is None:
        return None

    return JSONResponse(
        status_code=400,
        content={
            "status": "input_limit_exceeded",
            "message": message,
        },
    )


def reserve_ai_request_or_response(
    *,
    db: Session,
    project: models.Project,
    feature: str,
) -> (
    models.AIRequestLog
    | JSONResponse
):
    # The existing owner check runs first, preserving 404 for foreign projects.
    if not project.owner.email_verified:
        return JSONResponse(status_code=403, content={
            "status": "email_verification_required",
            "message": "Подтвердите email в личном кабинете, чтобы пользоваться ИИ.",
        })
    try:
        ai_budget_service.get_pricing()
    except ai_budget_service.AIBudgetConfigurationError:
        return JSONResponse(status_code=503, content={
            "status": "ai_unavailable",
            "message": "ИИ временно недоступен. Работа с проектами вручную доступна.",
        })
    try:
        return (
            ai_usage_service
            .reserve_ai_request(
                db=db,
                user_id=project.owner_id,
                project_id=project.id,
                feature=feature,
            )
        )

    except (
        ai_usage_service
        .AIRequestLimitError
    ) as exc:
        return JSONResponse(
            status_code=429,
            content={
                "status": "rate_limited",
                "message": str(exc),
                "scope": exc.scope,
            },
        )


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

    scope_error = get_ai_scope_error_response(
        project=project,
        alternatives_count=len(
            alternatives
        ),
    )

    if scope_error is not None:
        return scope_error

    reservation = (
        reserve_ai_request_or_response(
            db=db,
            project=project,
            feature="alternatives",
        )
    )

    if isinstance(
        reservation,
        JSONResponse,
    ):
        return reservation

    request_log = reservation

    try:
        with ai_budget_service.request_context(db, request_log):
            result = (
                ai_alternative_service
                .generate_alternative_suggestions(
                    project=project,
                    existing_alternatives=(
                        alternatives
                    ),
                )
            )

    except ai_budget_service.AIBudgetExceeded as exc:
        db.rollback()
        ai_usage_service.fail_ai_request(db=db, request_log=request_log)
        return JSONResponse(status_code=429, content={
            "status": "budget_exhausted", "message": str(exc), "scope": "global_day",
        })

    except RuntimeError:
        (
            ai_usage_service
            .fail_ai_request(
                db=db,
                request_log=request_log,
            )
        )

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

    (
        ai_usage_service
        .complete_ai_request(
            db=db,
            request_log=request_log,
            usage=result.get(
                "usage",
                {},
            ),
        )
    )

    if result.get("status") == "unsafe_content":
        return JSONResponse(
            status_code=400,
            content=result,
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

    scope_error = get_ai_scope_error_response(
        project=project,
        alternatives_count=len(
            alternatives
        ),
        criteria_count=len(
            criteria
        ),
    )

    if scope_error is not None:
        return scope_error

    reservation = (
        reserve_ai_request_or_response(
            db=db,
            project=project,
            feature="criteria",
        )
    )

    if isinstance(
        reservation,
        JSONResponse,
    ):
        return reservation

    request_log = reservation

    try:
        with ai_budget_service.request_context(db, request_log):
            result = (
                ai_criterion_service
                .generate_criterion_suggestions(
                    project=project,
                    alternatives=alternatives,
                    existing_criteria=criteria,
                )
            )

    except ai_budget_service.AIBudgetExceeded as exc:
        db.rollback()
        ai_usage_service.fail_ai_request(db=db, request_log=request_log)
        return JSONResponse(status_code=429, content={
            "status": "budget_exhausted", "message": str(exc), "scope": "global_day",
        })

    except RuntimeError:
        (
            ai_usage_service
            .fail_ai_request(
                db=db,
                request_log=request_log,
            )
        )

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

    (
        ai_usage_service
        .complete_ai_request(
            db=db,
            request_log=request_log,
            usage=result.get(
                "usage",
                {},
            ),
        )
    )

    if result.get("status") == "unsafe_content":
        return JSONResponse(
            status_code=400,
            content=result,
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

    scope_error = get_ai_scope_error_response(
        project=project,
        alternatives_count=len(
            alternatives
        ),
        criteria_count=len(
            criteria
        ),
        check_matrix_size=True,
    )

    if scope_error is not None:
        return scope_error

    reservation = (
        reserve_ai_request_or_response(
            db=db,
            project=project,
            feature="scores",
        )
    )

    if isinstance(
        reservation,
        JSONResponse,
    ):
        return reservation

    request_log = reservation

    try:
        with ai_budget_service.request_context(db, request_log):
            result = (
                ai_score_service
                .generate_score_suggestions(
                    project=project,
                    alternatives=alternatives,
                    criteria=criteria,
                )
            )

    except ai_budget_service.AIBudgetExceeded as exc:
        db.rollback()
        ai_usage_service.fail_ai_request(db=db, request_log=request_log)
        return JSONResponse(status_code=429, content={
            "status": "budget_exhausted", "message": str(exc), "scope": "global_day",
        })

    except RuntimeError:
        (
            ai_usage_service
            .fail_ai_request(
                db=db,
                request_log=request_log,
            )
        )

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

    (
        ai_usage_service
        .complete_ai_request(
            db=db,
            request_log=request_log,
            usage=result.get(
                "usage",
                {},
            ),
        )
    )

    if result.get("status") == "unsafe_content":
        return JSONResponse(
            status_code=400,
            content=result,
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

    scope_error = get_ai_scope_error_response(
        project=project,
        alternatives_count=len(
            alternatives
        ),
        criteria_count=len(
            criteria
        ),
        check_matrix_size=True,
    )

    if scope_error is not None:
        return scope_error

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

    reservation = (
        reserve_ai_request_or_response(
            db=db,
            project=project,
            feature="result_explanation",
        )
    )

    if isinstance(
        reservation,
        JSONResponse,
    ):
        return reservation

    request_log = reservation

    try:
        with ai_budget_service.request_context(db, request_log):
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

    except ai_budget_service.AIBudgetExceeded as exc:
        db.rollback()
        ai_usage_service.fail_ai_request(db=db, request_log=request_log)
        return JSONResponse(status_code=429, content={
            "status": "budget_exhausted", "message": str(exc), "scope": "global_day",
        })

    except RuntimeError:
        (
            ai_usage_service
            .fail_ai_request(
                db=db,
                request_log=request_log,
            )
        )

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

    (
        ai_usage_service
        .complete_ai_request(
            db=db,
            request_log=request_log,
            usage=result.get(
                "usage",
                {},
            ),
        )
    )

    if result.get("status") == "unsafe_content":
        return JSONResponse(
            status_code=400,
            content=result,
        )

    if result.get("status") == "ok":
        (
            project_ai_analysis_service
            .save_result_explanation(
                db=db,
                project_id=project.id,
                result=result,
            )
        )

    return result

@router.post(
    "/projects/{project_id}/ai/decision-risks"
)
def analyze_decision_risks(
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

    scope_error = get_ai_scope_error_response(
        project=project,
        alternatives_count=len(
            alternatives
        ),
        criteria_count=len(
            criteria
        ),
        check_matrix_size=True,
    )

    if scope_error is not None:
        return scope_error

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

    reservation = (
        reserve_ai_request_or_response(
            db=db,
            project=project,
            feature="decision_risks",
        )
    )

    if isinstance(
        reservation,
        JSONResponse,
    ):
        return reservation

    request_log = reservation

    try:
        with ai_budget_service.request_context(db, request_log):
            result = (
                ai_decision_risk_service
                .generate_decision_risks(
                    project=project,
                    criteria=criteria,
                    scores=scores,
                    results=results,
                    score_summary=score_summary,
                )
            )

    except ai_budget_service.AIBudgetExceeded as exc:
        db.rollback()
        ai_usage_service.fail_ai_request(db=db, request_log=request_log)
        return JSONResponse(status_code=429, content={
            "status": "budget_exhausted", "message": str(exc), "scope": "global_day",
        })

    except RuntimeError:
        (
            ai_usage_service
            .fail_ai_request(
                db=db,
                request_log=request_log,
            )
        )

        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": (
                    "Не удалось выполнить "
                    "анализ рисков. "
                    "Попробуйте ещё раз."
                ),
            },
        )

    (
        ai_usage_service
        .complete_ai_request(
            db=db,
            request_log=request_log,
            usage=result.get(
                "usage",
                {},
            ),
        )
    )

    if result.get("status") == "unsafe_content":
        return JSONResponse(
            status_code=400,
            content=result,
        )

    if result.get("status") == "ok":
        (
            project_ai_analysis_service
            .save_decision_risks(
                db=db,
                project_id=project.id,
                result=result,
            )
        )

    return result

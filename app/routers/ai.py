from pydantic import BaseModel, Field

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from time import perf_counter
from app.services import operation_service
from app.llm.errors import ProviderError

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
    ai_score_generation_service,
    growth_service,
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
    commit: bool = True,
    request: Request | None = None,
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
    key = request.headers.get("x-operation-key") if request else None
    if key and not operation_service.KEY.fullmatch(key):
        return JSONResponse({"status": "invalid_key", "message": "Некорректный идентификатор операции."}, status_code=400)
    if request is not None:
        db.query(models.Project).filter_by(id=project.id).with_for_update().one()
        if key:
            previous = db.query(models.AIRequestLog).filter_by(client_request_key=key).first()
            if previous:
                if previous.user_id != project.owner_id or previous.project_id != project.id or previous.feature != feature:
                    return JSONResponse({"status": "invalid_key"}, status_code=409)
                return JSONResponse(operation_service.state(db, previous), status_code=409)
        active = db.query(models.AIRequestLog).filter_by(
            project_id=project.id, user_id=project.owner_id, feature=feature, status="started",
        ).order_by(models.AIRequestLog.id.desc()).first()
        if active:
            return JSONResponse(operation_service.state(db, active), status_code=409)
    try:
        log = ai_usage_service.reserve_ai_request(db=db, user_id=project.owner_id,
            project_id=project.id, feature=feature, commit=False)
        log.client_request_key = key
        if commit:
            db.commit()
            db.refresh(log)
        return log

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
    request: Request,
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
            request=request,
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
    if result.get("status") == "ok":
        growth_service.record_trial_ai_project(
            db, user_id=project.owner_id, project_id=project.id,
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
    request: Request,
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
            request=request,
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

    if result.get("status") == "ok":
        growth_service.record_trial_ai_project(
            db, user_id=project.owner_id, project_id=project.id,
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

    try:
        job = ai_score_generation_service.matching_active_job(
            db, project, alternatives, criteria,
        )
    except ai_score_generation_service.GenerationBusyError as exc:
        active_job = db.get(models.AIScoreGenerationJob, project.id)
        if active_job and active_job.status == "uncertain":
            return JSONResponse({"status": "uncertain", "message": str(exc)}, status_code=503)
        return {
            "status": "in_progress",
            "message": str(exc),
            "retry_after_ms": 1500,
        }

    if job is None:
        reservation = reserve_ai_request_or_response(
            db=db,
            project=project,
            feature="scores",
            commit=False,
        )
        if isinstance(reservation, JSONResponse):
            return reservation
        request_log = reservation
        job = ai_score_generation_service.create_job(
            db, project, request_log, alternatives, criteria,
        )
    else:
        request_log = db.get(models.AIRequestLog, job.request_log_id)

    try:
        batch = ai_score_generation_service.claim_batch(
            db, job, alternatives, criteria,
        )
    except ai_score_generation_service.GenerationRetryLimitError as exc:
        return JSONResponse(
            status_code=429,
            content={"status": "retry_limit", "message": str(exc)},
        )
    except ai_score_generation_service.MatrixChangedError as exc:
        return JSONResponse(
            status_code=409,
            content={"status": "matrix_changed", "message": str(exc)},
        )

    try:
        with ai_budget_service.request_context(db, request_log):
            result = (
                ai_score_service
                .generate_score_suggestions(
                    project=project,
                    alternatives=batch,
                    criteria=criteria,
                )
            )

    except ai_budget_service.AIBudgetExceeded as exc:
        db.rollback()
        ai_score_generation_service.release_after_error(db, job, exc)
        return JSONResponse(status_code=429, content={
            "status": "budget_exhausted", "message": str(exc), "scope": "global_day",
        })

    except RuntimeError as exc:
        db.rollback()
        failure_code = ai_score_generation_service.release_after_error(
            db, job, exc,
        )
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error_code": failure_code,
                "message": (
                    "Не удалось получить "
                    "оценки ИИ. "
                    "Попробуйте ещё раз."
                ),
            },
        )

    if result.get("status") == "unsafe_content":
        ai_score_generation_service.complete_without_scores(
            db,
            job,
            request_log,
            job_status="cancelled",
            error_code="unsafe_content",
        )
        return JSONResponse(
            status_code=400,
            content=result,
        )

    if result["status"] != "ok":
        ai_score_generation_service.complete_without_scores(
            db, job, request_log,
        )
        return result

    try:
        response = ai_score_generation_service.finish_batch(db, job, criteria, batch, result)
    except ai_score_generation_service.MatrixChangedError as exc:
        return JSONResponse({"status": "matrix_changed", "message": str(exc)}, status_code=409)
    growth_service.record_trial_ai_project(
        db, user_id=project.owner_id, project_id=project.id,
    )
    return response

def _analyze(project, request, db, feature):
    started = perf_counter()
    revision = score_service.matrix_version(db, project.id)
    alternatives = alternative_service.get_alternatives(db, project.id)
    criteria = criterion_service.get_criteria(db, project.id)
    scope_error = get_ai_scope_error_response(project=project, alternatives_count=len(alternatives),
        criteria_count=len(criteria), check_matrix_size=True)
    if scope_error is not None:
        return scope_error
    scores = score_service.get_scores(db, project.id)
    score_summary = score_service.get_score_summary(scores=scores, alternatives_count=len(alternatives), criteria_count=len(criteria))
    results = calculation_service.calculate_results(db, project.id)
    reservation = reserve_ai_request_or_response(db=db, project=project, feature=feature, request=request)
    if isinstance(reservation, JSONResponse):
        return reservation
    request_log = reservation
    try:
        with ai_budget_service.request_context(db, request_log):
            if feature == "decision_risks":
                result = ai_decision_risk_service.generate_decision_risks(
                    project=project, criteria=criteria, scores=scores, results=results, score_summary=score_summary)
            else:
                result = ai_result_service.generate_result_explanation(
                    project=project, alternatives=alternatives, criteria=criteria, scores=scores, results=results, score_summary=score_summary)
        if result.get("status") == "ok":
            # Re-read after provider ledger commits released the transaction.
            locked = db.query(models.Project).filter_by(id=project.id).populate_existing().with_for_update().one()
            if locked.matrix_revision != revision:
                raise ProviderError("Матрица изменилась. Устаревший результат не сохранён.", "matrix_changed")
            save = project_ai_analysis_service.save_decision_risks if feature == "decision_risks" else project_ai_analysis_service.save_result_explanation
            save(db=db, project_id=project.id, result=result)
        if result.get("status") != "ok":
            request_log.error_code = "no_result"
        ai_usage_service.complete_ai_request(db=db, request_log=request_log, usage=result.get("usage", {}))
        if result.get("status") == "ok":
            growth_service.record_trial_ai_project(db, user_id=project.owner_id, project_id=project.id)
        operation_service.diagnostic(request_log.id, feature, (perf_counter()-started)*1000)
        if result.get("status") == "unsafe_content":
            return JSONResponse(result, status_code=400)
        return result
    except (RuntimeError, ValueError, SQLAlchemyError) as exc:
        db.rollback()
        code = operation_service.failure_code(exc)
        if isinstance(exc, ai_budget_service.AIBudgetExceeded):
            code = "budget_exhausted"
        if request_log.status == "started":
            ai_usage_service.fail_ai_request(db=db, request_log=request_log, error_code=code)
        operation_service.diagnostic(request_log.id, feature, (perf_counter()-started)*1000,
            code=code, http_status=getattr(exc, "http_status", None))
        message = {
            "truncated_response": "Ответ ИИ обрезан лимитом токенов. Данные проекта и известные расходы сохранены.",
            "matrix_changed": "Матрица изменилась во время анализа. Устаревший результат не сохранён.",
            "provider_timeout": "Ожидание ответа модели завершилось. Проверяем состояние; повторный запрос автоматически не отправляется.",
            "budget_exhausted": "Дневной бюджет ИИ исчерпан. Работа вручную доступна.",
        }.get(code, "Не удалось завершить анализ. Матрица и предыдущие результаты доступны.")
        return JSONResponse({"status": "budget_exhausted" if code == "budget_exhausted" else "error", "scope": "global_day" if code == "budget_exhausted" else None, "error_code": code, "request_id": request_log.id, "message": message},
                            status_code=429 if code == "budget_exhausted" else 503)


@router.post("/projects/{project_id}/ai/result-explanation")
def explain_result(project_id: int, request: Request, db: Session = Depends(get_db),
                   project: models.Project = Depends(require_project_owner)):
    return _analyze(project, request, db, "result_explanation")


@router.post("/projects/{project_id}/ai/decision-risks")
def analyze_decision_risks(project_id: int, request: Request, db: Session = Depends(get_db),
                          project: models.Project = Depends(require_project_owner)):
    return _analyze(project, request, db, "decision_risks")


@router.get("/projects/{project_id}/ai/operations/{key}")
def operation_state(project_id: int, key: str, db: Session = Depends(get_db),
                    project: models.Project = Depends(require_project_owner)):
    if not operation_service.KEY.fullmatch(key):
        return JSONResponse({"status": "not_found"}, status_code=404)
    log = db.query(models.AIRequestLog).filter_by(project_id=project.id, user_id=project.owner_id, client_request_key=key).first()
    if not log:
        return JSONResponse({"status": "not_found", "message": "Запрос не найден. Новое обращение к модели не отправлено."}, status_code=404)
    info = operation_service.state(db, log)
    if info["status"] == "completed" and not log.error_code:
        saved = project_ai_analysis_service.to_report_data(project_ai_analysis_service.get_analysis(db, project.id))
        if log.feature == "result_explanation" and saved["result"]:
            info["result"] = {"status": "ok", **saved["result"]}
        elif log.feature == "decision_risks" and saved["decision_risks"]:
            info["result"] = {"status": "ok", "items": saved["decision_risks"], "preliminary": saved.get("decision_risks_preliminary", False)}
    return info


@router.get("/projects/{project_id}/ai/scores/state")
def score_generation_state(project_id: int, db: Session = Depends(get_db),
                           project: models.Project = Depends(require_project_owner)):
    job = db.get(models.AIScoreGenerationJob, project.id)
    if job is None:
        return {"status": "not_started"}
    log = db.get(models.AIRequestLog, job.request_log_id)
    info = operation_service.state(db, log)
    if job.status == "uncertain":
        info["status"] = "uncertain"
    info["job_status"] = job.status
    info["completed"] = job.next_alternative_index * len(ai_score_generation_service.decoded(job.criterion_ids_json))
    return info

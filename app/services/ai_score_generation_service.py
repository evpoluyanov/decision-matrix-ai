"""Resumable, one-provider-call-at-a-time AI score generation."""

import json
import math
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.services import score_service


MAX_PAIRS_PER_BATCH = 20
PROCESSING_LEASE = timedelta(minutes=2)


class MatrixChangedError(RuntimeError):
    pass


class GenerationBusyError(RuntimeError):
    pass


class GenerationRetryLimitError(RuntimeError):
    pass


def ids(items):
    return [item.id for item in items]


def encoded(values):
    return json.dumps(values, separators=(",", ":"))


def decoded(value):
    data = json.loads(value)
    if not isinstance(data, list) or any(
        isinstance(item, bool) or not isinstance(item, int) for item in data
    ):
        raise ValueError("Некорректное состояние генерации оценок.")
    return data


def get_job(db: Session, project_id: int):
    return (
        db.query(models.AIScoreGenerationJob)
        .filter(models.AIScoreGenerationJob.project_id == project_id)
        .with_for_update()
        .one_or_none()
    )


def matching_active_job(db, project, alternatives, criteria, now=None):
    current = now or datetime.now(timezone.utc)
    # This row exists before any generation job and serializes the initial
    # reservation across tabs. The lock is released when the batch is claimed.
    db.query(models.Project).filter(
        models.Project.id == project.id,
    ).with_for_update().one()
    job = get_job(db, project.id)
    if job is not None and job.status == "uncertain":
        raise GenerationBusyError("Исход предыдущего обращения неизвестен. Резерв сохранён; новый вызов не отправлен.")
    if job is None or job.status not in {"ready", "processing"}:
        return None
    request_log = db.get(models.AIRequestLog, job.request_log_id)
    matches = (
        request_log is not None
        and request_log.status == "started"
        and request_log.user_id == project.owner_id
        and encoded(ids(alternatives)) == job.alternative_ids_json
        and encoded(ids(criteria)) == job.criterion_ids_json
    )
    if not matches:
        cancel_job(db, job, request_log, "matrix_changed", current)
        return None
    updated_at = job.updated_at
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    if job.status == "processing" and current - updated_at < PROCESSING_LEASE:
        raise GenerationBusyError("Предыдущая часть матрицы ещё обрабатывается.")
    if job.status == "processing":
        job.status = "uncertain"
        job.last_error_code = "processing_lease_expired"
        job.updated_at = current
        db.commit()
        db.refresh(job)
        raise GenerationBusyError("Завершение предыдущего обращения не подтверждено. Новый вызов не отправлен.")
    return job


def create_job(db, project, request_log, alternatives, criteria, now=None):
    current = now or datetime.now(timezone.utc)
    job = get_job(db, project.id)
    if job is None:
        job = models.AIScoreGenerationJob(project_id=project.id)
        db.add(job)
    else:
        old_log = db.get(models.AIRequestLog, job.request_log_id)
        if old_log is not None and old_log.status == "started":
            old_log.status = "failed"
            old_log.completed_at = current
    job.request_log_id = request_log.id
    job.alternative_ids_json = encoded(ids(alternatives))
    job.criterion_ids_json = encoded(ids(criteria))
    job.next_alternative_index = 0
    job.provider_attempts = 0
    job.status = "ready"
    job.last_error_code = None
    job.created_at = current
    job.updated_at = current
    db.commit()
    db.refresh(job)
    return job


def cancel_job(db, job, request_log, error_code, now=None):
    current = now or datetime.now(timezone.utc)
    job.status = "cancelled"
    job.last_error_code = error_code
    job.updated_at = current
    if request_log is not None and request_log.status == "started":
        request_log.status = "failed"
        request_log.completed_at = current
    db.commit()


def claim_batch(db, job, alternatives, criteria, now=None):
    current = now or datetime.now(timezone.utc)
    if (
        decoded(job.alternative_ids_json) != ids(alternatives)
        or decoded(job.criterion_ids_json) != ids(criteria)
    ):
        request_log = db.get(models.AIRequestLog, job.request_log_id)
        cancel_job(db, job, request_log, "matrix_changed", current)
        raise MatrixChangedError(
            "Матрица изменилась во время генерации. Запустите оценку заново."
        )
    alternatives_per_batch = max(1, MAX_PAIRS_PER_BATCH // len(criteria))
    total_batches = math.ceil(len(alternatives) / alternatives_per_batch)
    if job.provider_attempts >= total_batches + 3:
        request_log = db.get(models.AIRequestLog, job.request_log_id)
        cancel_job(db, job, request_log, "retry_limit", current)
        raise GenerationRetryLimitError(
            "Слишком много неудачных попыток этой генерации. Запустите её заново."
        )
    start = job.next_alternative_index
    batch = alternatives[start:start + alternatives_per_batch]
    if not batch:
        raise RuntimeError("Некорректный прогресс генерации оценок.")
    job.status = "processing"
    job.matrix_revision = score_service.matrix_version(db, job.project_id)
    job.provider_attempts += 1
    job.last_error_code = None
    job.updated_at = current
    db.commit()
    return batch


def error_code(exc):
    message = str(exc).lower()
    if "дневной бюджет" in message:
        return "budget_exhausted"
    if "вовремя" in message:
        return "provider_timeout"
    if "подключиться" in message:
        return "provider_connection"
    if "api вернул ошибку" in message:
        return "provider_http_error"
    if "json" in message:
        return "invalid_json"
    if "полный пакет" in message:
        return "incomplete_batch"
    return "provider_response_error"


def release_after_error(db, job, exc, now=None):
    failure_code = error_code(exc)
    job = db.get(models.AIScoreGenerationJob, job.project_id)
    if job is not None and job.status == "processing":
        unknown = db.query(models.AIProviderCall.id).filter(
            models.AIProviderCall.request_log_id == job.request_log_id,
            models.AIProviderCall.status != "reported",
        ).first() is not None
        job.status = "uncertain" if unknown else "ready"
        job.last_error_code = failure_code
        job.updated_at = now or datetime.now(timezone.utc)
        db.commit()
    return failure_code


def complete_without_scores(
    db,
    job,
    request_log,
    now=None,
    *,
    job_status="completed",
    error_code=None,
):
    current = now or datetime.now(timezone.utc)
    job = db.get(models.AIScoreGenerationJob, job.project_id)
    request_log = db.get(models.AIRequestLog, request_log.id)
    job.status = job_status
    job.last_error_code = error_code
    job.updated_at = current
    request_log.status = "completed"
    request_log.completed_at = current
    db.commit()


def finish_batch(db, job, criteria, batch, result, now=None):
    current = now or datetime.now(timezone.utc)
    job = db.get(models.AIScoreGenerationJob, job.project_id)
    request_log = db.get(models.AIRequestLog, job.request_log_id)
    project = db.query(models.Project).filter_by(id=job.project_id).populate_existing().with_for_update().one()
    if job.matrix_revision is not None and project.matrix_revision != job.matrix_revision:
        cancel_job(db, job, request_log, "matrix_changed", current)
        raise MatrixChangedError("Матрица изменилась во время генерации. Устаревшие оценки не сохранены.")
    score_service.set_ai_scores(db, result["items"], commit=False)
    # Production MWS records usage before validating model content. Unit tests
    # replace the provider, so preserve their usage without double-counting.
    provider_calls = db.query(func.count(models.AIProviderCall.id)).filter(
        models.AIProviderCall.request_log_id == request_log.id,
    ).scalar() or 0
    if provider_calls == 0:
        usage = result.get("usage", {})
        request_log.input_tokens += int(usage.get("input_tokens", 0))
        request_log.output_tokens += int(usage.get("output_tokens", 0))
        request_log.reasoning_tokens += int(usage.get("reasoning_tokens", 0))
        request_log.total_tokens += int(usage.get("total_tokens", 0))
    usage = result.get("usage", {})
    provider = usage.get("provider")
    model = usage.get("model")
    response_id = usage.get("response_id")
    if isinstance(provider, str) and provider:
        request_log.provider = provider[:50]
    if isinstance(model, str) and model:
        request_log.model = model[:100]
    if isinstance(response_id, str) and response_id:
        request_log.provider_response_id = response_id[:200]
    job.next_alternative_index += len(batch)
    job.updated_at = current
    completed = job.next_alternative_index >= len(decoded(job.alternative_ids_json))
    if completed:
        job.status = "completed"
        request_log.status = "completed"
        request_log.completed_at = current
    else:
        job.status = "ready"
    db.commit()
    return progress(job, len(criteria), request_log, result)


def progress(job, criteria_count, request_log, result=None):
    total_alternatives = len(decoded(job.alternative_ids_json))
    total_pairs = total_alternatives * criteria_count
    completed_pairs = min(job.next_alternative_index, total_alternatives) * criteria_count
    response = {
        "status": "ok" if job.status == "completed" else "in_progress",
        "completed": completed_pairs,
        "total": total_pairs,
        "message": (
            "Матрица оценена ИИ."
            if job.status == "completed"
            else f"Обработано {completed_pairs} из {total_pairs} оценок."
        ),
    }
    if job.status == "completed":
        response["updated"] = total_pairs
        response["usage"] = {
            "provider": (result or {}).get("usage", {}).get("provider", "mws"),
            "model": (result or {}).get("usage", {}).get("model", ""),
            "response_id": request_log.provider_response_id,
            "input_tokens": request_log.input_tokens,
            "output_tokens": request_log.output_tokens,
            "reasoning_tokens": request_log.reasoning_tokens,
            "total_tokens": request_log.total_tokens,
        }
    return response

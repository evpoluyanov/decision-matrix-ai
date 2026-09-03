"""Safe request identity/status/diagnostics; never logs user content."""
import json
import logging
import re
from sqlalchemy import select
from app import models

logger = logging.getLogger("dmatrix.operations")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    # Dedicated safe records are visible with both uvicorn and serverless runtimes.
    logger.addHandler(logging.StreamHandler())
KEY = re.compile(r"^[a-zA-Z0-9_-]{16,64}$")


def failure_code(exc):
    code = getattr(exc, "code", None)
    if code in {"provider_timeout", "provider_connection", "provider_http_error", "truncated_response", "invalid_response", "matrix_changed"}:
        return code
    if isinstance(exc.__cause__, json.JSONDecodeError):
        return "invalid_json"
    return "response_processing_error"


def diagnostic(request_id, stage, elapsed_ms, *, code=None, http_status=None, finish_reason=None, incoming=None, outgoing=None):
    # Explicit fields only: no exception repr/str, URLs, prompts or responses.
    logger.info("AI_DIAG %s", json.dumps({"request_id": request_id, "stage": stage,
        "duration_ms": round(elapsed_ms, 2), "error_code": code,
        "http_status": http_status, "finish_reason": finish_reason if finish_reason in {"stop", "length", "content_filter"} else None,
        "prompt_tokens": incoming, "completion_tokens": outgoing}))


def state(db, log):
    uncertain = db.scalar(select(models.AIProviderCall.id).where(
        models.AIProviderCall.request_log_id == log.id,
        models.AIProviderCall.status != "reported",
    ).limit(1))
    if log.status == "started":
        status = "in_progress"
        message = "Запрос ещё выполняется или его завершение пока не подтверждено. Новый запрос не отправлен."
    elif uncertain:
        status = "uncertain"
        message = "Исход обращения к модели неизвестен. Резерв сохранён. Новый запрос не отправлен; можно проверить состояние позже."
    else:
        status = "completed" if log.status == "completed" else "failed"
        message = "Предыдущая операция завершена." if status == "completed" else "Предыдущая операция завершилась ошибкой."
    return {"status": status, "message": message, "request_id": log.id,
            "request_key": log.client_request_key, "error_code": log.error_code}

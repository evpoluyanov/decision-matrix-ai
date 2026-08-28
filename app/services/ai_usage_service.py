import os
from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy.orm import Session

from app import models


DEFAULT_AI_REQUESTS_PER_MINUTE = 3
DEFAULT_AI_REQUESTS_PER_24_HOURS = 30

AI_FEATURES = frozenset(
    {
        "alternatives",
        "criteria",
        "scores",
        "result_explanation",
        "decision_risks",
    }
)

RATE_LIMIT_MESSAGE = (
    "Слишком много запросов к ИИ. "
    "Подождите немного и повторите попытку."
)

DAILY_LIMIT_MESSAGE = (
    "Лимит запросов к ИИ за последние "
    "24 часа исчерпан. Попробуйте позже."
)


class AIRequestLimitError(RuntimeError):
    def __init__(
        self,
        *,
        message: str,
        scope: str,
    ):
        super().__init__(
            message
        )

        self.scope = scope


def get_positive_int_setting(
    name: str,
    default: int,
) -> int:
    raw_value = os.getenv(
        name
    )

    if raw_value is None:
        return default

    try:
        value = int(
            raw_value
        )
    except ValueError as exc:
        raise RuntimeError(
            f"Переменная {name} "
            "должна быть целым числом."
        ) from exc

    if value < 1:
        raise RuntimeError(
            f"Переменная {name} "
            "должна быть больше нуля."
        )

    return value

def get_current_time(
    now: datetime | None,
) -> datetime:
    current_time = (
        now
        if now is not None
        else datetime.now(
            timezone.utc
        )
    )

    if current_time.utcoffset() is None:
        raise ValueError(
            "Время должно содержать "
            "часовой пояс."
        )

    return current_time.astimezone(timezone.utc)


def get_token_count(
    value,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        return 0

    return value

def reserve_ai_request(
    *,
    db: Session,
    user_id: int,
    project_id: int,
    feature: str,
    now: datetime | None = None,
) -> models.AIRequestLog:
    """
    Проверяет лимиты и резервирует один ИИ-запрос.

    Запись создаётся до обращения к LLM,
    поэтому параллельные запросы учитывают
    друг друга.
    """
    if feature not in AI_FEATURES:
        raise ValueError(
            "Неизвестная ИИ-функция."
        )

    current_time = get_current_time(
        now
    )

    minute_limit = (
        get_positive_int_setting(
            "AI_REQUESTS_PER_MINUTE",
            DEFAULT_AI_REQUESTS_PER_MINUTE,
        )
    )

    daily_limit = (
        get_positive_int_setting(
            "AI_REQUESTS_PER_24_HOURS",
            DEFAULT_AI_REQUESTS_PER_24_HOURS,
        )
    )

    user = (
        db.query(
            models.User
        )
        .filter(
            models.User.id
            == user_id
        )
        .with_for_update()
        .one_or_none()
    )

    if user is None:
        db.rollback()

        raise ValueError(
            "Пользователь не найден."
        )

    minute_start = (
        current_time
        - timedelta(
            minutes=1
        )
    )

    day_start = (
        current_time
        - timedelta(
            hours=24
        )
    )

    recent_requests = (
        db.query(
            models.AIRequestLog
        )
        .filter(
            models.AIRequestLog.user_id
            == user_id,
            models.AIRequestLog.created_at
            >= minute_start,
        )
        .count()
    )

    if (
        recent_requests
        >= minute_limit
    ):
        db.rollback()

        raise AIRequestLimitError(
            message=RATE_LIMIT_MESSAGE,
            scope="minute",
        )

    daily_requests = (
        db.query(
            models.AIRequestLog
        )
        .filter(
            models.AIRequestLog.user_id
            == user_id,
            models.AIRequestLog.created_at
            >= day_start,
        )
        .count()
    )

    if daily_requests >= daily_limit:
        db.rollback()

        raise AIRequestLimitError(
            message=DAILY_LIMIT_MESSAGE,
            scope="day",
        )

    request_log = models.AIRequestLog(
        user_id=user_id,
        project_id=project_id,
        feature=feature,
        status="started",
        input_tokens=0,
        output_tokens=0,
        reasoning_tokens=0,
        total_tokens=0,
        created_at=current_time,
    )

    db.add(
        request_log
    )

    db.commit()
    db.refresh(
        request_log
    )

    return request_log

def complete_ai_request(
    *,
    db: Session,
    request_log: models.AIRequestLog,
    usage: dict,
    now: datetime | None = None,
) -> models.AIRequestLog:
    """
    Завершает успешный ИИ-запрос
    и сохраняет фактическое использование.
    """
    if request_log.status != "started":
        raise ValueError(
            "ИИ-запрос уже завершён."
        )

    if not isinstance(
        usage,
        dict,
    ):
        raise ValueError(
            "Статистика токенов "
            "должна быть объектом."
        )

    completed_at = get_current_time(now)
    request_log.status = "completed"

    request_log.input_tokens = (
        get_token_count(
            usage.get(
                "input_tokens", request_log.input_tokens
            )
        )
    )

    request_log.output_tokens = (
        get_token_count(
            usage.get(
                "output_tokens", request_log.output_tokens
            )
        )
    )

    request_log.reasoning_tokens = (
        get_token_count(
            usage.get(
                "reasoning_tokens", request_log.reasoning_tokens
            )
        )
    )

    request_log.total_tokens = (
        get_token_count(
            usage.get(
                "total_tokens", request_log.total_tokens
            )
        )
    )

    request_log.completed_at = completed_at

    db.add(
        request_log
    )

    db.commit()
    db.refresh(
        request_log
    )

    return request_log


def fail_ai_request(
    *,
    db: Session,
    request_log: models.AIRequestLog,
    now: datetime | None = None,
) -> models.AIRequestLog:
    """
    Помечает зарезервированный запрос
    как завершившийся ошибкой.
    """
    if request_log.status != "started":
        raise ValueError(
            "ИИ-запрос уже завершён."
        )

    completed_at = get_current_time(now)
    request_log.status = "failed"

    request_log.completed_at = completed_at

    db.add(
        request_log
    )

    db.commit()
    db.refresh(
        request_log
    )

    return request_log

"""Application spend guard, not a mirror of the provider's billing balance.

Reserve a conservative upper bound BEFORE HTTP; settle only trustworthy usage.
Unknown outcomes retain their reservation. The ledger survives user deletion.
All amounts use integer micro-rubles (1 RUB = 1,000,000 units).
"""

import os
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from zoneinfo import ZoneInfo

from sqlalchemy import update

from app import models
from app.services.db_counters import insert_for

MICRORUB = 1_000_000
BUDGET_TIMEZONE = ZoneInfo("Europe/Moscow")
# MWS's 128K total context; reserve the full context for input, PLUS output.
# Deliberately conservative: no heuristic chars-to-tokens estimate is trusted.
INPUT_TOKEN_BOUND = 131_072
MAX_OUTPUT_TOKENS = 4_000
SUPPORTED_MODEL = "gpt-oss-120b"
_request_context = ContextVar("ai_budget_request", default=None)


class AIBudgetExceeded(RuntimeError):
    pass


class AIBudgetConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Pricing:
    provider: str
    model: str
    input_rate: Decimal
    output_rate: Decimal


def positive_decimal(name, default):
    try:
        value = Decimal(os.getenv(name, default))
        if not value.is_finite() or not 0 < value <= Decimal("1000000"):
            raise ValueError
        if value.as_tuple().exponent < -6:
            raise ValueError
        return value
    except (InvalidOperation, ValueError) as exc:
        raise AIBudgetConfigurationError(f"Некорректная настройка {name}.") from exc


def daily_limit_microrub():
    return int(positive_decimal("AI_DAILY_BUDGET_RUB", "100") * MICRORUB)


def get_pricing():
    if os.getenv("AI_ENABLED", "true").lower() != "true":
        raise AIBudgetConfigurationError("ИИ отключён администратором.")
    if os.getenv("VERCEL") == "1" and os.getenv("VERCEL_ENV") != "production":
        raise AIBudgetConfigurationError("Платный ИИ отключён в preview-развёртывании.")
    if os.getenv("AI_PRICING_CONFIRMED", "false").lower() != "true":
        raise AIBudgetConfigurationError("Тариф ИИ ещё не подтверждён администратором.")
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    model = os.getenv("LLM_MODEL", SUPPORTED_MODEL)
    if provider != "mws" or model != SUPPORTED_MODEL:
        raise AIBudgetConfigurationError("Для этой модели не настроена защита бюджета.")
    daily_limit_microrub()  # Fail closed on malformed budget configuration too.
    # Public MWS Model Hub prices including VAT, checked 2026-08-28.
    # Must be confirmed against the deployment/account before enabling paid AI.
    return Pricing(
        provider, model,
        positive_decimal("AI_INPUT_RUB_PER_MILLION", "13.42"),
        positive_decimal("AI_OUTPUT_RUB_PER_MILLION", "54.90"),
    )


def cost_microrub(input_tokens, output_tokens, input_rate, output_rate, *, upper=False):
    if upper:
        # MWS uses billing units of 100 tokens. Round each direction upward;
        # actual provider carry/rounding can make its invoice slightly lower.
        input_tokens = ((input_tokens + 99) // 100) * 100
        output_tokens = ((output_tokens + 99) // 100) * 100
    amount = input_tokens * input_rate + output_tokens * output_rate
    return int(amount.to_integral_value(rounding=ROUND_CEILING))


@contextmanager
def request_context(db, request_log):
    token = _request_context.set((db, request_log))
    try:
        yield
    finally:
        _request_context.reset(token)


def reserve_call(*, db, request_log, pricing, max_output_tokens, now=None):
    current = now or datetime.now(timezone.utc)
    if current.utcoffset() is None:
        raise ValueError("Требуется время с часовым поясом.")
    current = current.astimezone(timezone.utc)
    if (isinstance(max_output_tokens, bool) or not isinstance(max_output_tokens, int)
            or not 1 <= max_output_tokens <= MAX_OUTPUT_TOKENS):
        raise AIBudgetConfigurationError("Превышен предел длины ответа ИИ.")
    day = current.astimezone(BUDGET_TIMEZONE).date()
    reserved = cost_microrub(
        INPUT_TOKEN_BOUND, max_output_tokens, pricing.input_rate, pricing.output_rate,
        upper=True,
    )
    table = models.AIDailyBudget
    db.execute(insert_for(db, table).values(day=day, allocated_microrub=0)
               .on_conflict_do_nothing(index_elements=[table.day]))
    accepted = db.execute(
        update(table).where(
            table.day == day,
            table.allocated_microrub + reserved <= daily_limit_microrub(),
        ).values(allocated_microrub=table.allocated_microrub + reserved)
        .returning(table.day)
    ).scalar_one_or_none()
    if accepted is None:
        db.rollback()
        raise AIBudgetExceeded(
            "Общий дневной бюджет ИИ временно исчерпан. "
            "Попробуйте позже или после 00:00 по Москве. "
            "Работа с проектом вручную остаётся доступной."
        )
    call = models.AIProviderCall(
        request_log_id=request_log.id, budget_day=day,
        provider=pricing.provider, model=pricing.model,
        input_rub_per_million=pricing.input_rate,
        output_rub_per_million=pricing.output_rate,
        input_token_bound=INPUT_TOKEN_BOUND, output_token_bound=max_output_tokens,
        reserved_microrub=reserved, charged_microrub=reserved,
        status="reserved", created_at=current,
    )
    db.add(call)
    db.commit()  # Persist reservation and release the DB lock before HTTP.
    return call


@contextmanager
def metered_call(*, model, max_output_tokens):
    context = _request_context.get()
    if context is None:
        raise AIBudgetConfigurationError("Платный вызов требует журнала и бюджета.")
    db, request_log = context
    pricing = get_pricing()
    if model != pricing.model:
        raise AIBudgetConfigurationError("Модель не соответствует тарифу.")
    call = reserve_call(db=db, request_log=request_log, pricing=pricing,
                        max_output_tokens=max_output_tokens)
    call_id = call.id
    try:
        yield call
    finally:
        # A crash before this finally leaves 'reserved', with the same full
        # charge. Never release money on timeout, malformed/missing usage, etc.
        db.rollback()
        db.execute(update(models.AIProviderCall).where(
            models.AIProviderCall.id == call_id,
            models.AIProviderCall.status == "reserved",
        ).values(status="uncertain", completed_at=datetime.now(timezone.utc)))
        db.commit()


def record_usage(call, data):
    """Run immediately after JSON decoding, BEFORE validating model content."""
    db, request_log = _request_context.get()
    if not isinstance(data, dict):
        return
    if data.get("model", call.model) != call.model:
        raise AIBudgetConfigurationError("Провайдер вернул неожиданную модель.")
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return
    incoming = usage.get("prompt_tokens")
    outgoing = usage.get("completion_tokens")
    total = usage.get("total_tokens")
    details = usage.get("completion_tokens_details", {})
    if not isinstance(details, dict):
        return
    reasoning = details.get("reasoning_tokens", 0)
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 0
           for v in (incoming, outgoing, total, reasoning)):
        return
    if (incoming == 0 or total != incoming + outgoing or reasoning > outgoing
            or incoming > call.input_token_bound or outgoing > call.output_token_bound):
        # Cannot safely reconcile this response: keep the maximum reservation.
        return
    estimate = cost_microrub(incoming, outgoing,
                            call.input_rub_per_million, call.output_rub_per_million)
    charged = cost_microrub(incoming, outgoing,
                           call.input_rub_per_million, call.output_rub_per_million, upper=True)
    refund = call.reserved_microrub - charged
    updated = db.execute(update(models.AIProviderCall).where(
        models.AIProviderCall.id == call.id, models.AIProviderCall.status == "reserved",
    ).values(
        status="reported", estimated_microrub=estimate, charged_microrub=charged,
        input_tokens=incoming, output_tokens=outgoing, reasoning_tokens=reasoning,
        completed_at=datetime.now(timezone.utc),
    ).returning(models.AIProviderCall.id)).scalar_one_or_none()
    if updated is None:
        db.rollback()
        return  # Idempotent: a second settlement cannot free money twice.
    db.execute(update(models.AIDailyBudget).where(
        models.AIDailyBudget.day == call.budget_day,
    ).values(allocated_microrub=models.AIDailyBudget.allocated_microrub - refund))
    # Keep known tokens even if unsafe/invalid model content makes the route fail.
    request_log.input_tokens += incoming
    request_log.output_tokens += outgoing
    request_log.reasoning_tokens += reasoning
    request_log.total_tokens += total
    db.commit()

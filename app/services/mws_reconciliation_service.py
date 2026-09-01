"""Manual MWS invoice reconciliation; no console scraping or undocumented API."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from fastapi import HTTPException

from app import models


def _money(value, name):
    try:
        result = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise HTTPException(400, f"Некорректное значение: {name}.") from exc
    if not result.is_finite() or result < 0 or result.as_tuple().exponent < -6:
        raise HTTPException(400, f"Некорректное значение: {name}.")
    return result


def add_manual(db, *, period_start, period_end, input_tokens, output_tokens,
               actual_base_cost_rub, discount_or_grant_rub, amount_due_rub,
               application_estimated_cost_rub, source):
    if period_start.utcoffset() is None or period_end.utcoffset() is None or period_end <= period_start:
        raise HTTPException(400, "Некорректный период сверки.")
    if input_tokens < 0 or output_tokens < 0:
        raise HTTPException(400, "Количество токенов не может быть отрицательным.")
    source = source.strip()
    if not source or len(source) > 200:
        raise HTTPException(400, "Укажите источник данных MWS.")
    base = _money(actual_base_cost_rub, "базовая стоимость")
    grant = _money(discount_or_grant_rub, "скидка или грант")
    due = _money(amount_due_rub, "к оплате")
    estimated = _money(application_estimated_cost_rub, "расчётная стоимость")
    row = models.MWSBillingReconciliation(
        period_start=period_start.astimezone(timezone.utc),
        period_end=period_end.astimezone(timezone.utc),
        input_tokens=input_tokens, output_tokens=output_tokens,
        actual_base_cost_rub=base, discount_or_grant_rub=grant,
        amount_due_rub=due, application_estimated_cost_rub=estimated,
        deviation_rub=due - estimated, source=source,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

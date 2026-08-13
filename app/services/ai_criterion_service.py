import json

from app import models
from app.llm import service as llm_service


INSUFFICIENT_CONTEXT_MESSAGE = (
    "Недостаточно контекста для подготовки предложений. "
    "Конкретизируйте описание проекта."
)


def generate_criterion_suggestions(
    project: models.Project,
    alternatives: list[models.Alternative],
    existing_criteria: list[models.Criterion],
) -> dict:
    description = (
        project.description.strip()
        if project.description
        else ""
    )

    if not description:
        return {
            "status": "insufficient_context",
            "message": INSUFFICIENT_CONTEXT_MESSAGE,
            "items": [],
        }

    current_weight_percent = sum(
        criterion.weight
        for criterion in existing_criteria
    ) * 100

    remaining_weight = max(
        0.0,
        100.0 - current_weight_percent,
    )

    if remaining_weight < 0.1:
        return {
            "status": "no_weight_capacity",
            "message": (
                "Сумма установленных весов уже составляет 100%. "
                "Уменьшите существующие веса, чтобы добавить новые критерии."
            ),
            "items": [],
        }

    existing_data = [
        {
            "n": criterion.name,
            "w": round(
                criterion.weight * 100,
                1,
            ),
        }
        for criterion in existing_criteria
    ]

    alternative_names = [
        alternative.name
        for alternative in alternatives
    ]

    system_prompt = (
        "Ты помощник системы принятия решений. "
        "Предлагай дополнительные критерии сравнения. "
        "Не повторяй существующие критерии. "
        "Не задавай вопросов. "
        "Для каждого предложи начальный вес в процентах. "
        "Сумма новых весов не должна превышать доступный остаток. "
        "Ответ только JSON. "
        "Формат: "
        '{"s":"ok","i":[{"n":"критерий","w":20,'
        '"cr":"зачем критерий","wr":"почему такой вес"}]} '
        "или "
        '{"s":"insufficient"}. '
        "Не более 5 критериев. "
        "Название до 100 символов. "
        "Каждое обоснование до 180 символов."
    )

    user_prompt = (
        f"P:{project.name}\n"
        f"D:{description}\n"
        f"A:{json.dumps(alternative_names, ensure_ascii=False)}\n"
        f"C:{json.dumps(existing_data, ensure_ascii=False)}\n"
        f"R:{round(remaining_weight, 1)}"
    )

    response = llm_service.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_output_tokens=1000,
        temperature=0.2,
        json_mode=True,
    )

    try:
        data = json.loads(response.content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "LLM вернула некорректный JSON."
        ) from exc

    if data.get("s") == "insufficient":
        return {
            "status": "insufficient_context",
            "message": INSUFFICIENT_CONTEXT_MESSAGE,
            "items": [],
        }

    raw_items = data.get("i")

    if not isinstance(raw_items, list):
        raise RuntimeError(
            "LLM вернула ответ неожиданного формата."
        )

    existing_normalized = {
        criterion.name.strip().casefold()
        for criterion in existing_criteria
    }

    items = []
    seen = set()

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        name = str(
            item.get("n", "")
        ).strip()

        criterion_explanation = str(
            item.get("cr", "")
        ).strip()

        weight_explanation = str(
            item.get("wr", "")
        ).strip()

        try:
            weight_percent = float(
                item.get("w")
            )
        except (TypeError, ValueError):
            continue

        normalized_name = name.casefold()

        if (
            not name
            or not criterion_explanation
            or not weight_explanation
            or normalized_name in existing_normalized
            or normalized_name in seen
            or weight_percent < 0
            or weight_percent > 100
        ):
            continue

        seen.add(normalized_name)

        items.append(
            {
                "name": name[:100],
                "weight_percent": round(
                    weight_percent,
                    1,
                ),
                "criterion_explanation": (
                    criterion_explanation[:180]
                ),
                "weight_explanation": (
                    weight_explanation[:180]
                ),
            }
        )

    return {
        "status": "ok",
        "items": items[:5],
        "remaining_weight_percent": round(
            remaining_weight,
            1,
        ),
        "usage": {
            "provider": response.provider,
            "model": response.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "reasoning_tokens": (
                response.usage.reasoning_tokens
            ),
            "total_tokens": response.usage.total_tokens,
        },
    }
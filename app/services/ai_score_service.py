import json

from app import models
from app.llm import service as llm_service


INSUFFICIENT_CONTEXT_MESSAGE = (
    "Недостаточно контекста для подготовки оценок. "
    "Конкретизируйте описание проекта."
)


def generate_score_suggestions(
    project: models.Project,
    alternatives: list[models.Alternative],
    criteria: list[models.Criterion],
) -> dict:
    description = (
        project.description.strip()
        if project.description
        else ""
    )

    if not description:
        return {
            "status":
                "insufficient_context",
            "message":
                INSUFFICIENT_CONTEXT_MESSAGE,
            "items": [],
        }

    if not alternatives or not criteria:
        return {
            "status": "empty_matrix",
            "message": (
                "Для оценки нужны хотя бы "
                "одна альтернатива "
                "и один критерий."
            ),
            "items": [],
        }

    alternatives_data = [
        {
            "id": alternative.id,
            "n": alternative.name,
        }
        for alternative in alternatives
    ]

    criteria_data = [
        {
            "id": criterion.id,
            "n": criterion.name,
        }
        for criterion in criteria
    ]

    system_prompt = (
        "Ты помощник системы принятия решений. "
        "Независимо оцени каждую альтернативу "
        "по каждому критерию по шкале 0–10. "
        "Не задавай вопросов. "
        "Не используй веса критериев при выставлении оценки. "
        "Оценивай только соответствие альтернативы критерию "
        "с учётом описания проекта и собственных общих знаний. "
        "Ответ только JSON. "
        "Формат: "
        '{"s":"ok","i":['
        '{"a":1,"c":2,"v":7.5,"r":"обоснование"}'
        "]}. "
        "v от 0 до 10. "
        "Обоснование до 180 символов. "
        "Верни оценку для каждой пары "
        "альтернатива-критерий."
    )

    user_prompt = (
        f"P:{project.name}\n"
        f"D:{description}\n"
        f"A:{json.dumps(alternatives_data, ensure_ascii=False)}\n"
        f"C:{json.dumps(criteria_data, ensure_ascii=False)}"
    )

    expected_pairs = {
        (
            alternative.id,
            criterion.id,
        )
        for alternative in alternatives
        for criterion in criteria
    }

    # Чем больше матрица, тем больше нужен ответ.
    max_output_tokens = min(
        4000,
        max(
            700,
            len(expected_pairs) * 90,
        ),
    )

    response = llm_service.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_output_tokens=max_output_tokens,
        temperature=0.2,
        json_mode=True,
    )

    try:
        data = json.loads(
            response.content
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "LLM вернула некорректный JSON."
        ) from exc

    raw_items = data.get("i")

    if not isinstance(raw_items, list):
        raise RuntimeError(
            "LLM вернула ответ неожиданного формата."
        )

    items = []
    seen_pairs = set()

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        try:
            alternative_id = int(
                item.get("a")
            )

            criterion_id = int(
                item.get("c")
            )

            ai_value = float(
                item.get("v")
            )

        except (TypeError, ValueError):
            continue

        explanation = str(
            item.get("r", "")
        ).strip()

        pair = (
            alternative_id,
            criterion_id,
        )

        if (
            pair not in expected_pairs
            or pair in seen_pairs
            or ai_value < 0
            or ai_value > 10
            or not explanation
        ):
            continue

        seen_pairs.add(pair)

        items.append(
            {
                "alternative_id":
                    alternative_id,
                "criterion_id":
                    criterion_id,
                "ai_value":
                    round(ai_value, 1),
                "ai_explanation":
                    explanation[:180],
            }
        )

    if not items:
        raise RuntimeError(
            "LLM не вернула допустимых оценок."
        )

    return {
        "status": "ok",
        "items": items,
        "usage": {
            "provider":
                response.provider,
            "model":
                response.model,
            "input_tokens":
                response.usage.input_tokens,
            "output_tokens":
                response.usage.output_tokens,
            "reasoning_tokens":
                response.usage.reasoning_tokens,
            "total_tokens":
                response.usage.total_tokens,
        },
    }
import json

from app import models
from app.llm import service as llm_service
from app.llm.safety import unsafe_response


def generate_result_explanation(
    *,
    project: models.Project,
    alternatives: list[models.Alternative],
    criteria: list[models.Criterion],
    scores: dict,
    results: list[dict],
    score_summary: dict,
) -> dict:
    description = (
        project.description.strip()
        if project.description
        else ""
    )

    if not description:
        return {
            "status": "insufficient_context",
            "message": (
                "Недостаточно контекста для объяснения результата. "
                "Конкретизируйте описание проекта."
            ),
        }

    if not results:
        return {
            "status": "no_results",
            "message": (
                "Сначала заполните матрицу оценок."
            ),
        }

    if score_summary["empty"] > 0:
        return {
            "status": "incomplete_matrix",
            "message": (
                "Для корректного объяснения сначала "
                "заполните все ячейки матрицы."
            ),
        }

    criteria_by_id = {
        criterion.id: criterion
        for criterion in criteria
    }

    result_data = []

    for rank, result in enumerate(
        results,
        start=1,
    ):
        alternative = result["alternative"]

        factors = []

        for criterion in criteria:
            score = scores.get(
                (
                    alternative.id,
                    criterion.id,
                )
            )

            if score is None:
                continue

            effective_value = (
                score.value
                if score.value is not None
                else score.ai_value
            )

            if effective_value is None:
                continue

            source = (
                "confirmed"
                if score.value is not None
                else "ai"
            )

            factors.append(
                {
                    "c": criterion.name,
                    "w": round(
                        criterion.weight * 100,
                        1,
                    ),
                    "v": round(
                        effective_value,
                        1,
                    ),
                    "k": result[
                        "contributions"
                    ].get(
                        criterion.id,
                        0,
                    ),
                    "s": source,
                }
            )

        result_data.append(
            {
                "rank": rank,
                "name": alternative.name,
                "total": result["total"],
                "factors": factors,
            }
        )

    system_prompt = (
        "Ты аналитический помощник системы принятия решений. "
        "Рейтинг и математические результаты уже рассчитаны "
        "программой и являются источником истины. "
        "Не пересчитывай баллы, не меняй места альтернатив "
        "и не объявляй другого победителя. "
        "Объясни, почему получился именно такой результат. "
        "Используй только переданные данные матрицы. "
        "Не придумывай внешние факты об альтернативах. "
        "Выдели главные факторы результата, сильные и слабые "
        "стороны лидера и ближайшего конкурента. "
        "Если оценки ИИ ещё не подтверждены, явно укажи, "
        "что результат предварительный. "
        "Пиши кратко и конкретно. "
        "Ответ только JSON в формате: "
        "{"
        '"summary":"общий вывод",'
        '"factors":["фактор 1","фактор 2"],'
        '"strengths":["сильная сторона"],'
        '"weaknesses":["слабая сторона"],'
        '"competitor":"сравнение с ближайшим конкурентом",'
        '"caveat":"оговорка или пустая строка"'
        "}."
    )

    user_prompt = (
        f"P:{project.name}\n"
        f"D:{description}\n"
        f"M:{json.dumps(result_data, ensure_ascii=False)}\n"
        "Q:"
        + json.dumps(
            {
                "confirmed":
                    score_summary["confirmed"],
                "ai_only":
                    score_summary["ai_only"],
                "total":
                    score_summary["total"],
            },
            ensure_ascii=False,
        )
    )

    response = llm_service.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_output_tokens=900,
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

    if not isinstance(data, dict):
        raise RuntimeError(
            "LLM вернула ответ неожиданного формата."
        )

    if data.get("s") == "unsafe":
        return unsafe_response()

    summary = str(
        data.get("summary", "")
    ).strip()

    competitor = str(
        data.get("competitor", "")
    ).strip()

    caveat = str(
        data.get("caveat", "")
    ).strip()

    factors = data.get(
        "factors",
        [],
    )

    strengths = data.get(
        "strengths",
        [],
    )

    weaknesses = data.get(
        "weaknesses",
        [],
    )

    if not summary:
        raise RuntimeError(
            "LLM не вернула объяснение результата."
        )

    def clean_list(
        values,
        *,
        limit: int,
    ) -> list[str]:
        if not isinstance(
            values,
            list,
        ):
            return []

        result = []

        for value in values:
            text = str(value).strip()

            if text:
                result.append(
                    text[:220]
                )

        return result[:limit]

    return {
        "status": "ok",
        "summary": summary[:600],
        "factors": clean_list(
            factors,
            limit=4,
        ),
        "strengths": clean_list(
            strengths,
            limit=3,
        ),
        "weaknesses": clean_list(
            weaknesses,
            limit=3,
        ),
        "competitor": competitor[:500],
        "caveat": caveat[:400],
        "preliminary": (
            score_summary[
                "has_unconfirmed_ai"
            ]
        ),
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
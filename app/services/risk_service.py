def analyze_decision_risks(
    *,
    criteria,
    results: list[dict],
    score_summary: dict,
) -> dict:
    risks = []

    total_weight = sum(
        criterion.weight
        for criterion in criteria
    )

    total_weight_percent = round(
        total_weight * 100,
        1,
    )

    if (
        criteria
        and total_weight < 0.999
    ):
        risks.append(
            {
                "code": "weights_incomplete",
                "level": "warning",
                "title": (
                    "Сумма весов меньше 100%"
                ),
                "message": (
                    "Сейчас сумма весов критериев "
                    f"составляет {total_weight_percent}%. "
                    "Итоговые баллы могут быть "
                    "сложнее интерпретировать."
                ),
            }
        )

    heavy_criteria = [
        criterion
        for criterion in criteria
        if criterion.weight >= 0.4
    ]

    for criterion in heavy_criteria:
        risks.append(
            {
                "code": "weight_concentration",
                "level": "warning",
                "title": (
                    "Высокая зависимость "
                    "от одного критерия"
                ),
                "message": (
                    f"Критерий «{criterion.name}» "
                    "имеет вес "
                    f"{round(criterion.weight * 100, 1)}%. "
                    "Небольшое изменение его оценки "
                    "может заметно повлиять на итог."
                ),
            }
        )

    if len(results) >= 2:
        leader = results[0]
        runner_up = results[1]

        gap = round(
            leader["total"]
            - runner_up["total"],
            2,
        )

        if gap <= 0.5:
            risks.append(
                {
                    "code": "narrow_lead",
                    "level": "warning",
                    "title": (
                        "Небольшой отрыв лидера"
                    ),
                    "message": (
                        f"Разница между «"
                        f"{leader['alternative'].name}» "
                        f"и «"
                        f"{runner_up['alternative'].name}» "
                        f"составляет всего {gap} балла. "
                        "Результат может измениться "
                        "при небольших корректировках "
                        "весов или оценок."
                    ),
                }
            )

    if score_summary[
        "ai_only"
    ] > 0:
        risks.append(
            {
                "code": "unconfirmed_ai_scores",
                "level": "warning",
                "title": (
                    "Есть неподтверждённые "
                    "оценки ИИ"
                ),
                "message": (
                    "В расчёте участвуют "
                    f"{score_summary['ai_only']} "
                    "оценок ИИ, которые ещё "
                    "не подтверждены пользователем."
                ),
            }
        )

    if score_summary[
        "empty"
    ] > 0:
        risks.append(
            {
                "code": "incomplete_matrix",
                "level": "danger",
                "title": (
                    "Матрица заполнена "
                    "не полностью"
                ),
                "message": (
                    "Не заполнено "
                    f"{score_summary['empty']} "
                    "ячеек. Итоговый рейтинг "
                    "нельзя считать устойчивым."
                ),
            }
        )

    return {
        "risks": risks,
        "count": len(risks),
        "has_risks": bool(risks),
        "total_weight_percent": (
            total_weight_percent
        ),
    }
from sqlalchemy.orm import Session

from app.models import Score


def get_score(
    db: Session,
    alternative_id: int,
    criterion_id: int,
) -> Score | None:
    return (
        db.query(Score)
        .filter(
            Score.alternative_id
            == alternative_id,
            Score.criterion_id
            == criterion_id,
        )
        .first()
    )


def set_score(
    db: Session,
    alternative_id: int,
    criterion_id: int,
    value: float,
) -> Score:
    """
    Сохраняет подтверждённую пользователем оценку.

    AI-метаданные при этом не удаляются:
    они остаются доступны для сравнения.
    """

    score = get_score(
        db=db,
        alternative_id=alternative_id,
        criterion_id=criterion_id,
    )

    if score is None:
        score = Score(
            alternative_id=alternative_id,
            criterion_id=criterion_id,
            value=value,
        )

        db.add(score)

    else:
        score.value = value

    db.commit()
    db.refresh(score)

    return score


def set_ai_score(
    db: Session,
    alternative_id: int,
    criterion_id: int,
    ai_value: float,
    ai_explanation: str,
) -> Score:
    """
    Сохраняет новое независимое предложение ИИ.

    Подтверждённое value никогда не меняется.
    Старое ai_value заменяется новым.
    """

    score = get_score(
        db=db,
        alternative_id=alternative_id,
        criterion_id=criterion_id,
    )

    if score is None:
        score = Score(
            alternative_id=alternative_id,
            criterion_id=criterion_id,
            value=None,
            ai_value=ai_value,
            ai_explanation=ai_explanation.strip(),
        )

        db.add(score)

    else:
        score.ai_value = ai_value
        score.ai_explanation = (
            ai_explanation.strip()
        )

    db.commit()
    db.refresh(score)

    return score


def set_ai_scores(
    db: Session,
    suggestions: list[dict],
) -> int:
    """
    Сохраняет пакет AI-оценок одной транзакцией.
    """

    updated = 0

    for suggestion in suggestions:
        score = get_score(
            db=db,
            alternative_id=(
                suggestion["alternative_id"]
            ),
            criterion_id=(
                suggestion["criterion_id"]
            ),
        )

        if score is None:
            score = Score(
                alternative_id=(
                    suggestion["alternative_id"]
                ),
                criterion_id=(
                    suggestion["criterion_id"]
                ),
                value=None,
            )

            db.add(score)

        score.ai_value = (
            suggestion["ai_value"]
        )

        score.ai_explanation = (
            suggestion[
                "ai_explanation"
            ].strip()
        )

        updated += 1

    db.commit()

    return updated


def get_scores(
    db: Session,
    project_id: int,
) -> dict[tuple[int, int], Score]:
    scores = (
        db.query(Score)
        .join(Score.alternative)
        .filter_by(
            project_id=project_id
        )
        .all()
    )

    return {
        (
            score.alternative_id,
            score.criterion_id,
        ): score
        for score in scores
    }

def get_score_summary(
    *,
    scores: dict[tuple[int, int], Score],
    alternatives_count: int,
    criteria_count: int,
) -> dict:
    """
    Возвращает состояние заполнения матрицы.

    confirmed:
        есть сохранённое value.

    ai_only:
        value отсутствует, но есть ai_value.

    empty:
        нет ни value, ни ai_value.
    """

    total_cells = (
        alternatives_count
        * criteria_count
    )

    confirmed = 0
    ai_only = 0

    for score in scores.values():
        if score.value is not None:
            confirmed += 1

        elif score.ai_value is not None:
            ai_only += 1

    filled = confirmed + ai_only

    empty = max(
        0,
        total_cells - filled,
    )

    confirmed_percent = (
        round(
            confirmed
            / total_cells
            * 100,
            1,
        )
        if total_cells
        else 0.0
    )

    return {
        "total": total_cells,
        "confirmed": confirmed,
        "ai_only": ai_only,
        "empty": empty,
        "confirmed_percent": (
            confirmed_percent
        ),
        "has_unconfirmed_ai": (
            ai_only > 0
        ),
        "is_complete": (
            total_cells > 0
            and empty == 0
        ),
        "is_fully_confirmed": (
            total_cells > 0
            and confirmed
            == total_cells
        ),
    }
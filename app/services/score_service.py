import math
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alternative, Criterion, Project, Score

from app.services.project_ai_analysis_service import (
    invalidate_analysis,
)


class MatrixSaveError(ValueError):
    def __init__(self, message, status=422, field=None):
        super().__init__(message)
        self.status = status
        self.field = field


def matrix_version(db, project_id):
    return db.scalar(select(Project.matrix_revision).where(Project.id == project_id))


def save_matrix(db, project_id, form, expected_revision, request_key=None):
    """Validate everything, lock the project, save once. No model calls."""
    project = db.query(Project).filter_by(id=project_id).populate_existing().with_for_update().one()
    if request_key and project.last_matrix_save_key == request_key:
        return project.matrix_revision
    try:
        expected_revision = int(expected_revision)
    except (TypeError, ValueError):
        raise MatrixSaveError("Откройте актуальную матрицу перед сохранением.", 409)
    if project.matrix_revision != expected_revision:
        raise MatrixSaveError("Матрица уже изменилась в другой вкладке или после ИИ-запроса. Ввод сохранён на экране. Сверьте его с актуальной версией перед повторным сохранением.", 409)
    alternatives = set(db.scalars(select(Alternative.id).where(Alternative.project_id == project_id)))
    criteria = set(db.scalars(select(Criterion.id).where(Criterion.project_id == project_id)))
    updates = {}
    for name, raw in form.items():
        if not name.startswith("score_"):
            continue
        try:
            _, a, c = name.split("_")
            pair = (int(a), int(c))
            if pair[0] not in alternatives or pair[1] not in criteria:
                raise ValueError()
            value = None if str(raw).strip() == "" else float(raw)
            if value is not None and (not math.isfinite(value) or not 0 <= value <= 10):
                raise ValueError()
        except (ValueError, TypeError):
            raise MatrixSaveError("Оценка должна быть числом от 0 до 10 для существующей ячейки.", field=name if len(name) < 80 else None)
        updates[pair] = value
    scores = get_scores(db, project_id)
    changed = False
    for (a, c), value in updates.items():
        score = scores.get((a, c))
        if score is None:
            if value is None:
                continue
            db.add(Score(alternative_id=a, criterion_id=c, value=value))
        elif score.value != value:
            score.value = value
        else:
            continue
        changed = True
    if changed:
        invalidate_analysis(db, project_id)
    if request_key:
        project.last_matrix_save_key = request_key
    revision = project.matrix_revision
    db.commit()
    return revision

def _get_project_id_for_alternative(
    db: Session,
    alternative_id: int,
) -> int | None:
    alternative = db.get(
        Alternative,
        alternative_id,
    )

    if alternative is None:
        return None

    return alternative.project_id

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

    project_id = (
        _get_project_id_for_alternative(
            db=db,
            alternative_id=alternative_id,
        )
    )

    changed = (
        score is None
        or score.value != value
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

    if (
        changed
        and project_id is not None
    ):
        invalidate_analysis(
            db=db,
            project_id=project_id,
        )

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

    normalized_explanation = (
        ai_explanation.strip()
    )

    project_id = (
        _get_project_id_for_alternative(
            db=db,
            alternative_id=alternative_id,
        )
    )

    changed = (
        score is None
        or score.ai_value != ai_value
        or score.ai_explanation
        != normalized_explanation
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
            normalized_explanation
        )

    if (
        changed
        and project_id is not None
    ):
        invalidate_analysis(
            db=db,
            project_id=project_id,
        )

    db.commit()
    db.refresh(score)

    return score


def set_ai_scores(
    db: Session,
    suggestions: list[dict],
    *,
    commit: bool = True,
) -> int:
    """
    Сохраняет пакет AI-оценок одной транзакцией.
    """

    updated = 0

    changed_project_ids: set[int] = set()

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

        normalized_explanation = (
            suggestion[
                "ai_explanation"
            ].strip()
        )

        changed = (
            score is None
            or score.ai_value
            != suggestion["ai_value"]
            or score.ai_explanation
            != normalized_explanation
        )

        if changed:
            project_id = (
                _get_project_id_for_alternative(
                    db=db,
                    alternative_id=(
                        suggestion[
                            "alternative_id"
                        ]
                    ),
                )
            )

            if project_id is not None:
                changed_project_ids.add(
                    project_id
                )

        score.ai_value = (
            suggestion["ai_value"]
        )

        score.ai_explanation = (
            normalized_explanation
        )

        updated += 1

    for project_id in changed_project_ids:
        invalidate_analysis(
            db=db,
            project_id=project_id,
        )

    if commit:
        db.commit()
    else:
        db.flush()

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

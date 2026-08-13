from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_criteria(
    db: Session,
    project_id: int,
):
    statement = (
        select(models.Criterion)
        .where(
            models.Criterion.project_id
            == project_id
        )
        .order_by(models.Criterion.id)
    )

    return list(
        db.scalars(statement)
    )


def _validate_total_weight(
    *,
    existing_weight: float,
    new_weight: float,
):
    if new_weight < 0 or new_weight > 1:
        raise ValueError(
            "Вес должен быть от 0 до 100 процентов"
        )

    if (
        existing_weight + new_weight
        > 1.000001
    ):
        raise ValueError(
            "Сумма весов критериев "
            "не может превышать 100%"
        )


def create_criterion(
    db: Session,
    project_id: int,
    name: str,
    weight_percent: float,
):
    criteria = get_criteria(
        db,
        project_id,
    )

    current_total_weight = sum(
        criterion.weight
        for criterion in criteria
    )

    new_weight = (
        weight_percent / 100
    )

    _validate_total_weight(
        existing_weight=current_total_weight,
        new_weight=new_weight,
    )

    criterion = models.Criterion(
        name=name.strip(),
        weight=new_weight,
        project_id=project_id,
    )

    db.add(criterion)
    db.commit()
    db.refresh(criterion)

    return criterion


def create_ai_criteria(
    db: Session,
    project_id: int,
    suggestions: list[dict],
) -> list[models.Criterion]:
    existing_criteria = get_criteria(
        db,
        project_id,
    )

    existing_names = {
        criterion.name.strip().casefold()
        for criterion in existing_criteria
    }

    current_total_weight = sum(
        criterion.weight
        for criterion in existing_criteria
    )

    prepared = []

    for suggestion in suggestions:
        name = suggestion[
            "name"
        ].strip()

        normalized_name = (
            name.casefold()
        )

        if (
            not name
            or normalized_name
            in existing_names
        ):
            continue

        weight_percent = float(
            suggestion["weight_percent"]
        )

        ai_weight_percent = float(
            suggestion[
                "ai_suggested_weight_percent"
            ]
        )

        if (
            weight_percent < 0
            or weight_percent > 100
            or ai_weight_percent < 0
            or ai_weight_percent > 100
        ):
            raise ValueError(
                "Вес должен быть "
                "от 0 до 100 процентов"
            )

        prepared.append(
            {
                **suggestion,
                "name": name,
                "weight": (
                    weight_percent / 100
                ),
                "ai_weight": (
                    ai_weight_percent / 100
                ),
            }
        )

        existing_names.add(
            normalized_name
        )

    new_total_weight = sum(
        item["weight"]
        for item in prepared
    )

    _validate_total_weight(
        existing_weight=current_total_weight,
        new_weight=new_total_weight,
    )

    created = []

    for item in prepared:
        criterion = models.Criterion(
            name=item["name"],
            weight=item["weight"],
            ai_suggested_name=(
                item["name"]
            ),
            ai_suggested_weight=(
                item["ai_weight"]
            ),
            ai_criterion_explanation=(
                item[
                    "criterion_explanation"
                ].strip()
            ),
            ai_weight_explanation=(
                item[
                    "weight_explanation"
                ].strip()
            ),
            project_id=project_id,
        )

        db.add(criterion)
        created.append(criterion)

    db.commit()

    for criterion in created:
        db.refresh(criterion)

    return created


def delete_criterion(
    db: Session,
    criterion_id: int,
):
    criterion = db.get(
        models.Criterion,
        criterion_id,
    )

    if criterion is None:
        return

    db.delete(criterion)
    db.commit()


def update_criterion(
    db: Session,
    criterion_id: int,
    name: str,
    weight_percent: float,
):
    criterion = db.get(
        models.Criterion,
        criterion_id,
    )

    if criterion is None:
        return None

    other_criteria = (
        select(models.Criterion)
        .where(
            models.Criterion.project_id
            == criterion.project_id,
            models.Criterion.id
            != criterion.id,
        )
    )

    other_total_weight = sum(
        item.weight
        for item in db.scalars(
            other_criteria
        )
    )

    new_weight = (
        weight_percent / 100
    )

    _validate_total_weight(
        existing_weight=other_total_weight,
        new_weight=new_weight,
    )

    criterion.name = name.strip()
    criterion.weight = new_weight

    db.commit()
    db.refresh(criterion)

    return criterion
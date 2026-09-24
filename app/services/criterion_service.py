from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models

from app.services.project_ai_analysis_service import (
    invalidate_analysis,
)

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
    if existing_weight + new_weight > 1.000001:
        raise ValueError(
            "Сумма весов критериев не может превышать 100%"
        )


IMPORTANCE_SHARES = {
    "critical": 0.60,
    "important": 0.30,
    "desirable": 0.10,
}


def importance_level(weight: float, maximum_weight: float) -> str:
    """Fallback for rows created before the importance migration."""
    if maximum_weight <= 0 or weight <= 0:
        return "important"
    if weight >= 0.35:
        return "critical"
    if weight >= 0.15:
        return "important"
    return "desirable"


def _validate_importance(importance: str) -> str:
    # Compatibility with the previous UI, which called the top level "very".
    if importance == "very":
        importance = "critical"
    if importance not in IMPORTANCE_SHARES:
        raise ValueError("Неизвестный уровень важности")
    return importance


def _renormalize_importance(criteria: list[models.Criterion]) -> None:
    """Distribute 60/30/10 between present groups and always total 100%."""
    if not criteria:
        return
    grouped = {
        key: [item for item in criteria if item.importance == key]
        for key in IMPORTANCE_SHARES
    }
    active_share = sum(
        IMPORTANCE_SHARES[key]
        for key, items in grouped.items()
        if items
    )
    if active_share <= 0:
        for item in criteria:
            item.importance = "important"
        grouped["important"] = list(criteria)
        active_share = IMPORTANCE_SHARES["important"]
    for key, items in grouped.items():
        if not items:
            continue
        group_weight = IMPORTANCE_SHARES[key] / active_share
        item_weight = group_weight / len(items)
        for item in items:
            item.weight = item_weight
    # Keep the stored sum exactly one despite floating-point accumulation.
    criteria[-1].weight += 1.0 - sum(item.weight for item in criteria)


def normalize_project_importance(db: Session, project_id: int) -> None:
    criteria = get_criteria(db, project_id)
    _renormalize_importance(criteria)


def create_simple_criterion(
    db: Session,
    project_id: int,
    name: str,
    importance: str,
):
    importance = _validate_importance(importance)
    criteria = get_criteria(db, project_id)
    criterion = models.Criterion(
        name=name.strip(),
        weight=0.0,
        importance=importance,
        project_id=project_id,
    )
    db.add(criterion)
    db.flush()
    criteria.append(criterion)
    _renormalize_importance(criteria)
    invalidate_analysis(db=db, project_id=project_id)
    db.commit()
    db.refresh(criterion)
    return criterion


def set_simple_importance(
    db: Session,
    criterion: models.Criterion,
    importance: str,
):
    importance = _validate_importance(importance)
    criteria = get_criteria(db, criterion.project_id)
    criterion.importance = importance
    _renormalize_importance(criteria)
    invalidate_analysis(db=db, project_id=criterion.project_id)
    db.commit()


def create_criterion(
    db: Session,
    project_id: int,
    name: str,
    weight_percent: float,
):
    importance = (
        "critical" if weight_percent >= 35
        else "important" if weight_percent >= 15
        else "desirable"
    )
    return create_simple_criterion(db, project_id, name, importance)


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

        importance = suggestion.get("importance")
        if importance is None:
            legacy_weight = float(suggestion.get("weight_percent", 20))
            importance = (
                "critical" if legacy_weight >= 35
                else "important" if legacy_weight >= 15
                else "desirable"
            )
        importance = _validate_importance(str(importance))

        prepared.append(
            {
                **suggestion,
                "name": name,
                "importance": importance,
            }
        )

        existing_names.add(
            normalized_name
        )

    created = []

    for item in prepared:
        criterion = models.Criterion(
            name=item["name"],
            weight=0.0,
            importance=item["importance"],
            ai_suggested_name=(
                item["name"]
            ),
            ai_suggested_weight=(
                float(item["ai_suggested_weight_percent"]) / 100
                if item.get("ai_suggested_weight_percent") is not None
                else None
            ),
            ai_criterion_explanation=(
                item[
                    "criterion_explanation"
                ].strip()
            ),
            ai_weight_explanation=(
                str(item.get("weight_explanation", "")).strip()
            ),
            project_id=project_id,
        )

        db.add(criterion)
        created.append(criterion)

    if created:
        db.flush()
        _renormalize_importance(existing_criteria + created)
        invalidate_analysis(
            db=db,
            project_id=project_id,
        )

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

    project_id = criterion.project_id

    db.delete(criterion)
    db.flush()
    _renormalize_importance(get_criteria(db, project_id))

    invalidate_analysis(
        db=db,
        project_id=project_id,
    )

    db.commit()


def delete_criteria(
    db: Session,
    project_id: int,
    criterion_ids: list[int],
) -> int:
    selected = set(criterion_ids)
    if not selected:
        return 0
    criteria = list(db.scalars(select(models.Criterion).where(
        models.Criterion.project_id == project_id,
        models.Criterion.id.in_(selected),
    )))
    for criterion in criteria:
        db.delete(criterion)
    if criteria:
        db.flush()
        _renormalize_importance(get_criteria(db, project_id))
        invalidate_analysis(db=db, project_id=project_id)
        db.commit()
    return len(criteria)


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

    normalized_name = name.strip()

    importance = (
        "critical" if weight_percent >= 35
        else "important" if weight_percent >= 15
        else "desirable"
    )
    changed = (
        criterion.name != normalized_name
        or criterion.importance != importance
    )

    criterion.name = normalized_name
    criterion.importance = importance

    if changed:
        _renormalize_importance(
            get_criteria(db, criterion.project_id)
        )
        invalidate_analysis(
            db=db,
            project_id=criterion.project_id,
        )

    db.commit()
    db.refresh(criterion)

    return criterion

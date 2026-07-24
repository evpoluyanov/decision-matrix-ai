from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_criteria(db: Session, project_id: int):
    statement = (
        select(models.Criterion)
        .where(models.Criterion.project_id == project_id)
        .order_by(models.Criterion.id)
    )

    return list(db.scalars(statement))


def create_criterion(
    db: Session,
    project_id: int,
    name: str,
    weight_percent: float,
):
    if weight_percent < 0 or weight_percent > 100:
        raise ValueError("Вес должен быть от 0 до 100 процентов")

    criteria = get_criteria(db, project_id)

    current_total_weight = sum(
        criterion.weight for criterion in criteria
    )

    new_weight = weight_percent / 100

    if current_total_weight + new_weight > 1.000001:
        raise ValueError(
            "Сумма весов критериев не может превышать 100%"
        )

    criterion = models.Criterion(
        name=name,
        weight=new_weight,
        project_id=project_id,
    )

    db.add(criterion)
    db.commit()
    db.refresh(criterion)

    return criterion
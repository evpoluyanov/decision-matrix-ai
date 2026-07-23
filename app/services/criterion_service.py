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
):
    criterion = models.Criterion(
        name=name,
        project_id=project_id,
    )

    db.add(criterion)
    db.commit()
    db.refresh(criterion)

    return criterion
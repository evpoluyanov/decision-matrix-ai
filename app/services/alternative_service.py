from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_alternatives(db: Session, project_id: int):
    statement = (
        select(models.Alternative)
        .where(models.Alternative.project_id == project_id)
        .order_by(models.Alternative.id)
    )

    return list(db.scalars(statement))


def create_alternative(
    db: Session,
    project_id: int,
    name: str,
):
    alternative = models.Alternative(
        name=name,
        project_id=project_id,
    )

    db.add(alternative)
    db.commit()
    db.refresh(alternative)

    return alternative
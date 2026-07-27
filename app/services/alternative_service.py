from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.models import Alternative

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


def delete_alternative(
    db: Session,
    alternative_id: int,
):
    alternative = db.get(
        models.Alternative,
        alternative_id,
    )

    if alternative is None:
        return

    db.delete(alternative)
    db.commit()


def update_alternative(
    db: Session,
    alternative_id: int,
    name: str,
):
    alternative = db.get(
        Alternative,
        alternative_id,
    )

    if alternative is None:
        return None

    alternative.name = name.strip()

    db.commit()
    db.refresh(alternative)

    return alternative
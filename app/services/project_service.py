from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_projects(db: Session) -> list[models.Project]:
    statement = select(models.Project).order_by(models.Project.id)

    return list(db.scalars(statement).all())


def create_project(
    db: Session,
    project_name: str,
) -> models.Project:
    project = models.Project(name=project_name)

    db.add(project)
    db.commit()
    db.refresh(project)

    return project
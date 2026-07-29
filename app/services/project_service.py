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
    
def update_project(
    db: Session,
    project_id: int,
    project_name: str,
):
    project = db.get(
        models.Project,
        project_id,
    )

    if project is None:
        return None

    project.name = project_name.strip()

    db.commit()
    db.refresh(project)

    return project

def delete_project(
    db: Session,
    project_id: int,
) -> bool:
    project = db.get(
        models.Project,
        project_id,
    )

    if project is None:
        return False

    db.delete(project)
    db.commit()

    return True

def copy_project(
    db: Session,
    project_id: int,
):
    source_project = db.get(
        models.Project,
        project_id,
    )

    if source_project is None:
        return None

    new_project = models.Project(
        name=f"{source_project.name} (копия)",
    )

    db.add(new_project)
    db.flush()

    alternative_id_map = {}

    for source_alternative in source_project.alternatives:
        new_alternative = models.Alternative(
            name=source_alternative.name,
            project_id=new_project.id,
        )

        db.add(new_alternative)
        db.flush()

        alternative_id_map[source_alternative.id] = new_alternative.id

    criterion_id_map = {}

    for source_criterion in source_project.criteria:
        new_criterion = models.Criterion(
            name=source_criterion.name,
            weight=source_criterion.weight,
            project_id=new_project.id,
        )

        db.add(new_criterion)
        db.flush()

        criterion_id_map[source_criterion.id] = new_criterion.id

    for source_alternative in source_project.alternatives:
        for source_score in source_alternative.scores:
            new_score = models.Score(
                value=source_score.value,
                alternative_id=alternative_id_map[
                    source_score.alternative_id
                ],
                criterion_id=criterion_id_map[
                    source_score.criterion_id
                ],
            )

            db.add(new_score)

    db.commit()
    db.refresh(new_project)

    return new_project
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_project_for_owner(
    db: Session,
    project_id: int,
    owner_id: int,
) -> models.Project | None:
    """
    Возвращает проект только указанного владельца.
    """
    statement = select(models.Project).where(
        models.Project.id == project_id,
        models.Project.owner_id == owner_id,
    )

    return db.scalar(statement)


def get_projects(
    db: Session,
    owner_id: int,
) -> list[models.Project]:
    """
    Возвращает проекты конкретного пользователя.
    """
    statement = (
        select(models.Project)
        .where(models.Project.owner_id == owner_id)
        .order_by(models.Project.id)
    )

    return list(
        db.scalars(statement).all()
    )


def create_project(
    db: Session,
    project_name: str,
    owner_id: int,
) -> models.Project:
    """
    Создаёт проект и назначает ему владельца.
    """
    project = models.Project(
        name=project_name.strip(),
        owner_id=owner_id,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def update_project(
    db: Session,
    project: models.Project,
    project_name: str,
) -> models.Project:
    """
    Изменяет название уже проверенного проекта.
    """
    project.name = project_name.strip()

    db.commit()
    db.refresh(project)

    return project


def delete_project(
    db: Session,
    project: models.Project,
) -> None:
    """
    Удаляет уже проверенный проект.
    """
    db.delete(project)
    db.commit()


def copy_project(
    db: Session,
    source_project: models.Project,
) -> models.Project:
    """
    Создаёт полную копию проекта
    с тем же владельцем.
    """
    new_project = models.Project(
        name=f"{source_project.name} (копия)",
        owner_id=source_project.owner_id,
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

        alternative_id_map[
            source_alternative.id
        ] = new_alternative.id

    criterion_id_map = {}

    for source_criterion in source_project.criteria:
        new_criterion = models.Criterion(
            name=source_criterion.name,
            weight=source_criterion.weight,
            project_id=new_project.id,
        )

        db.add(new_criterion)
        db.flush()

        criterion_id_map[
            source_criterion.id
        ] = new_criterion.id

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
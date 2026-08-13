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
    project_description: str | None,
    owner_id: int,
) -> models.Project:
    """
    Создаёт проект и назначает ему владельца.
    """
    description = (
        project_description.strip()
        if project_description
        else None
    )

    if description == "":
        description = None

    project = models.Project(
        name=project_name.strip(),
        description=description,
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
    project_description: str | None,
) -> models.Project:
    """
    Изменяет название и описание
    уже проверенного проекта.
    """
    description = (
        project_description.strip()
        if project_description
        else None
    )

    if description == "":
        description = None

    project.name = project_name.strip()
    project.description = description

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
    с тем же владельцем и AI-метаданными.
    """
    new_project = models.Project(
        name=f"{source_project.name} (копия)",
        description=source_project.description,
        owner_id=source_project.owner_id,
    )

    db.add(new_project)
    db.flush()

    alternative_id_map = {}

    for source_alternative in source_project.alternatives:
        new_alternative = models.Alternative(
            name=source_alternative.name,
            ai_suggested_name=(
                source_alternative.ai_suggested_name
            ),
            ai_explanation=(
                source_alternative.ai_explanation
            ),
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
            ai_suggested_name=(
                source_criterion.ai_suggested_name
            ),
            ai_suggested_weight=(
                source_criterion.ai_suggested_weight
            ),
            ai_criterion_explanation=(
                source_criterion.ai_criterion_explanation
            ),
            ai_weight_explanation=(
                source_criterion.ai_weight_explanation
            ),
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
                ai_value=source_score.ai_value,
                ai_explanation=(
                    source_score.ai_explanation
                ),
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
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_alternatives(
    db: Session,
    project_id: int,
):
    statement = (
        select(models.Alternative)
        .where(
            models.Alternative.project_id
            == project_id
        )
        .order_by(models.Alternative.id)
    )

    return list(
        db.scalars(statement)
    )


def create_alternative(
    db: Session,
    project_id: int,
    name: str,
):
    """
    Создаёт альтернативу вручную.
    """
    alternative = models.Alternative(
        name=name.strip(),
        project_id=project_id,
    )

    db.add(alternative)
    db.commit()
    db.refresh(alternative)

    return alternative


def create_ai_alternatives(
    db: Session,
    project_id: int,
    suggestions: list[dict[str, str]],
) -> list[models.Alternative]:
    """
    Сохраняет выбранные пользователем
    предложения ИИ.
    """

    existing_names = {
        alternative.name.strip().casefold()
        for alternative in get_alternatives(
            db,
            project_id,
        )
    }

    created = []

    for suggestion in suggestions:
        name = suggestion["name"].strip()
        explanation = (
            suggestion["explanation"].strip()
        )

        normalized_name = name.casefold()

        if (
            not name
            or normalized_name
            in existing_names
        ):
            continue

        alternative = models.Alternative(
            name=name,
            ai_suggested_name=name,
            ai_explanation=explanation,
            project_id=project_id,
        )

        db.add(alternative)

        existing_names.add(
            normalized_name
        )

        created.append(
            alternative
        )

    db.commit()

    for alternative in created:
        db.refresh(alternative)

    return created


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
        models.Alternative,
        alternative_id,
    )

    if alternative is None:
        return None

    alternative.name = name.strip()

    db.commit()
    db.refresh(alternative)

    return alternative
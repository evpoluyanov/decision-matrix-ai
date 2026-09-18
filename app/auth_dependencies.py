from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.services import project_service, user_service


def require_user(
    request: Request,
    db: Session = Depends(get_db),
) -> models.User:
    """
    Возвращает текущего авторизованного пользователя.

    Если действующей пользовательской сессии нет,
    перенаправляет на страницу входа.
    """
    user_id = request.session.get("user_id")

    if not isinstance(user_id, int):
        request.session.clear()

        raise HTTPException(
            status_code=303,
            headers={"Location": "/login"},
        )

    user = user_service.get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        request.session.clear()

        raise HTTPException(
            status_code=303,
            headers={"Location": "/login"},
        )

    return user


def require_project_owner(
    project_id: int,
    current_user: models.User = Depends(require_user),
    db: Session = Depends(get_db),
) -> models.Project:
    """
    Возвращает проект только тогда, когда
    текущий пользователь является его владельцем.
    """
    project = project_service.get_project_for_owner(
        db=db,
        project_id=project_id,
        owner_id=current_user.id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Ресурс не найден",
        )

    return project


def require_alternative_owner(
    alternative_id: int,
    current_user: models.User = Depends(require_user),
    db: Session = Depends(get_db),
) -> models.Alternative:
    """
    Проверяет, что альтернатива относится
    к проекту текущего пользователя.
    """
    alternative = db.get(
        models.Alternative,
        alternative_id,
    )

    if alternative is None:
        raise HTTPException(
            status_code=404,
            detail="Ресурс не найден",
        )

    project = project_service.get_project_for_owner(
        db=db,
        project_id=alternative.project_id,
        owner_id=current_user.id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Ресурс не найден",
        )

    return alternative


def require_criterion_owner(
    criterion_id: int,
    current_user: models.User = Depends(require_user),
    db: Session = Depends(get_db),
) -> models.Criterion:
    """
    Проверяет, что критерий относится
    к проекту текущего пользователя.
    """
    criterion = db.get(
        models.Criterion,
        criterion_id,
    )

    if criterion is None:
        raise HTTPException(
            status_code=404,
            detail="Ресурс не найден",
        )

    project = project_service.get_project_for_owner(
        db=db,
        project_id=criterion.project_id,
        owner_id=current_user.id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Ресурс не найден",
        )

    return criterion
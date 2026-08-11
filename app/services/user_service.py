from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.security import hash_password


def get_user_by_email(
    db: Session,
    email: str,
) -> models.User | None:
    """
    Ищет пользователя по нормализованному email.
    """
    statement = select(models.User).where(
        models.User.email == email
    )

    return db.scalar(statement)


def create_user(
    db: Session,
    email: str,
    password: str,
) -> models.User | None:
    """
    Создаёт пользователя.

    Возвращает созданного пользователя или None,
    если такой email уже зарегистрирован.
    """
    existing_user = get_user_by_email(
        db=db,
        email=email,
    )

    if existing_user is not None:
        return None

    user = models.User(
        email=email,
        password_hash=hash_password(password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        # Уникальный индекс в самой базе дополнительно
        # защищает от одновременной регистрации одного email.
        db.rollback()
        return None

    db.refresh(user)

    return user
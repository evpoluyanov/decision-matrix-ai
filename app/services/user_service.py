from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.security import hash_password, verify_password


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


def get_user_by_id(
    db: Session,
    user_id: int,
) -> models.User | None:
    """
    Ищет пользователя по его идентификатору.
    """
    return db.get(
        models.User,
        user_id,
    )


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
        db.rollback()
        return None

    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> models.User | None:
    """
    Проверяет email и пароль пользователя.

    Возвращает пользователя при успешной проверке
    или None при неверных данных.
    """
    user = get_user_by_email(
        db=db,
        email=email,
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user

def change_password(
    db: Session,
    user: models.User,
    current_password: str,
    new_password: str,
) -> bool:
    """
    Меняет пароль только после проверки
    действующего пароля пользователя.
    """

    if not verify_password(
        current_password,
        user.password_hash,
    ):
        return False

    user.password_hash = hash_password(
        new_password
    )

    db.commit()
    db.refresh(user)

    return True
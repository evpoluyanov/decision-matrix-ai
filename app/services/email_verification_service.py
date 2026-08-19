import os

from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)


EMAIL_VERIFICATION_SALT = (
    "decision-matrix-email-verification"
)

EMAIL_VERIFICATION_TOKEN_MAX_AGE_SECONDS = (
    60 * 60 * 24
)


class EmailVerificationError(
    RuntimeError
):
    """Базовая ошибка подтверждения email."""


class EmailVerificationConfigurationError(
    EmailVerificationError
):
    """Ошибка конфигурации токенов."""


class EmailVerificationTokenError(
    EmailVerificationError
):
    """Некорректный токен подтверждения."""


class EmailVerificationTokenExpiredError(
    EmailVerificationTokenError
):
    """Срок действия токена истёк."""


def get_token_serializer(
) -> URLSafeTimedSerializer:
    """
    Создаёт сериализатор с секретным ключом
    приложения и отдельной солью.
    """
    session_secret = os.getenv(
        "SESSION_SECRET",
        "",
    ).strip()

    if not session_secret:
        raise (
            EmailVerificationConfigurationError(
                "Не задана переменная "
                "окружения SESSION_SECRET."
            )
        )

    return URLSafeTimedSerializer(
        secret_key=session_secret,
        salt=EMAIL_VERIFICATION_SALT,
    )


def create_email_verification_token(
    user_id: int,
) -> str:
    """
    Создаёт подписанный токен
    для идентификатора пользователя.
    """
    if (
        not isinstance(user_id, int)
        or isinstance(user_id, bool)
        or user_id <= 0
    ):
        raise ValueError(
            "Идентификатор пользователя "
            "должен быть положительным числом."
        )

    serializer = get_token_serializer()

    return serializer.dumps(
        {
            "user_id": user_id,
        }
    )


def verify_email_verification_token(
    token: str,
    max_age_seconds: int = (
        EMAIL_VERIFICATION_TOKEN_MAX_AGE_SECONDS
    ),
) -> int:
    """
    Проверяет подпись и срок действия токена.

    Возвращает идентификатор пользователя
    при успешной проверке.
    """
    token = token.strip()

    if not token:
        raise EmailVerificationTokenError(
            "Токен подтверждения отсутствует."
        )

    serializer = get_token_serializer()

    try:
        token_data = serializer.loads(
            token,
            max_age=max_age_seconds,
        )
    except SignatureExpired as error:
        raise (
            EmailVerificationTokenExpiredError(
                "Срок действия ссылки истёк."
            )
        ) from error
    except BadSignature as error:
        raise EmailVerificationTokenError(
            "Ссылка подтверждения некорректна."
        ) from error

    if not isinstance(
        token_data,
        dict,
    ):
        raise EmailVerificationTokenError(
            "Ссылка подтверждения "
            "содержит некорректные данные."
        )

    user_id = token_data.get(
        "user_id"
    )

    if (
        not isinstance(user_id, int)
        or isinstance(user_id, bool)
        or user_id <= 0
    ):
        raise EmailVerificationTokenError(
            "Ссылка подтверждения "
            "содержит некорректного пользователя."
        )

    return user_id
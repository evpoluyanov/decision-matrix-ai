import os
from html import escape

from urllib.parse import urlencode, urlparse

from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)

from app.services import email_service

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

def get_app_base_url() -> str:
    """
    Получает и проверяет публичный
    адрес приложения.
    """
    app_base_url = os.getenv(
        "APP_BASE_URL",
        "",
    ).strip()

    if not app_base_url:
        raise (
            EmailVerificationConfigurationError(
                "Не задана переменная "
                "окружения APP_BASE_URL."
            )
        )

    parsed_url = urlparse(
        app_base_url
    )

    if (
        parsed_url.scheme
        not in {
            "http",
            "https",
        }
        or not parsed_url.netloc
    ):
        raise (
            EmailVerificationConfigurationError(
                "APP_BASE_URL должен содержать "
                "полный адрес приложения."
            )
        )

    if (
        parsed_url.query
        or parsed_url.fragment
        or parsed_url.path
        not in {
            "",
            "/",
        }
    ):
        raise (
            EmailVerificationConfigurationError(
                "APP_BASE_URL не должен "
                "содержать путь, параметры "
                "или фрагмент."
            )
        )

    if (
        parsed_url.scheme == "http"
        and parsed_url.hostname
        not in {
            "127.0.0.1",
            "localhost",
        }
    ):
        raise (
            EmailVerificationConfigurationError(
                "Незащищённый HTTP разрешён "
                "только для локальной разработки."
            )
        )

    return app_base_url.rstrip(
        "/"
    )

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

def create_email_verification_url(
    user_id: int,
) -> str:
    """
    Создаёт полную ссылку
    подтверждения email.
    """
    app_base_url = get_app_base_url()

    token = (
        create_email_verification_token(
            user_id=user_id
        )
    )

    query_string = urlencode(
        {
            "token": token,
        }
    )

    return (
        f"{app_base_url}/verify-email"
        f"?{query_string}"
    )

def send_email_verification_message(
    recipient_email: str,
    user_id: int,
) -> email_service.EmailSendResult:
    """
    Формирует и отправляет пользователю
    письмо с подтверждением email.
    """
    verification_url = (
        create_email_verification_url(
            user_id=user_id
        )
    )

    safe_verification_url = escape(
        verification_url,
        quote=True,
    )

    return email_service.send_email(
        recipient_email=recipient_email,
        subject=(
            "Подтвердите email — "
            "Decision Matrix AI"
        ),
        html_content=(
            "<h1>Подтвердите email</h1>"
            "<p>"
            "Для завершения регистрации "
            "в Decision Matrix AI перейдите "
            "по ссылке:"
            "</p>"
            "<p>"
            f'<a href="{safe_verification_url}">'
            "Подтвердить email"
            "</a>"
            "</p>"
            "<p>"
            "Ссылка действует в течение "
            "24 часов."
            "</p>"
            "<p>"
            "Если вы не регистрировались "
            "в Decision Matrix AI, "
            "проигнорируйте это письмо."
            "</p>"
        ),
        text_content=(
            "Для завершения регистрации "
            "в Decision Matrix AI перейдите "
            "по ссылке:\n\n"
            f"{verification_url}\n\n"
            "Ссылка действует в течение "
            "24 часов.\n\n"
            "Если вы не регистрировались "
            "в Decision Matrix AI, "
            "проигнорируйте это письмо."
        ),
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
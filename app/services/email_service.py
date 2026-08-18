import os
from dataclasses import dataclass

import httpx


BREVO_EMAIL_API_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_REQUEST_TIMEOUT_SECONDS = 10.0


class EmailServiceError(RuntimeError):
    """Базовая ошибка сервиса отправки писем."""


class EmailConfigurationError(EmailServiceError):
    """Ошибка конфигурации почтового сервиса."""


class EmailDeliveryError(EmailServiceError):
    """Ошибка передачи письма в Brevo."""


@dataclass(frozen=True)
class EmailSendResult:
    """Результат успешной передачи письма в Brevo."""

    message_id: str | None


def get_required_setting(
    name: str,
) -> str:
    """
    Получает обязательную переменную окружения.

    Если переменная отсутствует или пуста,
    останавливает отправку с понятной ошибкой.
    """
    value = os.getenv(
        name,
        "",
    ).strip()

    if not value:
        raise EmailConfigurationError(
            f"Не задана переменная окружения {name}."
        )

    return value


def send_email(
    recipient_email: str,
    subject: str,
    html_content: str,
    recipient_name: str | None = None,
    text_content: str | None = None,
) -> EmailSendResult:
    """
    Передаёт одно транзакционное письмо
    в Brevo Transactional Email API.
    """
    recipient_email = recipient_email.strip()
    subject = subject.strip()

    if not recipient_email:
        raise ValueError(
            "Email получателя не может быть пустым."
        )

    if not subject:
        raise ValueError(
            "Тема письма не может быть пустой."
        )

    if not html_content.strip():
        raise ValueError(
            "HTML-содержимое письма не может быть пустым."
        )

    api_key = get_required_setting(
        "BREVO_API_KEY"
    )

    sender_email = get_required_setting(
        "BREVO_SENDER_EMAIL"
    )

    sender_name = get_required_setting(
        "BREVO_SENDER_NAME"
    )

    recipient = {
        "email": recipient_email,
    }

    if (
        recipient_name
        and recipient_name.strip()
    ):
        recipient["name"] = (
            recipient_name.strip()
        )

    payload = {
        "sender": {
            "email": sender_email,
            "name": sender_name,
        },
        "to": [
            recipient,
        ],
        "subject": subject,
        "htmlContent": html_content,
    }

    if text_content is not None:
        payload["textContent"] = (
            text_content
        )

    try:
        response = httpx.post(
            BREVO_EMAIL_API_URL,
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json=payload,
            timeout=BREVO_REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.RequestError as error:
        raise EmailDeliveryError(
            "Не удалось подключиться "
            "к сервису отправки писем."
        ) from error

    if response.status_code not in {
        200,
        201,
        202,
    }:
        raise EmailDeliveryError(
            "Brevo отклонил отправку письма "
            f"(HTTP {response.status_code})."
        )

    try:
        response_data = response.json()
    except ValueError:
        response_data = {}

    message_id = None

    if isinstance(
        response_data,
        dict,
    ):
        received_message_id = (
            response_data.get("messageId")
        )

        if isinstance(
            received_message_id,
            str,
        ):
            message_id = received_message_id

    return EmailSendResult(
        message_id=message_id,
    )
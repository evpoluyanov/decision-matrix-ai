import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr

import httpx


BREVO_EMAIL_API_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_REQUEST_TIMEOUT_SECONDS = 10.0
SMTP_REQUEST_TIMEOUT_SECONDS = 10.0


class EmailServiceError(RuntimeError):
    """Базовая ошибка сервиса отправки писем."""


class EmailConfigurationError(EmailServiceError):
    """Ошибка конфигурации почтового сервиса."""


class EmailDeliveryError(EmailServiceError):
    """Ошибка передачи письма почтовому провайдеру."""


@dataclass(frozen=True)
class EmailSendResult:
    """Результат успешной передачи письма."""

    message_id: str | None


def get_required_setting(name: str) -> str:
    """Получает обязательную переменную окружения."""
    value = os.getenv(name, "").strip()

    if not value:
        raise EmailConfigurationError(
            f"Не задана переменная окружения {name}."
        )

    return value


def _send_via_smtp(
    recipient_email: str,
    subject: str,
    html_content: str,
    recipient_name: str | None,
    text_content: str | None,
) -> EmailSendResult:
    host = get_required_setting("SMTP_HOST")

    try:
        port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError as error:
        raise EmailConfigurationError(
            "Переменная SMTP_PORT должна быть числом."
        ) from error

    security = os.getenv("SMTP_SECURITY", "starttls").strip().lower()
    username = get_required_setting("SMTP_USERNAME")
    password = get_required_setting("SMTP_PASSWORD")
    sender_email = get_required_setting("EMAIL_SENDER_EMAIL")
    sender_name = get_required_setting("EMAIL_SENDER_NAME")

    message = EmailMessage()
    message["From"] = formataddr((sender_name, sender_email))
    message["To"] = (
        formataddr((recipient_name.strip(), recipient_email))
        if recipient_name and recipient_name.strip()
        else recipient_email
    )
    message["Subject"] = subject
    message.set_content(text_content or "")
    message.add_alternative(html_content, subtype="html")

    try:
        if security in {"smtps", "ssl"}:
            smtp_client = smtplib.SMTP_SSL(
                host,
                port,
                timeout=SMTP_REQUEST_TIMEOUT_SECONDS,
                context=ssl.create_default_context(),
            )
        elif security in {"starttls", "tls"}:
            smtp_client = smtplib.SMTP(
                host,
                port,
                timeout=SMTP_REQUEST_TIMEOUT_SECONDS,
            )
        else:
            raise EmailConfigurationError(
                "SMTP_SECURITY должен быть starttls или smtps."
            )

        with smtp_client as client:
            if security in {"starttls", "tls"}:
                client.starttls(context=ssl.create_default_context())

            client.login(username, password)
            client.send_message(message)

    except EmailConfigurationError:
        raise
    except (OSError, smtplib.SMTPException) as error:
        raise EmailDeliveryError(
            "Не удалось отправить письмо через SMTP."
        ) from error

    return EmailSendResult(message_id=None)


def _send_via_brevo(
    recipient_email: str,
    subject: str,
    html_content: str,
    recipient_name: str | None,
    text_content: str | None,
) -> EmailSendResult:
    api_key = get_required_setting("BREVO_API_KEY")
    sender_email = get_required_setting("BREVO_SENDER_EMAIL")
    sender_name = get_required_setting("BREVO_SENDER_NAME")

    recipient = {"email": recipient_email}

    if recipient_name and recipient_name.strip():
        recipient["name"] = recipient_name.strip()

    payload = {
        "sender": {
            "email": sender_email,
            "name": sender_name,
        },
        "to": [recipient],
        "subject": subject,
        "htmlContent": html_content,
    }

    if text_content is not None:
        payload["textContent"] = text_content

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
            "Не удалось подключиться к сервису отправки писем."
        ) from error

    if response.status_code not in {200, 201, 202}:
        raise EmailDeliveryError(
            "Brevo отклонил отправку письма "
            f"(HTTP {response.status_code})."
        )

    try:
        response_data = response.json()
    except ValueError:
        response_data = {}

    message_id = None

    if isinstance(response_data, dict):
        received_message_id = response_data.get("messageId")

        if isinstance(received_message_id, str):
            message_id = received_message_id

    return EmailSendResult(message_id=message_id)


def send_email(
    recipient_email: str,
    subject: str,
    html_content: str,
    recipient_name: str | None = None,
    text_content: str | None = None,
) -> EmailSendResult:
    recipient_email = recipient_email.strip()
    subject = subject.strip()

    if not recipient_email:
        raise ValueError("Email получателя не может быть пустым.")

    if not subject:
        raise ValueError("Тема письма не может быть пустой.")

    if not html_content.strip():
        raise ValueError("HTML-содержимое письма не может быть пустым.")

    provider = os.getenv("EMAIL_PROVIDER", "brevo").strip().lower()

    if provider == "smtp":
        return _send_via_smtp(
            recipient_email,
            subject,
            html_content,
            recipient_name,
            text_content,
        )

    if provider == "brevo":
        return _send_via_brevo(
            recipient_email,
            subject,
            html_content,
            recipient_name,
            text_content,
        )

    raise EmailConfigurationError(
        "EMAIL_PROVIDER должен быть smtp или brevo."
    )

import smtplib

import pytest

from app.services import email_service


SMTP_SETTINGS = {
    "EMAIL_PROVIDER": "smtp",
    "SMTP_HOST": "postbox.cloud.yandex.net",
    "SMTP_PORT": "587",
    "SMTP_SECURITY": "starttls",
    "SMTP_USERNAME": "test-api-key-id",
    "SMTP_PASSWORD": "test-api-key-secret",
    "EMAIL_SENDER_EMAIL": "noreply@dmatrix.tech",
    "EMAIL_SENDER_NAME": "Decision Matrix AI",
}


def set_smtp_settings(monkeypatch):
    for name, value in SMTP_SETTINGS.items():
        monkeypatch.setenv(name, value)


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.logged_in = None
        self.message = None
        self.__class__.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def starttls(self, context=None):
        self.started_tls = True

    def login(self, username, password):
        self.logged_in = (username, password)

    def send_message(self, message):
        self.message = message


def test_send_email_via_smtp_starttls(monkeypatch):
    FakeSMTP.instances.clear()
    set_smtp_settings(monkeypatch)
    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    result = email_service.send_email(
        recipient_email="recipient@example.com",
        recipient_name="Получатель",
        subject="Проверка SMTP",
        text_content="Текстовая версия",
        html_content="<p>HTML-текст</p>",
    )

    client = FakeSMTP.instances[-1]

    assert result.message_id is None
    assert client.host == "postbox.cloud.yandex.net"
    assert client.port == 587
    assert client.timeout == email_service.SMTP_REQUEST_TIMEOUT_SECONDS
    assert client.started_tls is True
    assert client.logged_in == (
        "test-api-key-id",
        "test-api-key-secret",
    )
    assert client.message["From"] == (
        "Decision Matrix AI <noreply@dmatrix.tech>"
    )
    assert client.message["To"] == (
        "Получатель <recipient@example.com>"
    )
    assert client.message["Subject"] == "Проверка SMTP"
    assert (
        client.message.get_body(preferencelist=("plain",))
        .get_content()
        .strip()
        == "Текстовая версия"
    )
    assert (
        client.message.get_body(preferencelist=("html",))
        .get_content()
        .strip()
        == "<p>HTML-текст</p>"
    )


def test_smtp_authentication_error_is_hidden(monkeypatch):
    class RejectingSMTP(FakeSMTP):
        def login(self, username, password):
            raise smtplib.SMTPAuthenticationError(
                535,
                b"authentication failed",
            )

    set_smtp_settings(monkeypatch)
    monkeypatch.setattr(email_service.smtplib, "SMTP", RejectingSMTP)

    with pytest.raises(
        email_service.EmailDeliveryError,
        match="Не удалось отправить письмо через SMTP",
    ):
        email_service.send_email(
            recipient_email="recipient@example.com",
            subject="Проверка ошибки",
            html_content="<p>Тест</p>",
        )


def test_smtp_requires_password(monkeypatch):
    set_smtp_settings(monkeypatch)
    monkeypatch.delenv("SMTP_PASSWORD")

    with pytest.raises(
        email_service.EmailConfigurationError,
        match="SMTP_PASSWORD",
    ):
        email_service.send_email(
            recipient_email="recipient@example.com",
            subject="Проверка настройки",
            html_content="<p>Тест</p>",
        )


def test_unknown_email_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("EMAIL_PROVIDER", "unknown")

    with pytest.raises(
        email_service.EmailConfigurationError,
        match="EMAIL_PROVIDER",
    ):
        email_service.send_email(
            recipient_email="recipient@example.com",
            subject="Проверка провайдера",
            html_content="<p>Тест</p>",
        )

import httpx
import pytest

from app.services import email_service


@pytest.fixture(autouse=True)
def brevo_environment(
    monkeypatch,
):
    """
    Подставляет тестовые настройки Brevo
    вместо значений из настоящего .env.
    """
    monkeypatch.setenv(
        "BREVO_API_KEY",
        "test-api-key",
    )

    monkeypatch.setenv(
        "BREVO_SENDER_EMAIL",
        "no-reply@notify.dmatrix.tech",
    )

    monkeypatch.setenv(
        "BREVO_SENDER_NAME",
        "Decision Matrix AI",
    )


def test_send_email_builds_expected_request(
    monkeypatch,
):
    """
    Проверяет правильность запроса,
    который мы готовим для Brevo.
    """
    captured_request = {}

    def fake_post(
        url,
        *,
        headers,
        json,
        timeout,
    ):
        captured_request.update(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )

        return httpx.Response(
            201,
            json={
                "messageId": "test-message-id",
            },
        )

    monkeypatch.setattr(
        email_service.httpx,
        "post",
        fake_post,
    )

    result = email_service.send_email(
        recipient_email=" user@example.com ",
        recipient_name=" Тестовый пользователь ",
        subject=" Тестовая тема ",
        html_content="<p>Тест</p>",
        text_content="Тест",
    )

    assert result.message_id == (
        "test-message-id"
    )

    assert captured_request["url"] == (
        email_service.BREVO_EMAIL_API_URL
    )

    assert captured_request["headers"][
        "api-key"
    ] == "test-api-key"

    assert captured_request["json"] == {
        "sender": {
            "email": (
                "no-reply@notify.dmatrix.tech"
            ),
            "name": "Decision Matrix AI",
        },
        "to": [
            {
                "email": "user@example.com",
                "name": (
                    "Тестовый пользователь"
                ),
            }
        ],
        "subject": "Тестовая тема",
        "htmlContent": "<p>Тест</p>",
        "textContent": "Тест",
    }


def test_send_email_requires_api_key(
    monkeypatch,
):
    """
    Проверяет отказ от отправки,
    если API-ключ отсутствует.
    """
    monkeypatch.delenv(
        "BREVO_API_KEY"
    )

    with pytest.raises(
        email_service.EmailConfigurationError,
        match="BREVO_API_KEY",
    ):
        email_service.send_email(
            recipient_email="user@example.com",
            subject="Тест",
            html_content="<p>Тест</p>",
        )


def test_send_email_handles_network_error(
    monkeypatch,
):
    """
    Проверяет безопасную обработку
    сетевой ошибки.
    """
    def fake_post(
        *args,
        **kwargs,
    ):
        request = httpx.Request(
            "POST",
            email_service.BREVO_EMAIL_API_URL,
        )

        raise httpx.ConnectError(
            "Соединение отсутствует",
            request=request,
        )

    monkeypatch.setattr(
        email_service.httpx,
        "post",
        fake_post,
    )

    with pytest.raises(
        email_service.EmailDeliveryError,
        match="Не удалось подключиться",
    ):
        email_service.send_email(
            recipient_email="user@example.com",
            subject="Тест",
            html_content="<p>Тест</p>",
        )


def test_send_email_handles_brevo_rejection(
    monkeypatch,
):
    """
    Проверяет обработку отказа Brevo.
    """
    def fake_post(
        *args,
        **kwargs,
    ):
        return httpx.Response(
            400,
            json={
                "message": "Rejected",
            },
        )

    monkeypatch.setattr(
        email_service.httpx,
        "post",
        fake_post,
    )

    with pytest.raises(
        email_service.EmailDeliveryError,
        match="HTTP 400",
    ):
        email_service.send_email(
            recipient_email="user@example.com",
            subject="Тест",
            html_content="<p>Тест</p>",
        )
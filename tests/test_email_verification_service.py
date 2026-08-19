from urllib.parse import (
    parse_qs,
    urlparse,
)

import pytest

from app.services import (
    email_verification_service,
)


@pytest.fixture(autouse=True)
def session_secret(
    monkeypatch,
):
    """
    Подставляет отдельный тестовый
    секрет вместо настоящего.
    """
    monkeypatch.setenv(
        "SESSION_SECRET",
        "test-session-secret",
    )

    monkeypatch.setenv(
        "APP_BASE_URL",
        "http://127.0.0.1:8000",
    )


def test_token_round_trip():
    """
    Из корректного токена должен
    извлекаться исходный user_id.
    """
    token = (
        email_verification_service
        .create_email_verification_token(
            user_id=123
        )
    )

    user_id = (
        email_verification_service
        .verify_email_verification_token(
            token
        )
    )

    assert user_id == 123


@pytest.mark.parametrize(
    "invalid_user_id",
    [
        0,
        -1,
        True,
        "123",
    ],
)
def test_token_rejects_invalid_user_id(
    invalid_user_id,
):
    """
    Токен нельзя создать для
    некорректного идентификатора.
    """
    with pytest.raises(
        ValueError
    ):
        (
            email_verification_service
            .create_email_verification_token(
                user_id=invalid_user_id
            )
        )


def test_token_rejects_modified_value():
    """
    Любое изменение подписанного токена
    должно сделать его недействительным.
    """
    token = (
        email_verification_service
        .create_email_verification_token(
            user_id=123
        )
    )

    modified_token = (
        token + "modified"
    )

    with pytest.raises(
        email_verification_service
        .EmailVerificationTokenError
    ):
        (
            email_verification_service
            .verify_email_verification_token(
                modified_token
            )
        )


def test_token_reports_expiration():
    """
    Просроченный токен должен давать
    отдельную понятную ошибку.
    """
    token = (
        email_verification_service
        .create_email_verification_token(
            user_id=123
        )
    )

    with pytest.raises(
        email_verification_service
        .EmailVerificationTokenExpiredError
    ):
        (
            email_verification_service
            .verify_email_verification_token(
                token,
                max_age_seconds=-1,
            )
        )


def test_token_requires_session_secret(
    monkeypatch,
):
    """
    Без секретного ключа токены
    создаваться не должны.
    """
    monkeypatch.delenv(
        "SESSION_SECRET"
    )

    with pytest.raises(
        email_verification_service
        .EmailVerificationConfigurationError,
        match="SESSION_SECRET",
    ):
        (
            email_verification_service
            .create_email_verification_token(
                user_id=123
            )
        )

def test_token_signed_with_another_secret_is_rejected(
    monkeypatch,
):
    """
    Токен, подписанный другим секретом,
    не должен проходить проверку.
    """
    token = (
        email_verification_service
        .create_email_verification_token(
            user_id=123
        )
    )

    monkeypatch.setenv(
        "SESSION_SECRET",
        "another-session-secret",
    )

    with pytest.raises(
        email_verification_service
        .EmailVerificationTokenError
    ):
        (
            email_verification_service
            .verify_email_verification_token(
                token
            )
        )

def test_create_email_verification_url():
    """
    Ссылка должна содержать правильный
    адрес, маршрут и рабочий токен.
    """
    verification_url = (
        email_verification_service
        .create_email_verification_url(
            user_id=123
        )
    )

    parsed_url = urlparse(
        verification_url
    )

    token = parse_qs(
        parsed_url.query
    )["token"][0]

    assert parsed_url.scheme == "http"

    assert (
        parsed_url.netloc
        == "127.0.0.1:8000"
    )

    assert (
        parsed_url.path
        == "/verify-email"
    )

    assert (
        email_verification_service
        .verify_email_verification_token(
            token
        )
        == 123
    )


def test_app_base_url_removes_trailing_slash(
    monkeypatch,
):
    """
    Завершающий слеш не должен создавать
    двойной слеш в ссылке.
    """
    monkeypatch.setenv(
        "APP_BASE_URL",
        "https://dmatrix.tech/",
    )

    verification_url = (
        email_verification_service
        .create_email_verification_url(
            user_id=123
        )
    )

    assert verification_url.startswith(
        "https://dmatrix.tech/verify-email?"
    )

    assert (
        "dmatrix.tech//verify-email"
        not in verification_url
    )


def test_app_base_url_is_required(
    monkeypatch,
):
    """
    Без адреса приложения ссылку
    создавать нельзя.
    """
    monkeypatch.delenv(
        "APP_BASE_URL"
    )

    with pytest.raises(
        email_verification_service
        .EmailVerificationConfigurationError,
        match="APP_BASE_URL",
    ):
        (
            email_verification_service
            .create_email_verification_url(
                user_id=123
            )
        )


@pytest.mark.parametrize(
    "invalid_app_base_url",
    [
        "dmatrix.tech",
        "http://dmatrix.tech",
        "https://dmatrix.tech/path",
        "https://dmatrix.tech?source=test",
        "https://dmatrix.tech#fragment",
    ],
)
def test_app_base_url_rejects_unsafe_values(
    monkeypatch,
    invalid_app_base_url,
):
    """
    Внешний адрес должен использовать HTTPS
    и не содержать лишних частей.
    """
    monkeypatch.setenv(
        "APP_BASE_URL",
        invalid_app_base_url,
    )

    with pytest.raises(
        email_verification_service
        .EmailVerificationConfigurationError,
    ):
        (
            email_verification_service
            .create_email_verification_url(
                user_id=123
            )
        )

def test_send_email_verification_message(
    monkeypatch,
):
    """
    Письмо должно содержать рабочую
    ссылку подтверждения.
    """
    monkeypatch.setenv(
        "APP_BASE_URL",
        "https://dmatrix.tech",
    )

    captured_email = {}

    def fake_send_email(
        **kwargs,
    ):
        captured_email.update(
            kwargs
        )

        return (
            email_verification_service
            .email_service
            .EmailSendResult(
                message_id=(
                    "test-message-id"
                )
            )
        )

    monkeypatch.setattr(
        email_verification_service
        .email_service,
        "send_email",
        fake_send_email,
    )

    result = (
        email_verification_service
        .send_email_verification_message(
            recipient_email=(
                "user@example.com"
            ),
            user_id=123,
        )
    )

    assert result.message_id == (
        "test-message-id"
    )

    assert captured_email[
        "recipient_email"
    ] == "user@example.com"

    assert captured_email[
        "subject"
    ] == (
        "Подтвердите email — "
        "Decision Matrix AI"
    )

    assert (
        "https://dmatrix.tech/"
        "verify-email?token="
        in captured_email[
            "html_content"
        ]
    )

    assert (
        "https://dmatrix.tech/"
        "verify-email?token="
        in captured_email[
            "text_content"
        ]
    )

    assert (
        "24 часов"
        in captured_email[
            "html_content"
        ]
    )
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
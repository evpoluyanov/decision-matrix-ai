from app import models
from app.services import (
    email_verification_service,
)


def test_verify_email_route_confirms_user(
    client,
    test_environment,
):
    """
    Корректная ссылка должна подтвердить
    email пользователя.
    """
    user_id = test_environment[
        "user_1_id"
    ]

    token = (
        email_verification_service
        .create_email_verification_token(
            user_id=user_id
        )
    )

    response = client.get(
        "/verify-email",
        params={
            "token": token,
        },
    )

    assert response.status_code == 200

    assert (
        "Email успешно подтверждён"
        in response.text
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    with TestingSessionLocal() as database:
        user = database.get(
            models.User,
            user_id,
        )

        assert user is not None
        assert user.email_verified is True


def test_verify_email_route_is_repeatable(
    client,
    test_environment,
):
    """
    Повторный переход по корректной ссылке
    должен оставаться безопасным.
    """
    user_id = test_environment[
        "user_1_id"
    ]

    token = (
        email_verification_service
        .create_email_verification_token(
            user_id=user_id
        )
    )

    first_response = client.get(
        "/verify-email",
        params={
            "token": token,
        },
    )

    second_response = client.get(
        "/verify-email",
        params={
            "token": token,
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert (
        "Email уже подтверждён"
        in second_response.text
    )


def test_verify_email_route_rejects_invalid_token(
    client,
):
    """
    Поддельная ссылка должна быть
    отклонена без раскрытия данных.
    """
    response = client.get(
        "/verify-email",
        params={
            "token": "invalid-token",
        },
    )

    assert response.status_code == 400

    assert (
        "Ссылка недействительна"
        in response.text
    )


def test_verify_email_route_rejects_missing_user(
    client,
):
    """
    Корректно подписанный токен для
    отсутствующего пользователя отклоняется.
    """
    token = (
        email_verification_service
        .create_email_verification_token(
            user_id=999999
        )
    )

    response = client.get(
        "/verify-email",
        params={
            "token": token,
        },
    )

    assert response.status_code == 400

    assert (
        "Ссылка недействительна"
        in response.text
    )


def test_verify_email_route_reports_expired_token(
    client,
    monkeypatch,
):
    """
    Для просроченной ссылки маршрут
    должен возвращать HTTP 410.
    """
    def raise_expired_token_error(
        *args,
        **kwargs,
    ):
        raise (
            email_verification_service
            .EmailVerificationTokenExpiredError(
                "Срок действия ссылки истёк."
            )
        )

    monkeypatch.setattr(
        email_verification_service,
        "verify_email_verification_token",
        raise_expired_token_error,
    )

    response = client.get(
        "/verify-email",
        params={
            "token": "expired-token",
        },
    )

    assert response.status_code == 410

    assert (
        "Срок действия ссылки истёк"
        in response.text
    )


def test_verify_email_route_rejects_empty_token(
    client,
):
    """
    Открытие маршрута без токена
    должно показать безопасную ошибку.
    """
    response = client.get(
        "/verify-email"
    )

    assert response.status_code == 400

    assert (
        "Ссылка недействительна"
        in response.text
    )
from app import models
from app.services import (
    email_verification_service,
)


def test_verify_email_get_does_not_confirm_user(
    client,
    test_environment,
):
    """
    Открытие ссылки должно показать кнопку,
    но не изменять пользователя.
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
        "Подтвердите email"
        in response.text
    )

    assert (
        "Подтвердить email"
        in response.text
    )

    assert (
        'action="/verify-email"'
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
        assert user.email_verified is False


def test_verify_email_post_confirms_user(
    client,
    test_environment,
):
    """
    Отправка формы должна подтвердить email
    и перенаправить на страницу результата.
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

    response = client.post(
        "/verify-email",
        data={
            "token": token,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    assert response.headers[
        "location"
    ] == "/verify-email/result"

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

    result_page = client.get(
        "/verify-email/result"
    )

    assert result_page.status_code == 200

    assert (
        "Email успешно подтверждён"
        in result_page.text
    )


def test_verify_email_route_is_repeatable(
    client,
    test_environment,
):
    """
    Повторное открытие ссылки после
    подтверждения должно быть безопасным.
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

    first_response = client.post(
        "/verify-email",
        data={
            "token": token,
        },
        follow_redirects=False,
    )

    assert first_response.status_code == 303

    result_page = client.get(
        "/verify-email/result"
    )

    assert result_page.status_code == 200

    second_response = client.get(
        "/verify-email",
        params={
            "token": token,
        },
    )

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


def test_verify_email_post_rejects_invalid_token(
    client,
):
    """
    POST с поддельным токеном не должен
    изменять данные пользователя.
    """
    response = client.post(
        "/verify-email",
        data={
            "token": "invalid-token",
        },
    )

    assert response.status_code == 400

    assert (
        "Ссылка недействительна"
        in response.text
    )


def test_email_verification_result_requires_post(
    client,
):
    """
    Страницу успешного результата нельзя
    открыть без подтверждения через POST.
    """
    response = client.get(
        "/verify-email/result",
        follow_redirects=False,
    )

    assert response.status_code == 303

    assert response.headers[
        "location"
    ] == "/login"

def test_verification_result_shows_current_account(
    client,
    test_environment,
):
    """
    При действующей сессии результат должен
    вести в текущий кабинет, а не на вход.
    """
    user_id = test_environment[
        "user_1_id"
    ]

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

        user.email_verified = True
        database.commit()

    login_response = client.post(
        "/login",
        data={
            "email": "user1@test.com",
            "password": "test-password-123",
        },
        follow_redirects=False,
    )

    assert login_response.status_code == 303

    token = (
        email_verification_service
        .create_email_verification_token(
            user_id=user_id
        )
    )

    confirmation_response = client.post(
        "/verify-email",
        data={
            "token": token,
        },
        follow_redirects=False,
    )

    assert confirmation_response.status_code == 303

    result_page = client.get(
        "/verify-email/result"
    )

    assert result_page.status_code == 200

    assert (
        "Email уже подтверждён"
        in result_page.text
    )

    assert (
        "Текущий личный кабинет"
        in result_page.text
    )

    assert (
        'href="/account"'
        in result_page.text
    )
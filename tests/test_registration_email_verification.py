import re

from app.services import (
    email_service,
    email_verification_service,
    legal_document_service,
    user_service,
)
from app import models
from sqlalchemy import select


TEST_REGISTRATION_PASSWORD = (
    "test-password-123"
)


def test_registration_sends_verification_email(
    client,
    test_environment,
    monkeypatch,
):
    """
    Успешная регистрация должна вызвать
    отправку письма новому пользователю.
    """
    captured_message = {}

    def fake_send_verification_message(
        *,
        recipient_email,
        user_id,
    ):
        captured_message.update(
            {
                "recipient_email":
                    recipient_email,
                "user_id":
                    user_id,
            }
        )

    monkeypatch.setattr(
        email_verification_service,
        "send_email_verification_message",
        fake_send_verification_message,
    )

    response = client.post(
        "/register",
        data={
            "email":
                "registration@test.com",
            "password":
                TEST_REGISTRATION_PASSWORD,
            "password_confirmation":
                TEST_REGISTRATION_PASSWORD,
            "terms_accepted": "yes",
            "personal_data_consent": "yes",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    assert response.headers[
        "location"
    ] == "/register/success"

    assert captured_message[
        "recipient_email"
    ] == "registration@test.com"

    assert isinstance(
        captured_message["user_id"],
        int,
    )

    success_page = client.get(
        "/register/success"
    )

    assert success_page.status_code == 200

    assert (
        "Проверьте электронную почту"
        in success_page.text
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    with TestingSessionLocal() as database:
        user = user_service.get_user_by_email(
            db=database,
            email="registration@test.com",
        )

        assert user is not None

        assert user.id == (
            captured_message["user_id"]
        )

        assert user.email_verified is False
        acceptances = list(database.scalars(
            select(models.UserLegalAcceptance).where(
                models.UserLegalAcceptance.user_id == user.id
            )
        ))
        assert len(acceptances) == 3
        assert {row.action for row in acceptances} == {
            "accepted", "acknowledged", "consented",
        }
        assert legal_document_service.pending_versions(database, user.id) == []


def test_registration_survives_email_error(
    client,
    test_environment,
    monkeypatch,
):
    """
    Ошибка Brevo не должна удалять
    уже созданную учётную запись.
    """
    def raise_email_error(
        *,
        recipient_email,
        user_id,
    ):
        raise (
            email_service
            .EmailDeliveryError(
                "Тестовая ошибка отправки."
            )
        )

    monkeypatch.setattr(
        email_verification_service,
        "send_email_verification_message",
        raise_email_error,
    )

    response = client.post(
        "/register",
        data={
            "email":
                "email-error@test.com",
            "password":
                TEST_REGISTRATION_PASSWORD,
            "password_confirmation":
                TEST_REGISTRATION_PASSWORD,
            "terms_accepted": "yes",
            "personal_data_consent": "yes",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    success_page = client.get(
        "/register/success"
    )

    assert success_page.status_code == 200

    assert (
        "Письмо подтверждения пока"
        in success_page.text
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    with TestingSessionLocal() as database:
        user = user_service.get_user_by_email(
            db=database,
            email="email-error@test.com",
        )

        assert user is not None
        assert user.email_verified is False


def test_registration_success_requires_registration(
    client,
):
    """
    Страницу результата нельзя открыть
    без предыдущей регистрации.
    """
    response = client.get(
        "/register/success",
        follow_redirects=False,
    )

    assert response.status_code == 303

    assert response.headers[
        "location"
    ] == "/register"


def test_duplicate_registration_does_not_send_email(
    client,
    monkeypatch,
):
    """
    Для уже существующего email новое
    письмо при регистрации не отправляется.
    """
    email_was_sent = False

    def fake_send_verification_message(
        *,
        recipient_email,
        user_id,
    ):
        nonlocal email_was_sent

        email_was_sent = True

    monkeypatch.setattr(
        email_verification_service,
        "send_email_verification_message",
        fake_send_verification_message,
    )

    response = client.post(
        "/register",
        data={
            "email": "user1@test.com",
            "password":
                TEST_REGISTRATION_PASSWORD,
            "password_confirmation":
                TEST_REGISTRATION_PASSWORD,
            "terms_accepted": "yes",
            "personal_data_consent": "yes",
        },
    )

    assert response.status_code == 409
    assert email_was_sent is False

def test_authenticated_user_cannot_open_registration(
    client,
):
    """
    Авторизованному пользователю форма
    регистрации недоступна.
    """
    login_response = client.post(
        "/login",
        data={
            "email": "user1@test.com",
            "password":
                TEST_REGISTRATION_PASSWORD,
        },
        follow_redirects=False,
    )

    assert login_response.status_code == 303

    response = client.get(
        "/register",
        follow_redirects=False,
    )

    assert response.status_code == 303

    assert response.headers[
        "location"
    ] == "/start"


def test_authenticated_user_cannot_register_again(
    client,
    test_environment,
    monkeypatch,
):
    """
    Прямой POST не должен создавать второй
    аккаунт из авторизованной сессии.
    """
    email_was_sent = False

    def fake_send_verification_message(
        *,
        recipient_email,
        user_id,
    ):
        nonlocal email_was_sent

        email_was_sent = True

    monkeypatch.setattr(
        email_verification_service,
        "send_email_verification_message",
        fake_send_verification_message,
    )

    login_response = client.post(
        "/login",
        data={
            "email": "user1@test.com",
            "password":
                TEST_REGISTRATION_PASSWORD,
        },
        follow_redirects=False,
    )

    assert login_response.status_code == 303

    response = client.post(
        "/register",
        data={
            "email":
                "blocked-registration@test.com",
            "password":
                TEST_REGISTRATION_PASSWORD,
            "password_confirmation":
                TEST_REGISTRATION_PASSWORD,
            "terms_accepted": "yes",
            "personal_data_consent": "yes",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    assert response.headers[
        "location"
    ] == "/start"

    assert email_was_sent is False

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    with TestingSessionLocal() as database:
        user = user_service.get_user_by_email(
            db=database,
            email=(
                "blocked-registration@test.com"
            ),
        )

        assert user is None


def test_registration_requires_separate_legal_confirmations(
    client,
    test_environment,
    monkeypatch,
):
    sent = []
    monkeypatch.setattr(
        email_verification_service,
        "send_email_verification_message",
        lambda **kwargs: sent.append(kwargs),
    )
    base = {
        "email": "no-consent@test.com",
        "password": TEST_REGISTRATION_PASSWORD,
        "password_confirmation": TEST_REGISTRATION_PASSWORD,
    }

    response = client.post("/register", data=base)
    assert response.status_code == 400
    assert "Примите Пользовательское соглашение." in response.text
    assert "Дайте согласие на обработку персональных данных." in response.text

    response = client.post(
        "/register",
        data={**base, "terms_accepted": "yes"},
    )
    assert response.status_code == 400
    assert "Дайте согласие на обработку персональных данных." in response.text
    assert re.search(
        r'<input(?=[^>]*name="terms_accepted")(?=[^>]*\bchecked\b)[^>]*>',
        response.text,
    )
    assert not re.search(
        r'<input(?=[^>]*name="personal_data_consent")(?=[^>]*\bchecked\b)[^>]*>',
        response.text,
    )

    with test_environment["TestingSessionLocal"]() as database:
        assert user_service.get_user_by_email(
            db=database,
            email="no-consent@test.com",
        ) is None
    assert sent == []

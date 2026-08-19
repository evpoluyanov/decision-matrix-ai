from app import models
from app.services import user_service


def test_new_user_starts_unverified(
    test_environment,
):
    """
    Новый пользователь должен создаваться
    с неподтверждённым email.
    """
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    with TestingSessionLocal() as database:
        user = user_service.create_user(
            db=database,
            email="new-user@test.com",
            password="test-password-123",
        )

        assert user is not None
        assert user.email_verified is False


def test_mark_email_as_verified(
    test_environment,
):
    """
    Подтверждение должно сохраняться
    в базе данных.
    """
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    user_id = test_environment[
        "user_1_id"
    ]

    with TestingSessionLocal() as database:
        user = user_service.get_user_by_id(
            db=database,
            user_id=user_id,
        )

        assert user is not None
        assert user.email_verified is False

        status_changed = (
            user_service
            .mark_email_as_verified(
                db=database,
                user=user,
            )
        )

        assert status_changed is True
        assert user.email_verified is True

    with TestingSessionLocal() as database:
        saved_user = (
            database.get(
                models.User,
                user_id,
            )
        )

        assert saved_user is not None
        assert saved_user.email_verified is True


def test_repeated_email_verification_is_safe(
    test_environment,
):
    """
    Повторное подтверждение не должно
    изменять данные или вызывать ошибку.
    """
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    user_id = test_environment[
        "user_1_id"
    ]

    with TestingSessionLocal() as database:
        user = user_service.get_user_by_id(
            db=database,
            user_id=user_id,
        )

        assert user is not None

        first_result = (
            user_service
            .mark_email_as_verified(
                db=database,
                user=user,
            )
        )

        second_result = (
            user_service
            .mark_email_as_verified(
                db=database,
                user=user,
            )
        )

        assert first_result is True
        assert second_result is False
        assert user.email_verified is True
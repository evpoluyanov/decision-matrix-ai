from sqlalchemy import select

from app import models
from app.services import email_verification_service, user_service


PASSWORD = "test-password-123"


def test_start_before_registration_is_restored_after_verification(
    client,
    test_environment,
    monkeypatch,
):
    sent = {}

    def fake_send(*, recipient_email, user_id):
        sent.update(recipient_email=recipient_email, user_id=user_id)

    monkeypatch.setattr(
        email_verification_service,
        "send_email_verification_message",
        fake_send,
    )

    start = client.get("/start")
    assert start.status_code == 200
    assert "Подрядчик или поставщик" in start.text
    assert "Что вы хотите выбрать?" in start.text

    draft = client.post(
        "/start",
        data={
            "template_key": "software",
            "decision_question": "Какую CRM выбрать для отдела продаж?",
            "decision_details": "До 20 пользователей, нужен российский сервер.",
        },
        follow_redirects=False,
    )
    assert draft.status_code == 303
    assert draft.headers["location"] == "/register?from=start"

    registration = client.get(draft.headers["location"])
    assert "Ваш выбор сохранён" in registration.text
    assert "Какую CRM выбрать" in registration.text

    registered = client.post(
        "/register",
        data={
            "email": "journey@test.com",
            "password": PASSWORD,
            "password_confirmation": PASSWORD,
            "terms_accepted": "yes",
            "personal_data_consent": "yes",
        },
        follow_redirects=False,
    )
    assert registered.status_code == 303
    assert registered.headers["location"] == "/register/success"

    success = client.get("/register/success")
    assert "journey@test.com" in success.text
    assert "сразу откроем ваше решение" in success.text

    token = email_verification_service.create_email_verification_token(sent["user_id"])
    verify_page = client.get("/verify-email", params={"token": token})
    assert "/static/verify-email.js" in verify_page.text

    confirmed = client.post(
        "/verify-email",
        data={"token": token},
        follow_redirects=False,
    )
    assert confirmed.status_code == 303
    assert confirmed.headers["location"].startswith("/projects/")
    assert "welcome=1" in confirmed.headers["location"]

    project_page = client.get(confirmed.headers["location"])
    assert project_page.status_code == 200
    assert "Email подтверждён" in project_page.text
    assert "Какую CRM выбрать" in project_page.text
    assert "1. Варианты" in project_page.text
    assert "2. Что для вас важно?" in project_page.text
    assert "3. Рекомендация" in project_page.text
    assert "Подробный расчёт и матрица" in project_page.text

    with test_environment["TestingSessionLocal"]() as db:
        user = user_service.get_user_by_email(db, "journey@test.com")
        assert user is not None and user.email_verified is True
        projects = list(db.scalars(select(models.Project).where(
            models.Project.owner_id == user.id
        )))
        assert len(projects) == 1
        assert projects[0].name == "Какую CRM выбрать для отдела продаж?"


def test_project_creation_redirects_directly_to_workspace(client, test_environment):
    login = client.post(
        "/login",
        data={"email": "user1@test.com", "password": PASSWORD},
        follow_redirects=False,
    )
    assert login.status_code == 303

    created = client.post(
        "/projects",
        data={"project_name": "Прямой переход", "project_description": "Проверка"},
        follow_redirects=False,
    )
    assert created.status_code == 303
    assert created.headers["location"].startswith("/projects/")
    assert "created=1" in created.headers["location"]

    page = client.get(created.headers["location"])
    assert "Решение сохранено" in page.text
    assert "Проект создан" not in page.text


def test_simple_importance_renormalizes_weights(client, test_environment):
    client.post(
        "/login",
        data={"email": "user1@test.com", "password": PASSWORD},
        follow_redirects=False,
    )
    project_id = test_environment["project_1_id"]
    created = client.post(
        f"/projects/{project_id}/criteria",
        data={"name": "Стоимость", "importance": "desirable"},
        follow_redirects=False,
    )
    assert created.status_code == 303

    with test_environment["TestingSessionLocal"]() as db:
        criteria = list(db.scalars(select(models.Criterion).where(
            models.Criterion.project_id == project_id
        ).order_by(models.Criterion.id)))
        assert len(criteria) == 2
        assert abs(sum(item.weight for item in criteria) - 1.0) < 0.000001
        assert criteria[0].weight > criteria[1].weight

    changed = client.post(
        f"/criteria/{criteria[1].id}/importance",
        data={"importance": "very"},
        follow_redirects=False,
    )
    assert changed.status_code == 303
    assert changed.headers["location"].endswith("#priorities")

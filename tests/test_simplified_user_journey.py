import pytest
from sqlalchemy import select

from app import models
from app.services import criterion_service, email_verification_service, user_service


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
    assert "Какого подрядчика выбрать" in start.text
    assert "Что хотите выбрать?" in start.text

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
    assert draft.headers["location"] == "/login?from=start"

    registration = client.get(draft.headers["location"])
    assert "Ваш выбор сохранён" in registration.text
    assert "Какую CRM выбрать" in registration.text
    assert "Зарегистрироваться" in registration.text

    registration = client.get("/register?from=start")
    assert "Ваш выбор сохранён" in registration.text

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
    assert "2. На что смотрим?" in project_page.text
    assert "3. Рекомендация" in project_page.text
    assert "Открыть матрицу и точные веса" in project_page.text

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
        data={"importance": "critical"},
        follow_redirects=False,
    )
    assert changed.status_code == 303
    assert changed.headers["location"].endswith("#priorities")


def test_start_layout_examples_and_navigation_are_streamlined(client, test_environment):
    client.post(
        "/login",
        data={"email": "user1@test.com", "password": PASSWORD},
        follow_redirects=False,
    )
    page = client.get("/start")
    assert page.status_code == 200
    html = page.text
    assert html.index("Что выбираем?") < html.index("Примеры:")
    assert html.index("Примеры:") < html.index("На что обратить внимание при выборе?")
    assert html.count('class="form-control') >= 2
    assert html.count("Например:") >= 2
    assert "Добавить важные условия" not in html
    assert "Перейти к выбору" in html
    assert 'class="example-link"' in html
    assert "Материалы" not in html
    assert "Выбор поставщика" not in html
    assert "Выбор подрядчика" not in html
    assert "Взвешенная матрица решений" not in html
    assert html.index('title="Настройки"') < html.index('title="Тарифы"')
    assert html.index('title="Тарифы"') < html.index('title="Обратная связь"')
    script = client.get("/static/start-decision.js").text
    assert "question.value = card.dataset.templateExample" in script


def test_existing_user_draft_opens_new_choice_without_welcome_message(client, test_environment):
    draft = client.post(
        "/start",
        data={
            "template_key": "software",
            "decision_question": "Какую систему учёта выбрать?",
            "decision_details": "Нужна интеграция с CRM.",
        },
        follow_redirects=False,
    )
    assert draft.headers["location"] == "/login?from=start"
    logged_in = client.post(
        "/login",
        data={"email": "user1@test.com", "password": PASSWORD},
        follow_redirects=False,
    )
    assert logged_in.status_code == 303
    assert "autofill=1" in logged_in.headers["location"]
    assert "welcome=1" not in logged_in.headers["location"]
    page = client.get(logged_in.headers["location"])
    assert "Какую систему учёта выбрать?" in page.text
    assert "Нужна интеграция с CRM." in page.text
    assert "Email подтверждён" not in page.text


def test_project_workspace_has_batch_lists_and_no_inline_editing(client, test_environment):
    client.post(
        "/login",
        data={"email": "user1@test.com", "password": PASSWORD},
        follow_redirects=False,
    )
    project_id = test_environment["project_1_id"]
    page = client.get(f"/projects/{project_id}")
    html = page.text
    assert 'name="project_name"' in html
    assert 'name="project_description"' in html
    assert "Настройки решения" not in html
    assert f'/projects/{project_id}/alternatives/delete' in html
    assert f'/projects/{project_id}/criteria/delete' in html
    assert "/alternatives/1/edit" not in html
    assert "/criteria/1/edit" not in html
    assert "Критично" in html and "Важно" in html and "Желательно" in html
    assert "Точные веса и обоснования критериев" not in html
    assert "Получить результат и отчёт" in html
    assert "window.dmatrixBuildReport" in html


def test_importance_groups_keep_60_30_10_and_renormalize_when_absent(test_environment):
    project_id = test_environment["project_1_id"]
    with test_environment["TestingSessionLocal"]() as db:
        for item in criterion_service.get_criteria(db, project_id):
            criterion_service.delete_criterion(db, item.id)
        first = criterion_service.create_simple_criterion(db, project_id, "Критичный 1", "critical")
        second = criterion_service.create_simple_criterion(db, project_id, "Критичный 2", "critical")
        important = criterion_service.create_simple_criterion(db, project_id, "Важный", "important")
        desirable = criterion_service.create_simple_criterion(db, project_id, "Желательный", "desirable")
        assert first.weight == pytest.approx(0.30)
        assert second.weight == pytest.approx(0.30)
        assert important.weight == pytest.approx(0.30)
        assert desirable.weight == pytest.approx(0.10)
        assert sum(item.weight for item in criterion_service.get_criteria(db, project_id)) == pytest.approx(1.0)

        criterion_service.delete_criterion(db, desirable.id)
        remaining = criterion_service.get_criteria(db, project_id)
        critical = [item for item in remaining if item.importance == "critical"]
        important = [item for item in remaining if item.importance == "important"]
        assert sum(item.weight for item in critical) == pytest.approx(2 / 3)
        assert sum(item.weight for item in important) == pytest.approx(1 / 3)
        assert sum(item.weight for item in remaining) == pytest.approx(1.0)


def test_batch_delete_only_removes_selected_project_items(client, test_environment):
    client.post(
        "/login",
        data={"email": "user1@test.com", "password": PASSWORD},
        follow_redirects=False,
    )
    project_id = test_environment["project_1_id"]
    foreign_id = test_environment["project_2_id"]
    with test_environment["TestingSessionLocal"]() as db:
        own = models.Alternative(name="Удалить", project_id=project_id)
        keep = models.Alternative(name="Оставить", project_id=project_id)
        foreign = models.Alternative(name="Чужой", project_id=foreign_id)
        db.add_all([own, keep, foreign])
        db.commit()
        own_id, keep_id, foreign_alt_id = own.id, keep.id, foreign.id
    response = client.post(
        f"/projects/{project_id}/alternatives/delete",
        data={"alternative_ids": [str(own_id), str(foreign_alt_id)]},
        follow_redirects=False,
    )
    assert response.status_code == 303
    with test_environment["TestingSessionLocal"]() as db:
        assert db.get(models.Alternative, own_id) is None
        assert db.get(models.Alternative, keep_id) is not None
        assert db.get(models.Alternative, foreign_alt_id) is not None

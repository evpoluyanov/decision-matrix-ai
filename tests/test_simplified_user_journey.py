import pytest
from sqlalchemy import select

from app import models
from app.services import criterion_service, email_verification_service, user_service


PASSWORD = "test-password-123"


def test_start_before_registration_is_restored_after_verification(client, test_environment, monkeypatch):
    from app.services import decision_service
    from app.llm.schemas import LLMResponse, LLMUsage
    monkeypatch.setattr(decision_service.llm,"generate",lambda **kw: LLMResponse(
        content='{"options":["А"],"conditions":[{"name":"Стоимость","required":false}]}',
        provider="mock",model="mock",usage=LLMUsage(1,1,0,2)))
    page=client.get("/start")
    assert "Что хотите" in page.text and "Без регистрации" in page.text
    response=client.post("/start",data={"decision_question":"Какую CRM выбрать?"})
    assert response.status_code==200
    url=response.json()["url"]
    assert client.get(url).status_code==200
    assert client.get(url+"/status").json()["understanding"]["options"]==["А"]


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
    html=client.get("/start").text
    assert html.index("Что выбираем?") < html.index("Примеры:") < html.index("На что обратить внимание при выборе?")
    assert html.count("Например:")>=2
    assert "Добавить важные условия" not in html
    assert "Разобраться с выбором" in html
    assert "Тарифы" not in html and "Материалы" not in html
    assert 'id="decision-menu"' in html
    script=client.get("/static/decision-mvp.js").text
    assert 'decision_question.value=q' in script


def test_existing_user_draft_opens_new_choice_without_welcome_message(client, test_environment):
    client.post("/login",data={"email":"user1@test.com","password":PASSWORD})
    page=client.get("/")
    assert page.status_code==200
    assert "Мои разборы" in page.text
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

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import json

from app.llm.schemas import (
    LLMResponse,
    LLMUsage,
)
from app.services import (
    ai_alternative_service,
    ai_criterion_service,
    ai_score_service,
    score_service,
    calculation_service,
)

os.environ["SESSION_SECRET"] = (
    "test-session-secret-for-decision-matrix-ai"
)
os.environ["SESSION_HTTPS_ONLY"] = "false"


from app import models
from app.database import Base, get_db
from app.main import app
from app.security import hash_password


TEST_PASSWORD = "test-password-123"


@pytest.fixture()
def test_environment():
    """
    Создаёт отдельную SQLite-базу в памяти
    для каждого теста.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(
        bind=engine,
    )

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    setup_db = TestingSessionLocal()

    user_1 = models.User(
        email="user1@test.com",
        password_hash=hash_password(
            TEST_PASSWORD
        ),
    )

    user_2 = models.User(
        email="user2@test.com",
        password_hash=hash_password(
            TEST_PASSWORD
        ),
    )

    setup_db.add_all(
        [
            user_1,
            user_2,
        ]
    )

    setup_db.flush()

    project_1 = models.Project(
        name="Проект пользователя 1",
        owner_id=user_1.id,
    )

    project_2 = models.Project(
        name="Проект пользователя 2",
        owner_id=user_2.id,
    )

    setup_db.add_all(
        [
            project_1,
            project_2,
        ]
    )

    setup_db.flush()

    alternative_1 = models.Alternative(
        name="Альтернатива пользователя 1",
        project_id=project_1.id,
    )

    alternative_2 = models.Alternative(
        name="Альтернатива пользователя 2",
        project_id=project_2.id,
    )

    criterion_1 = models.Criterion(
        name="Критерий пользователя 1",
        weight=1.0,
        project_id=project_1.id,
    )

    criterion_2 = models.Criterion(
        name="Критерий пользователя 2",
        weight=1.0,
        project_id=project_2.id,
    )

    setup_db.add_all(
        [
            alternative_1,
            alternative_2,
            criterion_1,
            criterion_2,
        ]
    )

    setup_db.commit()

    data = {
        "TestingSessionLocal": TestingSessionLocal,
        "user_1_id": user_1.id,
        "user_2_id": user_2.id,
        "project_1_id": project_1.id,
        "project_2_id": project_2.id,
        "alternative_1_id": alternative_1.id,
        "alternative_2_id": alternative_2.id,
        "criterion_1_id": criterion_1.id,
        "criterion_2_id": criterion_2.id,
    }

    setup_db.close()

    yield data

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine,
    )

    engine.dispose()


@pytest.fixture()
def client(test_environment):
    with TestClient(app) as test_client:
        yield test_client


def login(
    client: TestClient,
    email: str,
):
    response = client.post(
        "/login",
        data={
            "email": email,
            "password": TEST_PASSWORD,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/account"


def test_projects_require_login(
    client: TestClient,
):
    response = client.get(
        "/projects",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_user_sees_only_own_projects(
    client: TestClient,
):
    login(
        client,
        "user1@test.com",
    )

    response = client.get(
        "/projects",
    )

    assert response.status_code == 200

    assert (
        "Проект пользователя 1"
        in response.text
    )

    assert (
        "Проект пользователя 2"
        not in response.text
    )


def test_user_cannot_open_foreign_project(
    client: TestClient,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    own_project_id = (
        test_environment[
            "project_1_id"
        ]
    )

    foreign_project_id = (
        test_environment[
            "project_2_id"
        ]
    )

    own_response = client.get(
        f"/projects/{own_project_id}"
    )

    foreign_response = client.get(
        f"/projects/{foreign_project_id}"
    )

    assert own_response.status_code == 200

    assert foreign_response.status_code == 404


def test_user_cannot_edit_foreign_project(
    client: TestClient,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    foreign_project_id = (
        test_environment[
            "project_2_id"
        ]
    )

    response = client.post(
        f"/projects/{foreign_project_id}/edit",
        data={
            "project_name": "Взломанный проект",
        },
        follow_redirects=False,
    )

    assert response.status_code == 404

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    db = TestingSessionLocal()

    project = db.get(
        models.Project,
        foreign_project_id,
    )

    assert project.name == (
        "Проект пользователя 2"
    )

    db.close()


def test_user_cannot_edit_foreign_alternative(
    client: TestClient,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    foreign_alternative_id = (
        test_environment[
            "alternative_2_id"
        ]
    )

    response = client.post(
        (
            "/alternatives/"
            f"{foreign_alternative_id}/edit"
        ),
        data={
            "name": "Чужая изменённая альтернатива",
        },
        follow_redirects=False,
    )

    assert response.status_code == 404

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    db = TestingSessionLocal()

    alternative = db.get(
        models.Alternative,
        foreign_alternative_id,
    )

    assert alternative.name == (
        "Альтернатива пользователя 2"
    )

    db.close()


def test_user_cannot_delete_foreign_criterion(
    client: TestClient,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    foreign_criterion_id = (
        test_environment[
            "criterion_2_id"
        ]
    )

    response = client.post(
        (
            "/criteria/"
            f"{foreign_criterion_id}/delete"
        ),
        follow_redirects=False,
    )

    assert response.status_code == 404

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    db = TestingSessionLocal()

    criterion = db.get(
        models.Criterion,
        foreign_criterion_id,
    )

    assert criterion is not None

    db.close()


def test_new_project_gets_current_user_as_owner(
    client: TestClient,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    response = client.post(
        "/projects",
        data={
            "project_name": "Новый личный проект",
            "project_description": (
                "Тестовое описание проекта"
            ),
        },
    )

    assert response.status_code == 200

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    db = TestingSessionLocal()

    project = (
        db.query(models.Project)
        .filter(
            models.Project.name
            == "Новый личный проект"
        )
        .one()
    )

    assert project.owner_id == (
        test_environment[
            "user_1_id"
        ]
    )

    assert project.description == (
        "Тестовое описание проекта"
    )

    db.close()

def test_ai_alternatives_require_project_owner(
    client,
    test_environment,
    monkeypatch,
):
    login(
        client,
        "user1@test.com",
    )

    foreign_project_id = (
        test_environment["project_2_id"]
    )

    called = False

    def fake_generate(*args, **kwargs):
        nonlocal called
        called = True

        return LLMResponse(
            content='{"s":"ok","i":[]}',
            provider="test",
            model="test-model",
            usage=LLMUsage(
                input_tokens=1,
                output_tokens=1,
                reasoning_tokens=0,
                total_tokens=2,
            ),
        )

    monkeypatch.setattr(
        ai_alternative_service.llm_service,
        "generate",
        fake_generate,
    )

    response = client.post(
        (
            f"/projects/{foreign_project_id}"
            "/ai/alternatives"
        )
    )

    assert response.status_code == 404
    assert called is False


def test_ai_alternatives_return_insufficient_context(
    client,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    project_id = (
        test_environment["project_1_id"]
    )

    response = client.post(
        (
            f"/projects/{project_id}"
            "/ai/alternatives"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["status"]
        == "insufficient_context"
    )

    assert data["items"] == []


def test_ai_alternatives_return_llm_suggestions(
    client,
    test_environment,
    monkeypatch,
):
    login(
        client,
        "user1@test.com",
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    db = TestingSessionLocal()

    project = db.get(
        models.Project,
        project_id,
    )

    project.description = (
        "Выбор семейного автомобиля. "
        "Бюджет до 4 млн рублей."
    )

    db.commit()
    db.close()

    def fake_generate(
        *,
        system_prompt,
        user_prompt,
        max_output_tokens,
        temperature,
        json_mode,
    ):
        assert json_mode is True
        assert "семейного автомобиля" in (
            user_prompt
        )

        return LLMResponse(
            content=json.dumps(
                {
                    "s": "ok",
                    "i": [
                        {
                            "n": "Toyota Camry",
                            "r": (
                                "Надёжный семейный "
                                "автомобиль."
                            ),
                        },
                        {
                            "n": (
                                "Альтернатива "
                                "пользователя 1"
                            ),
                            "r": (
                                "Дубликат уже "
                                "существующего варианта."
                            ),
                        },
                    ],
                },
                ensure_ascii=False,
            ),
            provider="test-provider",
            model="test-model",
            usage=LLMUsage(
                input_tokens=100,
                output_tokens=50,
                reasoning_tokens=10,
                total_tokens=150,
            ),
        )

    monkeypatch.setattr(
        ai_alternative_service.llm_service,
        "generate",
        fake_generate,
    )

    response = client.post(
        (
            f"/projects/{project_id}"
            "/ai/alternatives"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert data["items"] == [
        {
            "name": "Toyota Camry",
            "explanation": (
                "Надёжный семейный "
                "автомобиль."
            ),
        }
    ]

    assert (
        data["usage"]["provider"]
        == "test-provider"
    )

    assert (
        data["usage"]["total_tokens"]
        == 150
    )


def test_accept_ai_alternatives_saves_ai_metadata(
    client,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    project_id = (
        test_environment["project_1_id"]
    )

    response = client.post(
        (
            f"/projects/{project_id}"
            "/ai/alternatives/accept"
        ),
        json={
            "items": [
                {
                    "name": "Toyota Camry",
                    "explanation": (
                        "Надёжный семейный "
                        "автомобиль."
                    ),
                }
            ]
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "created": 1,
    }

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    db = TestingSessionLocal()

    alternative = (
        db.query(models.Alternative)
        .filter(
            models.Alternative.name
            == "Toyota Camry"
        )
        .one()
    )

    assert (
        alternative.project_id
        == project_id
    )

    assert (
        alternative.ai_suggested_name
        == "Toyota Camry"
    )

    assert (
        alternative.ai_explanation
        == (
            "Надёжный семейный "
            "автомобиль."
        )
    )

    db.close()


def test_accept_ai_alternatives_does_not_duplicate_existing(
    client,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    project_id = (
        test_environment["project_1_id"]
    )

    response = client.post(
        (
            f"/projects/{project_id}"
            "/ai/alternatives/accept"
        ),
        json={
            "items": [
                {
                    "name": (
                        "Альтернатива "
                        "пользователя 1"
                    ),
                    "explanation": (
                        "Попытка создать "
                        "дубликат."
                    ),
                }
            ]
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "created": 0,
    }

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    db = TestingSessionLocal()

    count = (
        db.query(models.Alternative)
        .filter(
            models.Alternative.project_id
            == project_id,
            models.Alternative.name
            == (
                "Альтернатива "
                "пользователя 1"
            ),
        )
        .count()
    )

    assert count == 1

    db.close()


def test_ai_criteria_require_project_owner(
    client,
    test_environment,
    monkeypatch,
):
    login(
        client,
        "user1@test.com",
    )

    foreign_project_id = (
        test_environment["project_2_id"]
    )

    called = False

    def fake_generate(*args, **kwargs):
        nonlocal called
        called = True

        return LLMResponse(
            content='{"s":"ok","i":[]}',
            provider="test",
            model="test-model",
            usage=LLMUsage(
                input_tokens=1,
                output_tokens=1,
                reasoning_tokens=0,
                total_tokens=2,
            ),
        )

    monkeypatch.setattr(
        ai_criterion_service.llm_service,
        "generate",
        fake_generate,
    )

    response = client.post(
        (
            f"/projects/{foreign_project_id}"
            "/ai/criteria"
        )
    )

    assert response.status_code == 404
    assert called is False


def test_ai_criteria_return_insufficient_context(
    client,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    project_id = (
        test_environment["project_1_id"]
    )

    response = client.post(
        (
            f"/projects/{project_id}"
            "/ai/criteria"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["status"]
        == "insufficient_context"
    )

    assert data["items"] == []


def test_ai_criteria_return_llm_suggestions(
    client,
    test_environment,
    monkeypatch,
):
    login(
        client,
        "user1@test.com",
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    db = TestingSessionLocal()

    project = db.get(
        models.Project,
        project_id,
    )

    project.description = (
        "Выбор семейного автомобиля. "
        "Важны безопасность и стоимость владения."
    )

    existing_criterion = db.get(
        models.Criterion,
        test_environment[
            "criterion_1_id"
        ],
    )

    existing_criterion.weight = 0.3
    
    db.commit()
    db.close()

    def fake_generate(
        *,
        system_prompt,
        user_prompt,
        max_output_tokens,
        temperature,
        json_mode,
    ):
        assert json_mode is True

        return LLMResponse(
            content=json.dumps(
                {
                    "s": "ok",
                    "i": [
                        {
                            "n": "Безопасность",
                            "w": 40,
                            "cr": (
                                "Ключевой фактор "
                                "для семейного автомобиля."
                            ),
                            "wr": (
                                "Высокий вес из-за "
                                "приоритета безопасности."
                            ),
                        },
                        {
                            "n": (
                                "Критерий "
                                "пользователя 1"
                            ),
                            "w": 10,
                            "cr": "Дубликат.",
                            "wr": "Дубликат.",
                        },
                    ],
                },
                ensure_ascii=False,
            ),
            provider="test-provider",
            model="test-model",
            usage=LLMUsage(
                input_tokens=120,
                output_tokens=80,
                reasoning_tokens=20,
                total_tokens=200,
            ),
        )

    monkeypatch.setattr(
        ai_criterion_service.llm_service,
        "generate",
        fake_generate,
    )

    response = client.post(
        (
            f"/projects/{project_id}"
            "/ai/criteria"
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert data["items"] == [
        {
            "name": "Безопасность",
            "weight_percent": 40.0,
            "criterion_explanation": (
                "Ключевой фактор "
                "для семейного автомобиля."
            ),
            "weight_explanation": (
                "Высокий вес из-за "
                "приоритета безопасности."
            ),
        }
    ]

    assert (
        data["usage"]["total_tokens"]
        == 200
    )


def test_accept_ai_criteria_preserves_original_ai_weight(
    client,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    db = TestingSessionLocal()

    existing_criterion = db.get(
        models.Criterion,
        test_environment["criterion_1_id"],
    )

    existing_criterion.weight = 0.2

    db.commit()
    db.close()

    response = client.post(
        (
            f"/projects/{project_id}"
            "/ai/criteria/accept"
        ),
        json={
            "items": [
                {
                    "name": "Безопасность",
                    "weight_percent": 35,
                    "ai_suggested_weight_percent": 25,
                    "criterion_explanation": (
                        "Важный фактор "
                        "для семейного автомобиля."
                    ),
                    "weight_explanation": (
                        "ИИ предложил вес 25%."
                    ),
                }
            ]
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "created": 1,
    }

    db = TestingSessionLocal()

    criterion = (
        db.query(models.Criterion)
        .filter(
            models.Criterion.name
            == "Безопасность"
        )
        .one()
    )

    assert criterion.weight == 0.35
    assert (
        criterion.ai_suggested_weight
        == 0.25
    )

    assert (
        criterion.ai_suggested_name
        == "Безопасность"
    )

    db.close()


def test_edit_criterion_cannot_exceed_total_weight(
    client,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    criterion_id = (
        test_environment[
            "criterion_1_id"
        ]
    )

    db = TestingSessionLocal()

    second = models.Criterion(
        name="Второй критерий",
        weight=0.6,
        project_id=project_id,
    )

    criterion = db.get(
        models.Criterion,
        criterion_id,
    )

    criterion.weight = 0.4

    db.add(second)
    db.commit()
    db.close()

    response = client.post(
        (
            f"/criteria/{criterion_id}"
            "/edit"
        ),
        data={
            "name": "Первый критерий",
            "weight_percent": 50,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    assert (
        response.headers["location"]
        == (
            f"/projects/{project_id}"
            "?weight_error=1"
        )
    )

    db = TestingSessionLocal()

    criterion = db.get(
        models.Criterion,
        criterion_id,
    )

    assert criterion.weight == 0.4

    db.close()

def test_ai_scores_require_project_owner(
    client,
    test_environment,
    monkeypatch,
):
    login(
        client,
        "user1@test.com",
    )

    foreign_project_id = (
        test_environment["project_2_id"]
    )

    called = False

    def fake_generate(*args, **kwargs):
        nonlocal called
        called = True

        return LLMResponse(
            content='{"s":"ok","i":[]}',
            provider="test",
            model="test-model",
            usage=LLMUsage(
                input_tokens=1,
                output_tokens=1,
                reasoning_tokens=0,
                total_tokens=2,
            ),
        )

    monkeypatch.setattr(
        ai_score_service.llm_service,
        "generate",
        fake_generate,
    )

    response = client.post(
        (
            f"/projects/{foreign_project_id}"
            "/ai/scores"
        )
    )

    assert response.status_code == 404
    assert called is False


def test_ai_scores_do_not_send_existing_scores_to_llm(
    client,
    test_environment,
    monkeypatch,
):
    login(
        client,
        "user1@test.com",
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    alternative_id = (
        test_environment[
            "alternative_1_id"
        ]
    )

    criterion_id = (
        test_environment[
            "criterion_1_id"
        ]
    )

    db = TestingSessionLocal()

    project = db.get(
        models.Project,
        project_id,
    )

    project.description = (
        "Тестовый проект для выбора варианта."
    )

    score = models.Score(
        alternative_id=alternative_id,
        criterion_id=criterion_id,
        value=9.0,
        ai_value=3.0,
        ai_explanation="Старая оценка ИИ.",
    )

    db.add(score)
    db.commit()
    db.close()

    def fake_generate(
        *,
        system_prompt,
        user_prompt,
        max_output_tokens,
        temperature,
        json_mode,
    ):
        assert "9.0" not in user_prompt
        assert "3.0" not in user_prompt
        assert "Старая оценка ИИ" not in user_prompt

        return LLMResponse(
            content=json.dumps(
                {
                    "s": "ok",
                    "i": [
                        {
                            "a": alternative_id,
                            "c": criterion_id,
                            "v": 7,
                            "r": "Новая независимая оценка.",
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            provider="test",
            model="test-model",
            usage=LLMUsage(
                input_tokens=100,
                output_tokens=50,
                reasoning_tokens=10,
                total_tokens=160,
            ),
        )

    monkeypatch.setattr(
        ai_score_service.llm_service,
        "generate",
        fake_generate,
    )

    response = client.post(
        (
            f"/projects/{project_id}"
            "/ai/scores"
        )
    )

    assert response.status_code == 200

    db = TestingSessionLocal()

    score = (
        db.query(models.Score)
        .filter(
            models.Score.alternative_id
            == alternative_id,
            models.Score.criterion_id
            == criterion_id,
        )
        .one()
    )

    assert score.value == 9.0
    assert score.ai_value == 7.0
    assert (
        score.ai_explanation
        == "Новая независимая оценка."
    )

    db.close()


def test_ai_score_is_used_when_value_is_not_confirmed(
    test_environment,
):
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    alternative_id = (
        test_environment[
            "alternative_1_id"
        ]
    )

    criterion_id = (
        test_environment[
            "criterion_1_id"
        ]
    )

    db = TestingSessionLocal()

    criterion = db.get(
        models.Criterion,
        criterion_id,
    )

    criterion.weight = 1.0

    score = models.Score(
        alternative_id=alternative_id,
        criterion_id=criterion_id,
        value=None,
        ai_value=7.5,
        ai_explanation="Предложение ИИ.",
    )

    db.add(score)
    db.commit()

    results = (
        calculation_service
        .calculate_results(
            db=db,
            project_id=project_id,
        )
    )

    result = next(
        item
        for item in results
        if item["alternative"].id
        == alternative_id
    )

    assert result["total"] == 7.5

    db.close()


def test_confirmed_value_has_priority_over_ai_value(
    test_environment,
):
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    alternative_id = (
        test_environment[
            "alternative_1_id"
        ]
    )

    criterion_id = (
        test_environment[
            "criterion_1_id"
        ]
    )

    db = TestingSessionLocal()

    criterion = db.get(
        models.Criterion,
        criterion_id,
    )

    criterion.weight = 1.0

    score = models.Score(
        alternative_id=alternative_id,
        criterion_id=criterion_id,
        value=9.0,
        ai_value=4.0,
        ai_explanation="Предложение ИИ.",
    )

    db.add(score)
    db.commit()

    results = (
        calculation_service
        .calculate_results(
            db=db,
            project_id=project_id,
        )
    )

    result = next(
        item
        for item in results
        if item["alternative"].id
        == alternative_id
    )

    assert result["total"] == 9.0

    db.close()


def test_saving_matrix_confirms_ai_value(
    client,
    test_environment,
):
    login(
        client,
        "user1@test.com",
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    alternative_id = (
        test_environment[
            "alternative_1_id"
        ]
    )

    criterion_id = (
        test_environment[
            "criterion_1_id"
        ]
    )

    db = TestingSessionLocal()

    score = models.Score(
        alternative_id=alternative_id,
        criterion_id=criterion_id,
        value=None,
        ai_value=7.0,
        ai_explanation="Предложение ИИ.",
    )

    db.add(score)
    db.commit()
    db.close()

    response = client.post(
        f"/projects/{project_id}/scores",
        data={
            (
                f"score_{alternative_id}_"
                f"{criterion_id}"
            ): "7"
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    db = TestingSessionLocal()

    score = (
        db.query(models.Score)
        .filter(
            models.Score.alternative_id
            == alternative_id,
            models.Score.criterion_id
            == criterion_id,
        )
        .one()
    )

    assert score.value == 7.0
    assert score.ai_value == 7.0
    assert (
        score.ai_explanation
        == "Предложение ИИ."
    )

    db.close()
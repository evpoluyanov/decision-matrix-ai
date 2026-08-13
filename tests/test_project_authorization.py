import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


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
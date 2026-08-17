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
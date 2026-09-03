"""The report question is answered once per account, not once per project."""
import io

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from app import models
from app.services import feedback_service, growth_service
from conftest import TEST_PASSWORD


QUESTION = "Насколько Decision Matrix AI помог вам принять решение?"


@pytest.fixture
def report_user(client, test_environment):
    env = test_environment
    with env["TestingSessionLocal"]() as db:
        user = db.get(models.User, env["user_1_id"])
        user.email_verified = True
        db.add(models.Score(alternative_id=env["alternative_1_id"],
                            criterion_id=env["criterion_1_id"], value=8))
        db.commit()
        growth_service.record_trial_ai_project(db, user_id=user.id, project_id=env["project_1_id"])
    client.post("/login", data={"email": "user1@test.com", "password": TEST_PASSWORD})
    return f'/projects/{env["project_1_id"]}/report'


def answer(client, env, **overrides):
    data = {"quick": "true", "category": "result_quality", "rating": "5",
            "project_id": env["project_1_id"], "message": "", "page_path": "/untrusted-path"}
    data.update(overrides)
    return client.post("/feedback", data=data, follow_redirects=False)


def test_viewing_or_generic_feedback_does_not_answer_question(client, test_environment, report_user):
    for _ in range(2):
        assert QUESTION in client.get(report_user).text
    # Even feedback from this report is not the dedicated question going forward.
    for category in ("bug", "result_quality"):
        response = client.post("/feedback", data={
            "category": category, "rating": "4", "message": "Обычный отзыв через общую форму",
            "page_path": report_user, "project_id": test_environment["project_1_id"],
        })
        assert response.status_code == 200
        assert QUESTION in client.get(report_user).text
    assert client.get("/feedback/report-question/state").json() == {"answered": False}


@pytest.mark.parametrize("message", ["", "Да"])
def test_saved_answer_hides_question_after_refresh_login_and_status_change(
    client, test_environment, report_user, message,
):
    assert answer(client, test_environment, message=message).status_code == 303
    assert QUESTION not in client.get(report_user).text
    with test_environment["TestingSessionLocal"]() as db:
        row = db.query(models.UserFeedback).one()
        assert row.message == (message or "Оценка итогового отчёта.")
        assert row.page_path == report_user
        assert row.question_key == feedback_service.REPORT_QUESTION_KEY
        feedback_service.update_status(db, feedback_id=row.id, status="rejected", admin_note="Проверено")
        # Losing the association with a removed project must not reset the answer.
        row.project_id = None
        db.commit()
        assert feedback_service.has_report_answer(db, test_environment["user_1_id"])
    client.cookies.clear()
    client.post("/login", data={"email": "user1@test.com", "password": TEST_PASSWORD})
    for _ in range(2):
        assert QUESTION not in client.get(report_user).text
    state = client.get("/feedback/report-question/state")
    assert state.json() == {"answered": True}
    assert "no-store" in state.headers["cache-control"]
    # The permanent general feedback form remains available after this answer.
    assert client.post("/feedback", data={"category": "idea", "message": "Другая полезная идея"}).status_code == 200


def test_duplicate_old_tab_submission_keeps_first_answer_and_does_not_consume_limit(
    client, test_environment, report_user, monkeypatch,
):
    monkeypatch.setenv("FEEDBACK_USER_LIMIT", "1")
    first = answer(client, test_environment)
    assert "feedback_submitted=1" in first.headers["location"]
    for _ in range(3):
        duplicate = answer(client, test_environment, rating="1", message="Другой ответ")
        assert duplicate.status_code == 303
        assert duplicate.headers["location"] == report_user
    with test_environment["TestingSessionLocal"]() as db:
        row = db.query(models.UserFeedback).one()
        assert row.rating == 5
        assert row.message == "Оценка итогового отчёта."


def test_answer_is_account_wide_but_does_not_affect_another_user(
    client, test_environment, report_user, monkeypatch,
):
    assert answer(client, test_environment).status_code == 303
    with test_environment["TestingSessionLocal"]() as db:
        other = db.get(models.Project, test_environment["project_2_id"])
        other.owner_id = test_environment["user_1_id"]
        alternative = db.query(models.Alternative).filter_by(project_id=other.id).one()
        criterion = db.query(models.Criterion).filter_by(project_id=other.id).one()
        db.add(models.Score(alternative_id=alternative.id, criterion_id=criterion.id, value=7))
        db.commit()
    # Deliberately make another report eligible, so the assertion is not merely
    # satisfied by the existing first-trial-project visibility condition.
    monkeypatch.setattr(growth_service, "first_trial_project_id", lambda db, uid: test_environment["project_2_id"])
    other_report = f'/projects/{test_environment["project_2_id"]}/report'
    assert QUESTION not in client.get(other_report).text
    duplicate = answer(client, test_environment, project_id=test_environment["project_2_id"])
    assert duplicate.status_code == 303
    assert "feedback_submitted" not in duplicate.headers["location"]
    with test_environment["TestingSessionLocal"]() as db:
        other = db.get(models.Project, test_environment["project_2_id"])
        other.owner_id = test_environment["user_2_id"]
        db.get(models.User, test_environment["user_2_id"]).email_verified = True
        db.commit()
        assert db.query(models.UserFeedback).count() == 1
    client.cookies.clear()
    client.post("/login", data={"email": "user2@test.com", "password": TEST_PASSWORD})
    assert client.get("/feedback/report-question/state").json() == {"answered": False}
    assert QUESTION in client.get(other_report).text


@pytest.mark.parametrize("invalid,status", [
    ({"rating": ""}, 400), ({"rating": "6"}, 400),
    ({"message": "x" * 2001}, 400), ({"category": "bug"}, 400),
    ({"project_id": ""}, 400),
])
def test_invalid_answer_does_not_dismiss_question(client, test_environment, report_user, invalid, status):
    assert answer(client, test_environment, **invalid).status_code == status
    assert QUESTION in client.get(report_user).text
    assert client.get("/feedback/report-question/state").json() == {"answered": False}


def test_rate_limited_or_foreign_project_answer_does_not_dismiss(
    client, test_environment, report_user, monkeypatch,
):
    assert answer(client, test_environment, project_id=test_environment["project_2_id"]).status_code == 404
    monkeypatch.setenv("FEEDBACK_USER_LIMIT", "1")
    client.post("/feedback", data={"category": "other", "message": "Достаточно длинный обычный отзыв"})
    assert answer(client, test_environment).status_code == 429
    assert QUESTION in client.get(report_user).text
    assert client.get("/feedback/report-question/state").json() == {"answered": False}


def test_question_state_and_submission_require_login(client, test_environment):
    assert client.get("/feedback/report-question/state", follow_redirects=False).status_code == 303
    assert answer(client, test_environment).status_code == 303
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.UserFeedback).count() == 0


def test_database_error_does_not_mark_answer(client, test_environment, report_user, monkeypatch):
    session_type = test_environment["TestingSessionLocal"].class_
    original = session_type.commit

    def fail_feedback_commit(db):
        if any(isinstance(row, models.UserFeedback) for row in db.new):
            raise IntegrityError("test insert", {}, Exception("simulated write failure"))
        return original(db)

    monkeypatch.setattr(session_type, "commit", fail_feedback_commit)
    with pytest.raises(IntegrityError):
        answer(client, test_environment)
    assert client.get("/feedback/report-question/state").json() == {"answered": False}
    assert QUESTION in client.get(report_user).text


def test_migration_preserves_legacy_answers_and_general_feedback(tmp_path, monkeypatch):
    url = f'sqlite:///{tmp_path / "answers.db"}'
    monkeypatch.setenv("MIGRATION_DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "d2f48ab17390")
    engine = create_engine(url)
    with engine.begin() as connection:
        for uid in range(1, 5):
            connection.execute(text("INSERT INTO users (id,email,password_hash,email_verified) VALUES (:id,:email,'test',1)"),
                               {"id": uid, "email": f"legacy{uid}@example.com"})
        for uid, category, rating, path in [
            (1, "bug", 4, "/projects/1/report"),
            (1, "result_quality", 5, "/projects/1/report"),
            (1, "result_quality", 4, "/projects/2/report"),
            (2, "result_quality", 5, "/feedback"),
            (3, "result_quality", None, "/projects/3/report"),
            (4, "result_quality", 3, "/projects/4/report"),
        ]:
            connection.execute(text("INSERT INTO user_feedback (user_id,category,rating,message,page_path,allow_email_reply,status) "
                                    "VALUES (:uid,:category,:rating,'Legacy feedback',:path,0,'new')"),
                               {"uid": uid, "category": category, "rating": rating, "path": path})
    for _ in range(2):
        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT COUNT(*) FROM user_feedback")) == 6
            assert connection.execute(text("SELECT user_id,rating FROM user_feedback WHERE question_key IS NOT NULL ORDER BY user_id")).all() == [(1, 5), (4, 3)]
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text("INSERT INTO user_feedback (user_id,category,rating,message,page_path,allow_email_reply,status,question_key) "
                                    "VALUES (1,'result_quality',1,'Duplicate','/projects/1/report',0,'new','report_helpfulness_v1')"))
        command.downgrade(config, "d2f48ab17390")
    engine.dispose()


def test_report_answer_postgresql_migration_is_additive(monkeypatch):
    monkeypatch.setenv("MIGRATION_DATABASE_URL", "postgresql+psycopg://unused:unused@localhost/unused")
    output = io.StringIO()
    command.upgrade(Config("alembic.ini", output_buffer=output), "d2f48ab17390:f4c912ab670e", sql=True)
    sql = output.getvalue()
    assert "ADD COLUMN question_key VARCHAR(40)" in sql
    assert "uq_feedback_user_question" in sql
    assert "GROUP BY user_id" in sql
    assert "DROP TABLE" not in sql and "DELETE FROM" not in sql

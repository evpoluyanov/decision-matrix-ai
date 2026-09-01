from datetime import datetime, timedelta, timezone

from app import models
from app.services import admin_service, growth_service, mws_reconciliation_service
from conftest import TEST_PASSWORD


def login(client):
    client.post("/login", data={"email": "user1@test.com", "password": TEST_PASSWORD})


def test_feedback_requires_login_and_escapes_html_in_admin(client, test_environment, monkeypatch):
    assert client.get("/feedback", follow_redirects=False).status_code == 303
    with test_environment["TestingSessionLocal"]() as db:
        user = db.get(models.User, test_environment["user_1_id"])
        user.email_verified = True
        db.commit()
    login(client)
    message = '<script>alert("xss")</script> полезный отзыв'
    response = client.post("/feedback", data={
        "category": "bug", "rating": "4", "message": message,
        "page_path": "/projects/1", "project_id": test_environment["project_1_id"],
        "allow_email_reply": "true", "return_to": "/feedback",
    }, follow_redirects=False)
    assert response.status_code == 303
    monkeypatch.setenv("ADMIN_USER_IDS", str(test_environment["user_1_id"]))
    admin = client.get("/admin")
    assert admin.status_code == 200
    assert "&lt;script&gt;" in admin.text
    assert '<script>alert("xss")</script>' not in admin.text
    with test_environment["TestingSessionLocal"]() as db:
        feedback = db.query(models.UserFeedback).one()
        assert feedback.message == message
        assert feedback.allow_email_reply is True


def test_feedback_rate_limit_stops_spam(client, test_environment, monkeypatch):
    monkeypatch.setenv("FEEDBACK_USER_LIMIT", "1")
    login(client)
    data = {"category": "idea", "message": "Достаточно длинное сообщение", "page_path": "/feedback"}
    assert client.post("/feedback", data=data).status_code == 200
    assert client.post("/feedback", data=data).status_code == 429


def test_beta_reward_requires_verified_result_and_feedback(client, test_environment):
    with test_environment["TestingSessionLocal"]() as db:
        user = db.get(models.User, test_environment["user_1_id"])
        user.email_verified = True
        growth_service.record_trial_ai_project(
            db, user_id=user.id, project_id=test_environment["project_1_id"],
        )
        growth_service.record_project_value(
            db, user=user, project_id=test_environment["project_1_id"], results=[object()],
        )
    login(client)
    client.post("/feedback", data={
        "category": "result_quality", "rating": "5",
        "message": "Результат оказался полезным", "page_path": "/feedback",
    })
    with test_environment["TestingSessionLocal"]() as db:
        user = db.get(models.User, test_environment["user_1_id"])
        assert user.beta_reward_eligible is True
        assert user.beta_reward_reason == "verified_result_and_feedback"
        assert user.beta_reward_granted is False


def test_feedback_goal_contains_no_text_or_identifiers(client, test_environment, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    monkeypatch.setenv("YANDEX_METRIKA_ID", "123")
    login(client)
    response = client.post("/feedback", data={
        "category": "interface", "rating": "3", "message": "Секретный текст отзыва",
        "page_path": "/feedback", "return_to": "/feedback",
    }, follow_redirects=True, headers={"Host": "dmatrix.tech", "Origin": "http://dmatrix.tech"})
    assert "feedback_submitted" in response.text
    assert "interface" in response.text
    assert "Секретный текст отзыва" not in response.text
    goal_script = response.text.split("feedback_submitted", 1)[-1].split("</script>", 1)[0]
    assert "user_id" not in goal_script and "project_id" not in goal_script


def test_manual_mws_reconciliation_is_separate_from_estimate(test_environment):
    with test_environment["TestingSessionLocal"]() as db:
        now = datetime.now(timezone.utc)
        row = mws_reconciliation_service.add_manual(
            db, period_start=now - timedelta(days=1), period_end=now,
            input_tokens=1000, output_tokens=200, actual_base_cost_rub="1.5",
            discount_or_grant_rub="0.5", amount_due_rub="1.0",
            application_estimated_cost_rub="0.8", source="MWS console export",
        )
        assert str(row.deviation_rub) == "0.200000"
        stats = admin_service.statistics(db, "all")
        assert stats["latest_reconciliation"].id == row.id
        assert stats["estimated"] == 0

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app import models
from app.llm import service as llm_service
from app.services import auth_rate_limit_service as throttle
from app.services import email_service, email_verification_service
from conftest import TEST_PASSWORD

FEATURES = ["alternatives", "criteria", "scores", "result-explanation", "decision-risks"]


def login(client, email="user1@test.com", password=TEST_PASSWORD):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=False)


@pytest.mark.parametrize("feature", FEATURES)
def test_unverified_email_blocks_all_paid_features(client, test_environment, monkeypatch, feature):
    provider = Mock(side_effect=AssertionError("Paid call must not run"))
    monkeypatch.setattr(llm_service, "generate", provider)
    assert login(client).status_code == 303
    project = test_environment["project_1_id"]
    response = client.post(f"/projects/{project}/ai/{feature}")
    assert response.status_code == 403
    assert response.json()["status"] == "email_verification_required"
    provider.assert_not_called()
    assert client.get("/account").status_code == 200
    assert client.get(f"/projects/{project}").status_code == 200
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.AIRequestLog).count() == 0
        assert db.query(models.AIProviderCall).count() == 0


@pytest.mark.parametrize("feature", FEATURES)
def test_unverified_user_still_cannot_probe_foreign_projects(client, test_environment, feature):
    login(client)
    response = client.post(f'/projects/{test_environment["project_2_id"]}/ai/{feature}')
    assert response.status_code == 404


def test_verification_unlocks_existing_login_session(client, test_environment):
    login(client)
    token = email_verification_service.create_email_verification_token(user_id=test_environment["user_1_id"])
    assert client.post("/verify-email", data={"token": token}, follow_redirects=False).status_code == 303
    # Fixture description is empty: this is a valid, zero-provider-call response.
    response = client.post(f'/projects/{test_environment["project_1_id"]}/ai/alternatives')
    assert response.status_code == 200
    assert response.json()["status"] == "insufficient_context"


@pytest.mark.parametrize("origin", ["https://attacker.test", "null", "http://testserver.attacker.test", "http://user@testserver"])
def test_cross_origin_registration_is_rejected(client, test_environment, origin):
    response = client.post("/register", headers={"Origin": origin}, data={
        "email": "new@example.com", "password": TEST_PASSWORD, "password_confirmation": TEST_PASSWORD,
    })
    assert response.status_code == 403
    assert response.json()["status"] == "csrf_rejected"
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.User).count() == 2


def test_missing_origin_fails_closed_and_same_origin_referer_works(client):
    client.headers.pop("Origin")
    assert login(client).status_code == 403
    client.headers["Referer"] = "http://testserver/login"
    assert login(client).status_code == 303


def test_cross_site_metadata_and_wrong_port_are_rejected(client):
    client.headers["Sec-Fetch-Site"] = "cross-site"
    assert login(client).status_code == 403
    client.headers.pop("Sec-Fetch-Site")
    client.headers["Origin"] = "http://testserver:81"
    assert login(client).status_code == 403


def test_login_limit_is_account_wide_and_normalizes_email(client, monkeypatch):
    monkeypatch.setenv("AUTH_LOGIN_ACCOUNT_LIMIT", "2")
    assert login(client, password="wrong").status_code == 401
    assert login(client, email=" USER1@TEST.COM ", password="wrong").status_code == 401
    response = login(client)
    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 900
    assert "Слишком много" in response.text


def test_login_ip_limit_cannot_be_bypassed_by_email_or_forwarded_header(client, monkeypatch):
    monkeypatch.setenv("AUTH_LOGIN_IP_LIMIT", "2")
    for number in range(2):
        client.headers["X-Forwarded-For"] = f"192.0.2.{number + 1}"
        assert login(client, email=f"nobody{number}@example.com").status_code == 401
    client.headers["X-Forwarded-For"] = "198.51.100.9"
    assert login(client).status_code == 429


def test_register_limit_precedes_mail_and_user_creation(client, test_environment, monkeypatch):
    monkeypatch.setenv("AUTH_REGISTER_IP_LIMIT", "1")
    send = Mock()
    monkeypatch.setattr(email_verification_service, "send_email_verification_message", send)
    data = {"email": "first@example.com", "password": TEST_PASSWORD, "password_confirmation": TEST_PASSWORD}
    assert client.post("/register", data=data, follow_redirects=False).status_code == 303
    data["email"] = "second@example.com"
    assert client.post("/register", data=data).status_code == 429
    assert send.call_count == 1
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.User).count() == 3
        keys = [row.key for row in db.query(models.AuthRateLimit)]
        assert all(len(key) == 64 and "@" not in key for key in keys)


def test_auth_window_expires_and_blocked_attempts_do_not_extend_it(test_environment):
    now = datetime(2026, 8, 28, 10, tzinfo=timezone.utc)
    with test_environment["TestingSessionLocal"]() as db:
        args = dict(scope="login", identity="a@example.com", limit=1, seconds=60)
        throttle.consume(db, now=now, **args)
        with pytest.raises(HTTPException) as error:
            throttle.consume(db, now=now + timedelta(seconds=59), **args)
        assert error.value.headers["Retry-After"] == "1"
        throttle.consume(db, now=now + timedelta(seconds=60), **args)
        assert db.query(models.AuthRateLimit).one().attempts == 1


def test_vercel_ip_is_trusted_only_in_vercel_and_ipv6_is_grouped(monkeypatch):
    request = Request({"type": "http", "client": ("192.0.2.1", 100), "headers": [
        (b"x-vercel-forwarded-for", b"2001:db8:1:2::99"),
    ]})
    assert throttle.client_address(request) == "192.0.2.1"
    monkeypatch.setenv("VERCEL", "1")
    assert throttle.client_address(request) == "2001:db8:1:2::/64"
    request = Request({"type": "http", "client": ("192.0.2.1", 100), "headers": []})
    with pytest.raises(HTTPException) as error:
        throttle.client_address(request)
    assert error.value.status_code == 503


def test_resend_is_authenticated_and_throttled(client, monkeypatch):
    assert client.post("/account/resend-verification", follow_redirects=False).status_code == 303
    login(client)
    monkeypatch.setenv("AUTH_RESEND_USER_LIMIT", "1")
    send = Mock()
    monkeypatch.setattr(email_verification_service, "send_email_verification_message", send)
    assert client.post("/account/resend-verification").status_code == 200
    assert client.post("/account/resend-verification").status_code == 429
    assert send.call_count == 1
    assert send.call_args.kwargs["recipient_email"] == "user1@test.com"


def test_resend_failure_is_displayed_without_secrets(client, monkeypatch):
    login(client)
    send = Mock(side_effect=email_service.EmailServiceError("SECRET"))
    monkeypatch.setattr(email_verification_service, "send_email_verification_message", send)
    response = client.post("/account/resend-verification")
    assert response.status_code == 200
    assert "Не удалось отправить" in response.text
    assert "SECRET" not in response.text


def test_admin_requires_verified_allowlisted_user(client, test_environment, monkeypatch):
    assert client.get("/admin", follow_redirects=False).status_code == 303
    login(client)
    monkeypatch.setenv("ADMIN_USER_IDS", str(test_environment["user_1_id"]))
    assert client.get("/admin").status_code == 403
    with test_environment["TestingSessionLocal"]() as db:
        db.get(models.User, test_environment["user_1_id"]).email_verified = True
        db.commit()
    response = client.get("/admin")
    assert response.status_code == 200
    assert "private, no-store" == response.headers["Cache-Control"]
    assert "noindex" in response.headers["X-Robots-Tag"]
    assert "user2@test.com" not in response.text
    assert "Статистика сервиса" in client.get("/account").text
    assert client.get("/admin?days=365").status_code == 422
    monkeypatch.setenv("ADMIN_USER_IDS", "")
    assert client.get("/admin").status_code == 403


def test_admin_can_see_configuration_errors_without_enabling_ai(client, test_environment, verified_users, monkeypatch):
    login(client)
    monkeypatch.setenv("ADMIN_USER_IDS", str(test_environment["user_1_id"]))
    monkeypatch.setenv("AI_DAILY_BUDGET_RUB", "not-a-budget")
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Некорректная настройка AI_DAILY_BUDGET_RUB" in response.text
    assert "не рассчитано" in response.text
    response = client.post(f'/projects/{test_environment["project_1_id"]}/ai/alternatives')
    assert response.status_code == 503


@pytest.mark.parametrize("path", ["/login", "/register", "/account", "/admin", "/verify-email?token=secret"])
def test_sensitive_pages_are_not_cached_or_indexed(client, path):
    response = client.get(path, follow_redirects=False)
    assert response.headers["Cache-Control"] == "private, no-store"
    assert response.headers["X-Robots-Tag"] == "noindex, nofollow"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["X-Frame-Options"] == "DENY"

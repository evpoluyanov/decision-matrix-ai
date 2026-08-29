"""Form-flow regressions without the client's default synthetic Origin.

TestClient is not a browser. Assert the response policy explicitly, then send
the origin-only headers produced by strict-origin for same-origin form POSTs.
A real-browser smoke test is still required after deployment.
"""

from html.parser import HTMLParser
from unittest.mock import Mock

import pytest

from app import models
from app.services import email_verification_service
from conftest import TEST_PASSWORD


class Forms(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.forms = {}
        self.current = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.current = {"method": attrs.get("method", "get"), "data": {}}
            self.forms[attrs.get("action", "")] = self.current
        elif tag == "input" and self.current is not None and attrs.get("name"):
            self.current["data"][attrs["name"]] = attrs.get("value", "")

    def handle_endtag(self, tag):
        if tag == "form":
            self.current = None


@pytest.fixture(params=["http", "https"])
def form_client(client, request):
    client.headers.pop("Origin")
    client.base_url = f"{request.param}://testserver"
    return client


def submit_form(client, page, action, data=None):
    assert page.status_code == 200
    # no-referrer makes native form POSTs send Origin: null, unlike fetch().
    assert page.headers["Referrer-Policy"] == "strict-origin"
    form = Forms(page.text).forms[action]
    assert form["method"].lower() == "post"
    origin = f"{page.url.scheme}://{page.url.netloc.decode()}"
    return client.post(
        action,
        data={**form["data"], **(data or {})},
        headers={
            "Origin": origin,
            "Referer": origin + "/",  # No path or verification token.
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
        },
        follow_redirects=False,
    )


def sign_in(client):
    response = submit_form(client, client.get("/login"), "/login", {
        "email": "user1@test.com", "password": TEST_PASSWORD,
    })
    assert response.status_code == 303
    assert response.headers["location"] == "/account"


def test_login_and_logout_forms_clear_session(form_client):
    sign_in(form_client)
    response = submit_form(form_client, form_client.get("/account"), "/logout")
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "decision_matrix_session" not in form_client.cookies
    account = form_client.get("/account", follow_redirects=False)
    assert account.status_code == 303
    assert account.headers["location"] == "/login"


def test_registration_form_creates_user(form_client, test_environment, monkeypatch):
    send = Mock()
    monkeypatch.setattr(email_verification_service, "send_email_verification_message", send)
    response = submit_form(form_client, form_client.get("/register"), "/register", {
        "email": "new@example.com", "password": TEST_PASSWORD,
        "password_confirmation": TEST_PASSWORD,
    })
    assert response.status_code == 303
    send.assert_called_once()
    with test_environment["TestingSessionLocal"]() as db:
        user = db.query(models.User).filter_by(email="new@example.com").one()
        assert user.email_verified is False


def test_verification_form_uses_hidden_token(form_client, test_environment):
    user_id = test_environment["user_1_id"]
    token = email_verification_service.create_email_verification_token(user_id=user_id)
    page = form_client.get("/verify-email", params={"token": token})
    response = submit_form(form_client, page, "/verify-email")
    assert response.status_code == 303
    assert response.headers["location"] == "/verify-email/result"
    with test_environment["TestingSessionLocal"]() as db:
        assert db.get(models.User, user_id).email_verified is True


def test_resend_verification_form(form_client, monkeypatch):
    send = Mock()
    monkeypatch.setattr(email_verification_service, "send_email_verification_message", send)
    sign_in(form_client)
    response = submit_form(
        form_client, form_client.get("/account"), "/account/resend-verification",
    )
    assert response.status_code == 303
    send.assert_called_once()


def test_logout_behind_vercel_https_proxy(client, monkeypatch):
    client.headers.pop("Origin")
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("VERCEL_ENV", "production")
    headers = {
        "Origin": "https://testserver", "Referer": "https://testserver/",
        "Sec-Fetch-Site": "same-origin", "X-Vercel-Forwarded-For": "192.0.2.1",
    }
    # ASGI sees HTTP behind the TLS-terminating edge; browser origin is HTTPS.
    response = client.post("/login", headers=headers, data={
        "email": "user1@test.com", "password": TEST_PASSWORD,
    }, follow_redirects=False)
    assert response.status_code == 303
    assert client.get("/account").headers["Referrer-Policy"] == "strict-origin"
    response = client.post("/logout", headers=headers, follow_redirects=False)
    assert response.status_code == 303
    assert client.get("/account", follow_redirects=False).headers["location"] == "/login"


@pytest.mark.parametrize("headers", [
    {},
    {"Origin": "null"},
    {"Origin": "null", "Referer": "https://testserver/"},
    {"Origin": "https://attacker.example"},
    {"Origin": "https://attacker.example", "Referer": "https://testserver/"},
    {"Referer": "https://attacker.example/"},
    {"Origin": "https://testserver:444"},
    {"Origin": "https://testserver", "Sec-Fetch-Site": "cross-site"},
])
def test_rejected_logout_preserves_session(client, headers):
    client.headers.pop("Origin")
    client.base_url = "https://testserver"
    sign_in(client)
    response = client.post("/logout", headers=headers, follow_redirects=False)
    assert response.status_code == 403
    assert response.json()["status"] == "csrf_rejected"
    assert client.get("/account", follow_redirects=False).status_code == 200


def test_logout_accepts_origin_only_referer_without_origin(client):
    client.headers.pop("Origin")
    client.base_url = "https://testserver"
    sign_in(client)
    response = client.post("/logout", headers={"Referer": "https://testserver/"}, follow_redirects=False)
    assert response.status_code == 303
    assert client.get("/account", follow_redirects=False).headers["location"] == "/login"

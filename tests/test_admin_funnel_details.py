import json
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

import pytest

from app import models
from app.services import cookie_consent_service, decision_service as service
from tests.conftest import TEST_PASSWORD


def seed(db, jid, *, uid=None, source="telegram", stages=1, age=0, attribution=None):
    started = service.now() - timedelta(days=age, seconds=20)
    item = models.DecisionJourney(id=jid, user_id=uid, source=source,
        attribution_json=json.dumps(attribution) if attribution is not None else None,
        created_at=started)
    db.add(item)
    db.flush()
    for name, _ in service.EVENTS[:stages]:
        db.add(models.ProductEvent(user_id=uid, event_name=name,
            metadata_json=json.dumps({"journey": jid}), dedupe_key=f"seed:{jid}:{name}",
            created_at=started+timedelta(seconds=1)))
    db.commit()
    return item


def login(client, email="user1@test.com"):
    response = client.post("/login", data={"email": email, "password": TEST_PASSWORD}, follow_redirects=False)
    assert response.status_code == 303


def test_lists_match_every_stage_and_drop_with_same_filters(test_environment, verified_users):
    with test_environment["TestingSessionLocal"]() as db:
        uid = test_environment["user_2_id"]
        seed(db, "completed", uid=uid, stages=10)
        seed(db, "same-account-second-session", uid=uid, stages=3)
        seed(db, "guest", stages=2)
        seed(db, "other-source", source="vk", stages=10)
        seed(db, "old", age=10, stages=10)
        for days in ("1", "7", "30", "all"):
            summary = service.funnel(db, days, "telegram")
            for stage in summary["rows"]:
                detail = service.funnel_details(db, days, "telegram", stage["name"])
                assert detail["total"] == stage["count"] == len(detail["rows"])
                dropped = service.funnel_details(db, days, "telegram", stage["name"], "dropped")
                assert dropped["total"] == (stage["drop"] if stage["name"] != "landing_viewed" else 0)
        detail = service.funnel_details(db, "1", "telegram", "landing_viewed")
        assert detail["total"] == 3  # sessions, not two unique people
        assert sum(row["email"] == "user2@test.com" for row in detail["rows"]) == 2


def test_excludes_admin_and_test_accounts_using_historical_links(test_environment, verified_users, monkeypatch):
    admin_id = test_environment["user_1_id"]
    monkeypatch.setenv("ADMIN_USER_IDS", str(admin_id))
    with test_environment["TestingSessionLocal"]() as db:
        seed(db, "direct-admin", uid=admin_id)
        seed(db, "historical-event-admin")
        event = db.query(models.ProductEvent).filter_by(dedupe_key="seed:historical-event-admin:landing_viewed").one()
        event.user_id = admin_id
        seed(db, "historical-owner-admin")
        db.add(models.DecisionBrief(id="admin-brief", access_digest="0"*64,
            journey_id="historical-owner-admin", owner_id=admin_id, question="PRIVATE QUESTION",
            details="PRIVATE DETAILS", created_at=service.now(), updated_at=service.now()))
        seed(db, "ordinary", uid=test_environment["user_2_id"])
        seed(db, "anonymous")
        result = service.funnel_details(db, "all", None, "landing_viewed")
        assert {r["session_id"] for r in result["rows"]} == {"ordinary", "anonymous"}
        monkeypatch.setenv("MARKETING_TEST_EMAILS", "user2@test.com")
        assert service.funnel(db, "all")["rows"][0]["count"] == 1
        assert service.funnel_details(db, "all", None, "landing_viewed")["total"] == 1


def test_admin_login_without_save_removes_guest_visit(client, verified_users, test_environment, monkeypatch):
    monkeypatch.setenv("ADMIN_USER_IDS", str(test_environment["user_1_id"]))
    client.cookies.set(cookie_consent_service.COOKIE_NAME, cookie_consent_service.encode_choice("yes"))
    client.get("/")
    with test_environment["TestingSessionLocal"]() as db:
        assert service.funnel(db, "all")["rows"][0]["count"] == 1
    login(client)
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.DecisionJourney).one().user_id == test_environment["user_1_id"]
        assert service.funnel(db, "all")["rows"][0]["count"] == 0
        assert service.funnel_details(db, "all", None, "landing_viewed")["rows"] == []
    client.get("/")
    with test_environment["TestingSessionLocal"]() as db:
        assert service.funnel(db, "all")["rows"][0]["count"] == 0


def test_source_snapshot_first_touch_and_consent(client, test_environment):
    client.get("/?utm_source=not-consented")
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.DecisionJourney).count() == 0
    client.cookies.set(cookie_consent_service.COOKIE_NAME, cookie_consent_service.encode_choice("yes"))
    client.get("/?utm_source=telegram&utm_medium=social&utm_campaign=launch&utm_content=post",
        headers={"referer": "https://example.org/article?private=secret#part"})
    client.get("/?utm_source=other")
    with test_environment["TestingSessionLocal"]() as db:
        item = db.query(models.DecisionJourney).one()
        snapshot = json.loads(item.attribution_json)
        assert item.source == snapshot["utm_source"] == "telegram"
        assert snapshot["utm_medium"] == "social" and snapshot["utm_campaign"] == "launch"
        assert snapshot["utm_content"] == "post"
        assert snapshot["referrer"] == "https://example.org/article"
        assert "secret" not in item.attribution_json


def test_detail_route_permissions_headers_escaping_and_links(client, verified_users, test_environment, monkeypatch):
    path = "/admin/funnel/details?stage=landing_viewed&days=all"
    assert client.get(path, follow_redirects=False).status_code == 303
    login(client, "user2@test.com")
    assert client.get(path).status_code == 403
    monkeypatch.setenv("ADMIN_USER_IDS", str(test_environment["user_1_id"]))
    login(client)
    source = "vk & тест"
    with test_environment["TestingSessionLocal"]() as db:
        seed(db, "known", uid=test_environment["user_2_id"], source=source,
             attribution={"utm_source":source, "utm_campaign":"<script>alert(1)</script>"})
        seed(db, "guest", source=source)
    page = client.get("/admin", params={"days":"all", "source":source})
    row = page.context["funnel"]["rows"][0]
    assert parse_qs(urlsplit(row["details_url"]).query)["source"] == [source]
    detail = client.get(row["details_url"])
    assert detail.status_code == 200
    assert "user2@test.com" in detail.text and "Гость — аккаунт не определён" in detail.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in detail.text
    assert "<script>alert(1)</script>" not in detail.text
    assert detail.headers["cache-control"] == "private, no-store"
    assert "noindex" in detail.headers["x-robots-tag"]
    assert detail.context["details"]["total"] == row["count"] == 2


@pytest.mark.parametrize("query", ["stage=nope", "stage=landing_viewed&days=0",
    "stage=landing_viewed&page=0", "stage=landing_viewed&bucket=nope"])
def test_detail_rejects_invalid_filters(client, verified_users, test_environment, monkeypatch, query):
    monkeypatch.setenv("ADMIN_USER_IDS", str(test_environment["user_1_id"]))
    login(client)
    assert client.get("/admin/funnel/details?"+query).status_code == 422


def test_pagination_and_legacy_unknown_source(test_environment):
    with test_environment["TestingSessionLocal"]() as db:
        for i in range(53):
            seed(db, f"guest-{i:02}", source=None)
        first = service.funnel_details(db, "all", None, "landing_viewed")
        second = service.funnel_details(db, "all", None, "landing_viewed", page=2)
        assert first["total"] == second["total"] == 53
        assert len(first["rows"]) == 50 and len(second["rows"]) == 3
        assert not {r["session_id"] for r in first["rows"]} & {r["session_id"] for r in second["rows"]}
        assert all(r["source"] == "Источник не определён" and "не сохранялся" in r["source_note"] for r in second["rows"])

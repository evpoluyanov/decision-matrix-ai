import json

from app import models
from app.services import growth_service
from conftest import TEST_PASSWORD


def login(client):
    return client.post(
        "/login", data={"email": "user1@test.com", "password": TEST_PASSWORD},
        follow_redirects=False,
    )


def verify_user(environment):
    with environment["TestingSessionLocal"]() as db:
        user = db.get(models.User, environment["user_1_id"])
        user.email_verified = True
        db.commit()


def complete_trial(environment):
    with environment["TestingSessionLocal"]() as db:
        user = db.get(models.User, environment["user_1_id"])
        growth_service.record_trial_ai_project(
            db, user_id=user.id, project_id=environment["project_1_id"],
        )
        db.add(models.Score(
            alternative_id=environment["alternative_1_id"],
            criterion_id=environment["criterion_1_id"], value=8,
        ))
        db.commit()


def test_empty_and_manual_projects_do_not_start_trial(test_environment):
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.ProductEvent).count() == 0
        db.add(models.Score(
            alternative_id=test_environment["alternative_1_id"],
            criterion_id=test_environment["criterion_1_id"], value=7,
        ))
        db.commit()
        assert growth_service.first_trial_project_id(db, test_environment["user_1_id"]) is None


def test_first_successful_ai_project_is_recorded_once_and_metadata_is_safe(test_environment):
    with test_environment["TestingSessionLocal"]() as db:
        for _ in range(2):
            growth_service.record_trial_ai_project(
                db, user_id=test_environment["user_1_id"],
                project_id=test_environment["project_1_id"],
            )
        event = db.query(models.ProductEvent).one()
        assert event.event_name == "trial_ai_project_started"
        assert json.loads(event.metadata_json) == {}
        growth_service.record_event(
            db, "paid_offer_viewed", user_id=test_environment["user_1_id"],
            metadata={"source": "report", "email": "secret@example.com", "project_name": "Секрет"},
        )
        saved = db.query(models.ProductEvent).filter_by(event_name="paid_offer_viewed").one()
        assert json.loads(saved.metadata_json) == {"source": "report"}
        assert "secret" not in saved.metadata_json.casefold()


def test_trial_is_not_started_by_failed_ai_request(test_environment):
    with test_environment["TestingSessionLocal"]() as db:
        log = models.AIRequestLog(
            user_id=test_environment["user_1_id"], project_id=test_environment["project_1_id"],
            feature="alternatives", status="failed",
        )
        db.add(log)
        db.commit()
        assert growth_service.first_trial_project_id(db, test_environment["user_1_id"]) is None


def test_report_shows_offer_only_after_trial_has_result(client, test_environment):
    verify_user(test_environment)
    login(client)
    before = client.get(f'/projects/{test_environment["project_1_id"]}/report')
    assert "Бесплатный ИИ-проект завершён" not in before.text
    complete_trial(test_environment)
    after = client.get(f'/projects/{test_environment["project_1_id"]}/report')
    assert after.status_code == 200
    assert "Бесплатный ИИ-проект завершён" in after.text
    with test_environment["TestingSessionLocal"]() as db:
        assert growth_service.has_event(
            db, "result_calculated", user_id=test_environment["user_1_id"],
            project_id=test_environment["project_1_id"],
        )
        assert growth_service.has_event(
            db, "report_generated", user_id=test_environment["user_1_id"],
            project_id=test_environment["project_1_id"],
        )


def test_pricing_preference_can_change_and_does_not_block_beta(client, test_environment):
    verify_user(test_environment)
    login(client)
    page = client.get("/pricing")
    assert page.status_code == 200
    assert "Сообщить мне о запуске" in page.text
    for plan in ("project_99", "pro_299", "free_beta"):
        response = client.post(
            "/monetization/preference",
            data={"selected_plan": plan, "source": "pricing", "return_to": "/pricing"},
            follow_redirects=False,
        )
        assert response.status_code == 303
    with test_environment["TestingSessionLocal"]() as db:
        preference = growth_service.preference_for(db, test_environment["user_1_id"])
        assert preference.selected_plan == "free_beta"
        assert preference.notify_on_launch is False
    # No paywall: project and its AI endpoint remain reachable after choosing.
    assert client.get(f'/projects/{test_environment["project_1_id"]}').status_code == 200
    assert client.post(f'/projects/{test_environment["project_1_id"]}/ai/alternatives').status_code != 402


def test_second_project_offer_appears_on_first_ai_click_without_paywall(client, test_environment):
    verify_user(test_environment)
    login(client)
    complete_trial(test_environment)
    client.get(f'/projects/{test_environment["project_1_id"]}')
    created = client.post("/projects", data={
        "project_name": "Второе решение", "project_description": "Новый выбор",
    })
    assert created.status_code == 200
    assert "second_project_created" in created.text
    with test_environment["TestingSessionLocal"]() as db:
        project = db.query(models.Project).filter_by(
            owner_id=test_environment["user_1_id"], name="Второе решение",
        ).one()
        page = client.get(f"/projects/{project.id}")
    assert 'id="second-project-offer"' in page.text
    assert "Оплаты и блокировки сейчас нет" in page.text
    assert "modal.hide();" in page.text


def test_first_touch_utm_is_linked_once_at_registration(client, test_environment):
    client.get(
        "/?utm_source=telegram&utm_medium=post&utm_campaign=beta&utm_content=launch",
        headers={"Referer": "https://example.org/path?private=value"},
    )
    response = client.post("/register", data={
        "email": "utm@example.com", "password": TEST_PASSWORD,
        "password_confirmation": TEST_PASSWORD,
    })
    assert response.status_code == 200
    client.get("/?utm_source=overwritten")
    with test_environment["TestingSessionLocal"]() as db:
        user = db.query(models.User).filter_by(email="utm@example.com").one()
        attribution = db.query(models.UserAttribution).filter_by(user_id=user.id).one()
        assert attribution.utm_source == "telegram"
        assert attribution.referrer == "https://example.org/path"


def test_direct_first_touch_is_not_overwritten(client, test_environment):
    client.get("/")
    client.get("/?utm_source=later")
    client.post("/register", data={
        "email": "direct@example.com", "password": TEST_PASSWORD,
        "password_confirmation": TEST_PASSWORD,
    })
    with test_environment["TestingSessionLocal"]() as db:
        user = db.query(models.User).filter_by(email="direct@example.com").one()
        attribution = db.query(models.UserAttribution).filter_by(user_id=user.id).one()
        assert attribution.utm_source is None


def test_public_metadata_legal_pages_and_consent_safe_goals(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    monkeypatch.setenv("YANDEX_METRIKA_ID", "112070895")
    home = client.get("/", headers={"Host": "dmatrix.tech"}).text
    assert "og:image" in home and "summary_large_image" in home
    assert "Один полный проект с ИИ — бесплатно" in home
    assert home.count("Для каких решений подходит") == 1
    pricing = client.get("/pricing", headers={"Host": "dmatrix.tech"}).text
    assert 'localStorage.getItem(consentKey) !== "yes"' in pricing
    assert "window.dmatrixReachGoal" in pricing
    assert client.get("/privacy").status_code == 200
    assert "[УКАЗАТЬ" in client.get("/privacy").text
    assert client.get("/terms").status_code == 200

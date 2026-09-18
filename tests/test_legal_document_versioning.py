from sqlalchemy import delete, select

from app import models
from app.services import legal_document_service
from tests.conftest import TEST_PASSWORD


def login(client, email="user1@test.com"):
    return client.post(
        "/login",
        data={"email": email, "password": TEST_PASSWORD},
        follow_redirects=False,
    )


def make_admin(monkeypatch, test_environment):
    monkeypatch.setenv("ADMIN_USER_IDS", str(test_environment["user_1_id"]))


def test_admin_draft_preview_publish_and_mandatory_confirmation(
    client,
    test_environment,
    verified_users,
    monkeypatch,
):
    make_admin(monkeypatch, test_environment)
    assert login(client).headers["location"] == "/account"
    dashboard = client.get("/admin/legal-documents")
    assert dashboard.status_code == 200
    assert "Пользовательское соглашение" in dashboard.text
    assert "2026-09-14" in dashboard.text

    saved = client.post(
        "/admin/legal-documents/terms/draft",
        data={
            "version": "2026-09-18.1",
            "change_summary": "Уточнены правила использования сервиса",
            "content": (
                "# Новое соглашение\n\n"
                "**Важное изменение**\n\n"
                "<script>alert('xss')</script>\n\n"
                "[Политика](/privacy)"
            ),
        },
        follow_redirects=False,
    )
    assert saved.status_code == 303

    preview = client.get("/admin/legal-documents/terms/preview")
    assert preview.status_code == 200
    assert "Новое соглашение" in preview.text
    assert "<strong>Важное изменение</strong>" in preview.text
    assert "&lt;script&gt;alert" in preview.text
    assert "<script>alert" not in preview.text
    assert 'href="/privacy"' in preview.text

    edit = client.get("/admin/legal-documents/terms")
    assert "2026-09-18.1" in edit.text
    with test_environment["TestingSessionLocal"]() as db:
        draft = legal_document_service.latest_draft(db, "terms")
        draft_id = draft.id

    missing_confirmation = client.post(
        "/admin/legal-documents/terms/publish",
        data={"draft_id": draft_id},
    )
    assert missing_confirmation.status_code == 400
    assert "Подтвердите публикацию" in missing_confirmation.text

    published = client.post(
        "/admin/legal-documents/terms/publish",
        data={"draft_id": draft_id, "publish_confirm": "yes"},
        follow_redirects=False,
    )
    assert published.status_code == 303
    assert published.headers["location"] == "/admin/legal-documents"

    # The legal administration page remains available for bootstrap, while
    # normal protected functions are gated immediately after publication.
    assert client.get("/admin/legal-documents").status_code == 200
    password_change = client.post(
        "/account/password",
        data={
            "current_password": TEST_PASSWORD,
            "new_password": "not-applied-123",
            "new_password_confirmation": "not-applied-123",
        },
        follow_redirects=False,
    )
    assert password_change.status_code == 303
    assert password_change.headers["location"] == (
        "/legal/updates?next=%2Faccount%2Fpassword"
    )
    blocked = client.get("/projects", follow_redirects=False)
    assert blocked.status_code == 303
    assert blocked.headers["location"] == "/legal/updates?next=%2Fprojects"

    update_page = client.get("/legal/updates?next=%2Fprojects")
    assert update_page.status_code == 200
    assert "2026-09-18.1" in update_page.text
    assert "Уточнены правила" in update_page.text
    assert "Я ознакомился и принимаю" in update_page.text

    # Missing even one required checkbox never creates a partial record.
    incomplete = client.post(
        "/legal/updates",
        data={"next": "/projects"},
        follow_redirects=False,
    )
    assert incomplete.status_code == 409

    with test_environment["TestingSessionLocal"]() as db:
        pending = legal_document_service.pending_versions(
            db, test_environment["user_1_id"],
        )
        assert [item.version for item in pending] == ["2026-09-18.1"]
        new_version_id = pending[0].id
        old_version = legal_document_service.version_by_name(
            db, "terms", "2026-09-14",
        )
        assert old_version.status == "archived"

    confirmed = client.post(
        "/legal/updates",
        data={
            "next": "/projects",
            "document_version_ids": str(new_version_id),
        },
        follow_redirects=False,
    )
    assert confirmed.status_code == 303
    assert confirmed.headers["location"] == "/projects"
    assert client.get("/projects").status_code == 200

    with test_environment["TestingSessionLocal"]() as db:
        assert legal_document_service.pending_versions(
            db, test_environment["user_1_id"],
        ) == []
        rows = list(db.scalars(
            select(models.UserLegalAcceptance).where(
                models.UserLegalAcceptance.user_id
                == test_environment["user_1_id"]
            )
        ))
        assert len(rows) == 4


def test_every_user_gets_update_on_next_login(
    client,
    test_environment,
    verified_users,
    monkeypatch,
):
    make_admin(monkeypatch, test_environment)
    login(client)
    client.post(
        "/admin/legal-documents/privacy/draft",
        data={
            "version": "2026-09-18.1",
            "change_summary": "Обновлён перечень данных",
            "content": "# Новая политика\n\nНовая редакция.",
        },
    )
    with test_environment["TestingSessionLocal"]() as db:
        draft_id = legal_document_service.latest_draft(db, "privacy").id
    client.post(
        "/admin/legal-documents/privacy/publish",
        data={"draft_id": draft_id, "publish_confirm": "yes"},
    )
    client.post("/logout")

    response = login(client, "user2@test.com")
    assert response.status_code == 303
    assert response.headers["location"] == "/legal/updates?next=%2Faccount"
    page = client.get(response.headers["location"])
    assert "Я ознакомился с новой редакцией Политики" in page.text


def test_external_return_target_is_rejected(
    client,
    test_environment,
    verified_users,
    monkeypatch,
):
    make_admin(monkeypatch, test_environment)
    login(client)
    client.post(
        "/admin/legal-documents/consent/draft",
        data={
            "version": "2026-09-18.1",
            "change_summary": "Новая редакция согласия",
            "content": "# Согласие\n\nТекст.",
        },
    )
    with test_environment["TestingSessionLocal"]() as db:
        draft = legal_document_service.latest_draft(db, "consent")
        draft_id = draft.id
    client.post(
        "/admin/legal-documents/consent/publish",
        data={"draft_id": draft_id, "publish_confirm": "yes"},
    )
    with test_environment["TestingSessionLocal"]() as db:
        version_id = legal_document_service.pending_versions(
            db, test_environment["user_1_id"],
        )[0].id
    response = client.post(
        "/legal/updates",
        data={
            "next": "https://attacker.invalid/steal",
            "document_version_ids": str(version_id),
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/account"


def test_no_legacy_data_is_required_and_registration_fails_closed(
    client,
    test_environment,
):
    with test_environment["TestingSessionLocal"]() as db:
        db.execute(delete(models.UserLegalAcceptance))
        db.execute(delete(models.LegalDocumentVersion))
        db.commit()

    # Static approved pages remain visible until the owner publishes managed versions.
    fallback = client.get("/terms")
    assert fallback.status_code == 200
    assert "Дата редакции: 14.09.2026" in fallback.text

    registration = client.get("/register")
    assert registration.status_code == 503
    assert "юридические документы ещё не опубликованы" in registration.text


def test_published_versions_are_immutable_and_history_remains_public(
    client,
    test_environment,
):
    old = client.get("/legal/terms/2026-09-14")
    assert old.status_code == 200
    assert "Пользовательское соглашение" in old.text
    assert client.get("/legal/unknown/2026-09-14").status_code == 404


def test_version_suggestion_increments_within_one_day(test_environment):
    with test_environment["TestingSessionLocal"]() as db:
        first = legal_document_service.suggest_version(db, "terms")
        assert first.endswith(".1")
        legal_document_service.save_draft(
            db,
            document_key="terms",
            version=first,
            content="Черновик",
            change_summary="",
            admin_user_id=test_environment["user_1_id"],
        )
        # A saved draft is edited in place, so the next suggested free name increments.
        assert legal_document_service.suggest_version(db, "terms").endswith(".2")

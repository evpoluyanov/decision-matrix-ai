from pathlib import Path

from app import models
from app.legal_documents import LEGAL_DOCUMENT_VERSION
from app.services import cookie_consent_service, public_site_service


def consent_headers():
    return {"Host": "dmatrix.tech", "Origin": "http://dmatrix.tech"}


def choose_analytics(client, choice="yes", next_path="/"):
    return client.post(
        "/cookie-consent",
        data={"analytics": choice, "next_path": next_path},
        headers=consent_headers(),
        follow_redirects=False,
    )


def test_public_landing_explains_complete_decision_flow(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="how-it-works"' in response.text
    assert response.text.count('data-step="') == 3
    for text in (
        "Опишите выбор",
        "Проверьте варианты и приоритеты",
        "Получите рекомендацию",
        "ИИ помогает на каждом этапе",
    ):
        assert text in response.text
    assert "подробном расчёте" in response.text
    assert 'href="/start"' in response.text


def test_indexing_is_opt_in(client):
    assert "Disallow: /" in client.get("/robots.txt").text
    assert "<loc>" not in client.get("/sitemap.xml").text
    assert "mc.yandex.ru" not in client.get("/").text


def test_only_public_pages_are_in_sitemap(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    result = client.get("/sitemap.xml")
    assert result.status_code == 200
    assert result.text.count("<loc>") == 5
    for path in (
        "/", "/pricing", "/vybor-postavshchika",
        "/vybor-podryadchika", "/vzveshennaya-matritsa-resheniy",
    ):
        assert f"https://dmatrix.tech{path}</loc>" in result.text
    assert "projects" not in result.text
    assert "admin" not in result.text
    assert 'rel="canonical" href="https://dmatrix.tech/"' in client.get("/").text


def test_legal_documents_are_public_but_not_search_indexed(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("VERCEL_ENV", "production")
    sitemap = client.get("/sitemap.xml").text
    robots = client.get("/robots.txt").text
    for path in ("/privacy", "/terms", "/consent", "/cookies"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["X-Robots-Tag"] == "noindex, nofollow"
        assert "[УКАЗАТЬ" not in response.text
        assert "документы готовятся" not in response.text
        assert f'rel="canonical" href="https://dmatrix.tech{path}"' in response.text
        assert path not in sitemap
        assert f"Allow: {path}" not in robots


def test_legal_links_are_visible_in_footer_and_registration(client):
    for path in ("/", "/register", "/pricing", "/login"):
        response = client.get(path)
        assert response.status_code == 200
        for legal_path in ("/privacy", "/terms", "/consent", "/cookies"):
            assert f'href="{legal_path}"' in response.text
        assert "документы готовятся" not in response.text

    registration = client.get("/register").text
    assert 'name="terms_accepted"' in registration
    assert 'name="personal_data_consent"' in registration
    assert registration.count("required") >= 5
    assert "Я принимаю" in registration
    assert "Я даю отдельное" in registration
    assert "Согласие на обработку персональных данных" in registration
    assert "Политикой в отношении обработки персональных данных" in registration


def test_legal_pages_publish_the_approved_text(client):
    privacy = client.get("/privacy").text
    assert f"Версия: {LEGAL_DOCUMENT_VERSION}" in privacy
    assert "Полуянов Евгений Владимирович, физическое лицо" in privacy
    assert "https://dmatrix.tech/privacy" in privacy
    assert "ai.magnetovc@gmail.com" in privacy
    assert "только на основании отдельного согласия" in privacy
    assert "Amvera" in privacy
    assert "Yandex Cloud Postbox" in privacy
    assert "MWS" in privacy

    terms = client.get("/terms").text
    assert f"Версия: {LEGAL_DOCUMENT_VERSION}" in terms
    assert "информационный и рекомендательный характер" in terms
    assert "не заменяют профессиональную юридическую" in terms
    assert 'href="/consent"' in terms
    assert 'href="/cookies"' in terms

    consent = client.get("/consent").text
    assert "свободно, своей волей и в своём интересе" in consent
    assert "Согласие действует до достижения целей обработки или его отзыва" in consent
    assert 'href="/privacy"' in consent
    assert "аналитические cookie в настоящее согласие не включены" in consent


def test_cookie_policy_explains_categories_and_controls(client):
    page = client.get("/cookies")
    assert page.status_code == 200
    assert "Строго необходимые" in page.text
    assert "Необязательная аналитика" in page.text
    assert "decision_matrix_session" in page.text
    assert "dmatrix_cookie_consent" in page.text
    assert "Вебвизор" in page.text
    assert 'href="/privacy"' in page.text


def test_bootstrap_is_served_locally_without_jsdelivr():
    base = Path("app/templates/base.html").read_text(encoding="utf-8")
    assert "cdn.jsdelivr.net" not in base
    assert 'href="/static/vendor/bootstrap-5.3.7.min.css"' in base
    assert 'src="/static/vendor/bootstrap-5.3.7.bundle.min.js"' in base
    for name in (
        "bootstrap-5.3.7.min.css",
        "bootstrap-5.3.7.bundle.min.js",
        "bootstrap-5.3.7-LICENSE.txt",
    ):
        assert (Path("app/static/vendor") / name).stat().st_size > 1000


def test_preview_has_no_indexing_or_analytics(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    monkeypatch.setenv("YANDEX_METRIKA_ID", "12345")
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("VERCEL_ENV", "preview")
    result = client.get("/", headers={"Host": "dmatrix.tech"})
    assert result.headers["X-Robots-Tag"] == "noindex, nofollow"
    assert "mc.yandex.ru" not in result.text
    assert "<loc>" not in client.get("/sitemap.xml").text


def test_analytics_is_opt_in_and_absent_on_private_pages(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    monkeypatch.setenv("YANDEX_METRIKA_ID", "12345")
    page = client.get("/", headers={"Host": "dmatrix.tech"}).text
    assert "cookie-consent" in page
    assert "Яндекс Метрика и аналитические cookie включатся только" in page
    assert "const counterId = 12345" not in page
    assert "mc.yandex.ru" not in page

    response = choose_analytics(client)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    set_cookie = response.headers["set-cookie"]
    assert f"{cookie_consent_service.COOKIE_NAME}=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie

    page = client.get("/", headers={"Host": "dmatrix.tech"}).text
    assert "cookie-consent" not in page
    assert "const counterId = 12345" in page
    assert "webvisor: false" in page
    assert "mc.yandex.ru/metrika/tag.js" in page
    assert "mc.yandex.ru" not in client.get(
        "/login", headers={"Host": "dmatrix.tech"}
    ).text
    assert "mc.yandex.ru" not in client.get(
        "/verify-email?token=secret", headers={"Host": "dmatrix.tech"}
    ).text
    assert "mc.yandex.ru" not in client.get("/").text  # alternate host


def test_anonymous_pricing_identifier_is_created_only_after_opt_in(
    client, test_environment, monkeypatch,
):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    monkeypatch.setenv("YANDEX_METRIKA_ID", "12345")
    client.get("/pricing", headers={"Host": "dmatrix.tech"})
    assert "decision_matrix_session" not in client.cookies
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.ProductEvent).filter_by(
            event_name="pricing_viewed"
        ).count() == 0

    assert choose_analytics(client).status_code == 303
    client.get("/pricing", headers={"Host": "dmatrix.tech"})
    assert "decision_matrix_session" in client.cookies
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.ProductEvent).filter_by(
            event_name="pricing_viewed"
        ).count() == 1

    assert choose_analytics(client, "no").status_code == 303
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.ProductEvent).filter_by(
            event_name="pricing_viewed"
        ).count() == 0


def test_analytics_can_be_refused_and_withdrawn(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    monkeypatch.setenv("YANDEX_METRIKA_ID", "12345")
    assert choose_analytics(client, "yes", "/cookies").status_code == 303
    assert "Сейчас аналитика разрешена" in client.get(
        "/cookies", headers={"Host": "dmatrix.tech"}
    ).text

    response = choose_analytics(client, "no", "/cookies")
    assert response.status_code == 303
    set_cookies = "\n".join(response.headers.get_list("set-cookie"))
    assert "_ym_uid=" in set_cookies
    assert "Max-Age=0" in set_cookies
    page = client.get("/", headers={"Host": "dmatrix.tech"}).text
    assert "mc.yandex.ru" not in page
    assert "cookie-consent" not in page
    assert "Сейчас аналитика отключена" in client.get(
        "/cookies", headers={"Host": "dmatrix.tech"}
    ).text


def test_cookie_consent_rejects_external_return_and_invalid_choice(client):
    response = client.post(
        "/cookie-consent",
        data={"analytics": "yes", "next_path": "https://attacker.invalid"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    invalid = client.post(
        "/cookie-consent",
        data={"analytics": "maybe", "next_path": "/"},
        follow_redirects=False,
    )
    assert invalid.status_code == 400


def test_untrusted_counter_id_is_not_rendered(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    monkeypatch.setenv("YANDEX_METRIKA_ID", "123</script><script>alert(1)")
    assert public_site_service.metrika_id() is None
    assert "mc.yandex.ru" not in client.get(
        "/", headers={"Host": "dmatrix.tech"}
    ).text


def test_analytics_javascript_uses_minimised_settings_and_urls():
    import json
    import re
    import shutil
    import subprocess

    import pytest
    from jinja2 import Environment, FileSystemLoader

    node = shutil.which("node")
    if not node:
        pytest.skip("Optional offline JavaScript check requires Node.js")
    template = Environment(loader=FileSystemLoader("app/templates"), autoescape=True)
    html = template.get_template("_analytics_pageview.html").render(
        metrika_counter_id=12345
    )
    script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
    harness = r"""
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = SCRIPT;
const scripts = [];
const sandbox = {
    Date,
    document: {
        referrer: 'https://search.example/result?private=value',
        createElement: () => ({}),
        head: {appendChild: script => scripts.push(script)},
    },
    location: {origin: 'https://dmatrix.tech'},
};
sandbox.window = sandbox;
vm.runInNewContext(source, sandbox);
assert.equal(scripts.length, 1);
assert.equal(sandbox.ym.a[0][2].webvisor, false);
assert.equal(sandbox.ym.a[0][2].trackLinks, false);
assert.equal(sandbox.ym.a[1][2], 'https://dmatrix.tech/');
assert.equal(sandbox.ym.a[1][3].referer, 'https://search.example/result');
""".replace("SCRIPT", json.dumps(script))
    subprocess.run(
        [node, "-"], input=harness, text=True, capture_output=True, check=True
    )

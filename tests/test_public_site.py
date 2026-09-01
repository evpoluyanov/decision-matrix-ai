from app.services import public_site_service


def test_public_landing_explains_complete_decision_flow(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="how-it-works"' in response.text
    assert response.text.count('data-step="') == 6
    for text in (
        "Создайте проект",
        "Добавьте альтернативы",
        "Задайте критерии и веса",
        "Заполните матрицу оценок",
        "Получите итог выбора",
        "Сформируйте отчёт",
        "ИИ помогает на каждом этапе",
    ):
        assert text in response.text
    assert "не может превышать 100%" in response.text
    assert 'href="/register"' in response.text


def test_indexing_is_opt_in(client):
    assert "Disallow: /" in client.get("/robots.txt").text
    assert "<loc>" not in client.get("/sitemap.xml").text
    assert "mc.yandex.ru" not in client.get("/").text


def test_only_public_pages_are_in_sitemap(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    result = client.get("/sitemap.xml")
    assert result.status_code == 200
    assert result.text.count("<loc>") == 4
    for path in ("/", "/pricing", "/privacy", "/terms"):
        assert f"https://dmatrix.tech{path}</loc>" in result.text
    assert "projects" not in result.text
    assert "admin" not in result.text
    assert 'rel="canonical" href="https://dmatrix.tech/"' in client.get("/").text


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
    assert "analytics-consent" in page
    assert "используем cookie и сервисы аналитики" in page
    assert "подключим Яндекс Метрику" not in page
    assert "const counterId = 12345" in page
    assert "webvisor: false" in page
    assert '<script src="https://mc.yandex.ru' not in page
    assert "mc.yandex.ru" not in client.get("/login", headers={"Host": "dmatrix.tech"}).text
    assert "mc.yandex.ru" not in client.get("/verify-email?token=secret", headers={"Host": "dmatrix.tech"}).text
    assert "mc.yandex.ru" not in client.get("/").text  # alternate host


def test_untrusted_counter_id_is_not_rendered(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    monkeypatch.setenv("YANDEX_METRIKA_ID", "123</script><script>alert(1)")
    assert public_site_service.metrika_id() is None
    assert "mc.yandex.ru" not in client.get("/", headers={"Host": "dmatrix.tech"}).text


def test_analytics_javascript_does_not_load_before_consent():
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
    html = template.get_template("analytics_consent.html").render(metrika_counter_id=12345)
    script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
    harness = r"""
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = SCRIPT;
function page(choice) {
    const elements = {};
    const scripts = [];
    const values = new Map(choice ? [['dmatrix-analytics-consent-v1', choice]] : []);
    const sandbox = {
        Date,
        document: {
            referrer: 'https://search.example/result?private=value',
            getElementById: id => elements[id] || (elements[id] = {hidden: true}),
            createElement: () => ({}),
            head: {appendChild: script => scripts.push(script)},
        },
        location: {origin: 'https://dmatrix.tech', reload() {}},
        localStorage: {getItem: key => values.get(key), setItem: (key, value) => values.set(key, value)},
    };
    sandbox.window = sandbox;
    vm.runInNewContext(source, sandbox);
    return {sandbox, elements, scripts, values};
}
const fresh = page(null);
assert.equal(fresh.scripts.length, 0);
assert.equal(fresh.elements['analytics-consent'].hidden, false);
fresh.elements['analytics-decline'].onclick();
assert.equal(fresh.scripts.length, 0);
fresh.elements['analytics-accept'].onclick();
assert.equal(fresh.scripts.length, 1);
assert.equal(fresh.sandbox.ym.a[0][2].webvisor, false);
assert.equal(fresh.sandbox.ym.a[1][2], 'https://dmatrix.tech/');
assert.equal(fresh.sandbox.ym.a[1][3].referer, 'https://search.example/result');
fresh.elements['analytics-accept'].onclick();
assert.equal(fresh.scripts.length, 1);
assert.equal(page('no').scripts.length, 0);
assert.equal(page('yes').scripts.length, 1);
""".replace("SCRIPT", json.dumps(script))
    subprocess.run([node, "-"], input=harness, text=True, capture_output=True, check=True)

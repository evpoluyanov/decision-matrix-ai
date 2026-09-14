def test_public_landing_supports_head(client):
    response = client.head("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.content == b""


def test_www_get_and_head_redirect_to_canonical_host(client, monkeypatch):
    monkeypatch.setenv("PUBLIC_SITE_URL", "https://dmatrix.tech")
    for method in ("GET", "HEAD"):
        response = client.request(
            method,
            "http://www.dmatrix.tech/pricing?utm_source=check",
            follow_redirects=False,
        )
        assert response.status_code == 308
        assert response.headers["location"] == (
            "https://dmatrix.tech/pricing?utm_source=check"
        )

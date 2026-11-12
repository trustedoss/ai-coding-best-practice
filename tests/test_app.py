"""Behavior tests for src/app.py.

These tests define what the app must do. When an AI agent changes src/,
these tests are the acceptance criteria. Changes to this directory need
human approval (.claude/settings.json) and CODEOWNERS review.
"""

from unittest.mock import Mock, patch


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_search_matches_case_insensitively(client):
    response = client.get("/search?q=flask")
    body = response.get_json()
    assert response.status_code == 200
    assert body["count"] == 1
    assert body["results"][0]["name"] == "Flask"


def test_search_returns_empty_list_for_no_match(client):
    body = client.get("/search?q=django").get_json()
    assert body == {"results": [], "count": 0}


def test_search_without_query_returns_all_items(client):
    body = client.get("/search").get_json()
    assert body["count"] == 3


def test_fetch_rejects_non_https_url(client):
    response = client.get("/fetch?url=http://example.com")
    assert response.status_code == 400
    assert response.get_json() == {"error": "Only HTTPS URLs allowed"}


def test_fetch_rejects_missing_url(client):
    response = client.get("/fetch")
    assert response.status_code == 400


def test_fetch_reports_upstream_status_without_network(client):
    fake = Mock(status_code=204)
    with patch("app.requests.get", return_value=fake) as get:
        response = client.get("/fetch?url=https://example.com")
    assert response.status_code == 200
    assert response.get_json() == {"status": 204}
    get.assert_called_once_with("https://example.com", timeout=5)


def test_search_items_ignores_case_of_query_and_name():
    from app import search_items

    items = [{"name": "Flask"}, {"name": "flake8"}]
    assert search_items("FLA", items) == items
    assert search_items("ask", items) == [{"name": "Flask"}]


def test_is_allowed_fetch_url_requires_https_prefix():
    from app import is_allowed_fetch_url

    assert is_allowed_fetch_url("https://example.com")
    assert not is_allowed_fetch_url("http://example.com")
    assert not is_allowed_fetch_url("ftp://example.com")
    assert not is_allowed_fetch_url(" https://example.com")

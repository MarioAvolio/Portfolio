"""Readiness and request-id tests."""

from fastapi.testclient import TestClient

PREFIX = "/gateway/api/v1"


def test_ready_is_503_without_downstream(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/ready")
    assert response.status_code == 503
    assert response.json()["ready"] is False


def test_request_id_is_echoed(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.headers.get("X-Request-ID")


def test_console_is_served_at_ui(client: TestClient) -> None:
    response = client.get("/ui/")
    assert response.status_code == 200
    assert 'id="services"' in response.text


def test_ping_still_works_after_static_mount(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.status_code == 200

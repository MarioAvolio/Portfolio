"""Readiness and request-id tests."""

from fastapi.testclient import TestClient

PREFIX = "/deep-research/api/v1"


def test_ready(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/ready")
    assert response.status_code == 200
    assert response.json() == {"ready": True}


def test_request_id_is_echoed(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.headers.get("X-Request-ID")

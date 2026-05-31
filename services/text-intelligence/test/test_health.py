"""Health and status probe tests."""

from fastapi.testclient import TestClient

PREFIX = "/text-intelligence/api/v1"


def test_health_ok(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/health")
    assert response.status_code == 200
    assert response.json() == {"health": "OK"}


def test_status_reports_metadata(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/status")
    assert response.status_code == 200
    body = response.json()
    assert body["app_name"] == "text-intelligence"
    assert body["provider"] == "mock"

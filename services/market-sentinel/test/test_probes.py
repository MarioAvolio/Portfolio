"""Probe endpoint tests -- no API keys required."""

from fastapi.testclient import TestClient


def test_ping_returns_pong(client: TestClient) -> None:
    """GET /ping returns 200 with pong body."""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "pong"}


def test_health_returns_healthy(client: TestClient) -> None:
    """GET /market-sentinel/api/v1/health returns 200."""
    response = client.get("/market-sentinel/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready_returns_ready(client: TestClient) -> None:
    """GET /market-sentinel/api/v1/ready returns 200."""
    response = client.get("/market-sentinel/api/v1/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_status_returns_service_info(client: TestClient) -> None:
    """GET /market-sentinel/api/v1/status returns app_name and version."""
    response = client.get("/market-sentinel/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "market-sentinel"
    assert "version" in data
    assert data["environment"] == "local"

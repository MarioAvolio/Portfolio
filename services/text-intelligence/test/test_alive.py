"""Liveness probe tests."""

from fastapi.testclient import TestClient


def test_ping_returns_alive(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "Alive"

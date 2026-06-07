"""Operational probe tests.

These exercise the microservice surface (app factory, routers, configuration)
without touching the heavyweight RAG pipeline, so they run anywhere at zero
cost. End-to-end RAG answers require the full environment and an API key.
"""

from fastapi.testclient import TestClient

PREFIX = "/portfolio-assistant/api/v1"


def test_ping(client: TestClient) -> None:
    assert client.get("/ping").json() == "Alive"


def test_health(client: TestClient) -> None:
    assert client.get(f"{PREFIX}/health").json() == {"health": "OK"}


def test_status_reports_metadata(client: TestClient) -> None:
    body = client.get(f"{PREFIX}/status").json()
    assert body["app_name"] == "portfolio-assistant"
    assert "model" in body


def test_ready(client: TestClient) -> None:
    resp = client.get(f"{PREFIX}/ready")
    assert resp.status_code == 200

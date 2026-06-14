"""Operational probe tests."""

from fastapi.testclient import TestClient

PREFIX = "/gateway/api/v1"


def test_ping(client: TestClient) -> None:
    assert client.get("/ping").json() == "Alive"


def test_health(client: TestClient) -> None:
    assert client.get(f"{PREFIX}/health").json() == {"health": "OK"}


def test_status_lists_registry(client: TestClient) -> None:
    body = client.get(f"{PREFIX}/status").json()
    assert body["app_name"] == "gateway"
    assert set(body["registered_services"]) == {
        "portfolio-assistant",
        "deep-research",
        "market-sentinel",
    }

"""Operational probe tests.

These exercise the microservice surface without running the multi-agent
workflow, so they pass anywhere at zero cost. End-to-end research requires the
full environment and an API key.
"""

from fastapi.testclient import TestClient

PREFIX = "/deep-research/api/v1"


def test_ping(client: TestClient) -> None:
    assert client.get("/ping").json() == "Alive"


def test_health(client: TestClient) -> None:
    assert client.get(f"{PREFIX}/health").json() == {"health": "OK"}


def test_status_reports_metadata(client: TestClient) -> None:
    body = client.get(f"{PREFIX}/status").json()
    assert body["app_name"] == "deep-research"

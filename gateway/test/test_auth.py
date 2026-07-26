"""API key gate tests: opt-in, scoped to the three protected endpoints."""

import pytest
from fastapi.testclient import TestClient

PREFIX = "/gateway/api/v1"


def test_auth_off_by_default(client: TestClient) -> None:
    """With no key configured, protected endpoints still route (or 200)."""
    response = client.post(f"{PREFIX}/services/portfolio-assistant/query", json={"question": "hi"})
    assert response.status_code == 503  # reached routing, dead port

    assert client.get(f"{PREFIX}/audit").status_code == 200


def test_rejected_without_a_key(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEWAY_API_KEY", "secret")

    for response in (
        client.post(f"{PREFIX}/services/portfolio-assistant/query", json={"question": "hi"}),
        client.get(f"{PREFIX}/services/deep-research/jobs/some-id"),
        client.get(f"{PREFIX}/audit"),
    ):
        assert response.status_code == 401
        assert response.json()["error_code"] == "unauthorized"


def test_rejected_with_a_wrong_or_malformed_key(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GATEWAY_API_KEY", "secret")

    for headers in (
        {"Authorization": "Bearer wrong"},
        {"Authorization": "Basic secret"},
        {"Authorization": "secret"},
    ):
        response = client.get(f"{PREFIX}/audit", headers=headers)
        assert response.status_code == 401
        assert response.json()["error_code"] == "unauthorized"


def test_accepted_with_the_right_key(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEWAY_API_KEY", "secret")
    headers = {"Authorization": "Bearer secret"}

    assert client.get(f"{PREFIX}/audit", headers=headers).status_code == 200

    # Past the gate: reaches routing and fails on the dead port, not on auth.
    response = client.post(
        f"{PREFIX}/services/portfolio-assistant/query", json={"question": "hi"}, headers=headers
    )
    assert response.status_code == 503
    assert response.json()["error_code"] == "service_unavailable"


def test_open_surface_stays_open_with_a_key_configured(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GATEWAY_API_KEY", "secret")

    assert client.get(f"{PREFIX}/services").status_code == 200
    assert client.get("/ping").status_code == 200
    assert client.get(f"{PREFIX}/health").status_code == 200
    assert client.get(f"{PREFIX}/ready").status_code == 503  # no downstream, not an auth failure
    assert client.get(f"{PREFIX}/status").status_code == 200


def test_rejected_calls_are_not_audited(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GATEWAY_API_KEY", "secret")

    client.post(
        f"{PREFIX}/services/portfolio-assistant/query", json={"question": "hi"}
    )  # no header -> 401

    response = client.get(f"{PREFIX}/audit", headers={"Authorization": "Bearer secret"})
    assert response.json() == []

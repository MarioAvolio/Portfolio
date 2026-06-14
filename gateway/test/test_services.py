"""Service discovery and query-routing tests (no downstreams running)."""

from fastapi.testclient import TestClient

PREFIX = "/gateway/api/v1"


def test_list_services_reports_unreachable(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/services")
    assert response.status_code == 200
    services = response.json()
    assert {s["name"] for s in services} == {
        "portfolio-assistant",
        "deep-research",
    }
    # No downstream is running, so every probe must degrade gracefully.
    assert all(s["health"] == "unreachable" for s in services)


def test_query_unknown_service_returns_404(client: TestClient) -> None:
    response = client.post(f"{PREFIX}/services/does-not-exist/query", json={"x": 1})
    assert response.status_code == 404
    assert response.json()["error_code"] == "service_not_found"


def test_query_known_but_down_returns_503(client: TestClient) -> None:
    response = client.post(f"{PREFIX}/services/portfolio-assistant/query", json={"question": "hi"})
    assert response.status_code == 503
    assert response.json()["error_code"] == "service_unavailable"

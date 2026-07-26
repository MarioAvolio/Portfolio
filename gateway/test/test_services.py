"""Service discovery and query-routing tests (no downstreams running)."""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from gateway.webserver import request_id_ctx
from gateway.webserver.configurations import get_configs
from gateway.webserver.errors import ServiceUnavailableError
from gateway.webserver.services.gateway_service import GatewayService
from gateway.webserver.stores.audit_store import AuditStore

PREFIX = "/gateway/api/v1"


def test_list_services_reports_unreachable(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/services")
    assert response.status_code == 200
    services = response.json()
    assert {s["name"] for s in services} == {
        "portfolio-assistant",
        "deep-research",
        "market-sentinel",
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


def test_job_status_unknown_service_returns_404(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/services/does-not-exist/jobs/some-id")
    assert response.status_code == 404
    assert response.json()["error_code"] == "service_not_found"


def test_job_status_service_without_job_path_returns_404(client: TestClient) -> None:
    """portfolio-assistant is synchronous and declares no job_path."""
    response = client.get(f"{PREFIX}/services/portfolio-assistant/jobs/some-id")
    assert response.status_code == 404
    assert response.json()["error_code"] == "service_not_found"


def test_job_status_known_but_down_returns_503(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/services/market-sentinel/jobs/some-id")
    assert response.status_code == 503
    assert response.json()["error_code"] == "service_unavailable"


def test_registry_job_paths_use_their_own_api_prefix() -> None:
    """Guards against a copy-paste typo in the registry YAML."""
    for service in get_configs().services:
        if service.job_path is not None:
            assert service.job_path.startswith(f"/{service.name}/api/v1/")


def test_url_override_is_derived_for_every_registered_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The override env var is derived from the name, not a hardcoded map.

    Regression test: market-sentinel previously had no entry in the old
    hardcoded map, so MARKET_SENTINEL_URL from docker-compose was silently
    ignored.
    """
    monkeypatch.setenv("PORTFOLIO_ASSISTANT_URL", "http://pa.example:1")
    monkeypatch.setenv("DEEP_RESEARCH_URL", "http://dr.example:1")
    monkeypatch.setenv("MARKET_SENTINEL_URL", "http://ms.example:1")
    get_configs.cache_clear()
    try:
        urls = {service.name: service.base_url for service in get_configs().services}
        assert urls["portfolio-assistant"] == "http://pa.example:1"
        assert urls["deep-research"] == "http://dr.example:1"
        assert urls["market-sentinel"] == "http://ms.example:1"
    finally:
        get_configs.cache_clear()


def _service_with_transport(
    handler, retry_attempts: int = 2, retry_delay_seconds: float = 0.0
) -> GatewayService:
    """Builds a GatewayService whose HTTP calls are intercepted by ``handler``."""
    configs = get_configs().model_copy(
        update={"retry_attempts": retry_attempts, "retry_delay_seconds": retry_delay_seconds}
    )
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return GatewayService(configs=configs, client=client, audit=AuditStore(capacity=10))


def test_request_id_header_is_forwarded_on_query() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["value"] = request.headers.get("X-Request-ID")
        return httpx.Response(200, json={"ok": True})

    service = _service_with_transport(handler)
    token = request_id_ctx.set("abc123")
    try:
        asyncio.run(service.query("portfolio-assistant", {"question": "hi"}))
    finally:
        request_id_ctx.reset(token)
    assert seen["value"] == "abc123"


def test_request_id_header_is_forwarded_on_job_status() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["value"] = request.headers.get("X-Request-ID")
        return httpx.Response(200, json={"status": "done"})

    service = _service_with_transport(handler)
    token = request_id_ctx.set("job-xyz")
    try:
        asyncio.run(service.job_status("deep-research", "job-1"))
    finally:
        request_id_ctx.reset(token)
    assert seen["value"] == "job-xyz"


def test_connect_error_is_retried_and_both_attempts_are_audited() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.ConnectError("boom", request=request)
        return httpx.Response(200, json={"ok": True})

    service = _service_with_transport(handler, retry_attempts=2)
    result = asyncio.run(service.query("portfolio-assistant", {"question": "hi"}))

    assert result.status_code == 200
    assert calls["count"] == 2
    entries = service._audit.recent(10)
    assert [entry.status_code for entry in entries] == [200, 503]  # newest first


def test_retries_are_bounded() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        raise httpx.ConnectError("boom", request=request)

    service = _service_with_transport(handler, retry_attempts=2)
    with pytest.raises(ServiceUnavailableError):
        asyncio.run(service.query("portfolio-assistant", {"question": "hi"}))
    assert calls["count"] == 2


def test_read_timeout_is_not_retried() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        raise httpx.ReadTimeout("boom", request=request)

    service = _service_with_transport(handler, retry_attempts=3)
    with pytest.raises(ServiceUnavailableError):
        asyncio.run(service.query("portfolio-assistant", {"question": "hi"}))
    assert calls["count"] == 1

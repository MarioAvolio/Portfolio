"""Audit trail tests: recording at the choke point and the read endpoint."""

from fastapi.testclient import TestClient

from gateway.webserver.stores.audit_store import AuditStore

PREFIX = "/gateway/api/v1"


def test_routed_calls_are_recorded(client: TestClient) -> None:
    client.post(
        f"{PREFIX}/services/market-sentinel/query", json={"product": "X", "competitors": ["Y"]}
    )
    client.get(f"{PREFIX}/services/market-sentinel/jobs/some-id")

    response = client.get(f"{PREFIX}/audit")
    assert response.status_code == 200
    entries = response.json()

    # A dead port fails to connect, so each routed call is retried once and
    # leaves two entries (the failed attempt and the failed retry) -- see
    # test_services.py for the dedicated retry-count assertions.
    assert len(entries) == 4
    # Newest first: job_status was called after query.
    assert entries[0]["kind"] == entries[1]["kind"] == "job_status"
    assert entries[2]["kind"] == entries[3]["kind"] == "query"
    for entry in entries:
        assert entry["service"] == "market-sentinel"
        assert entry["status_code"] == 503
        assert entry["latency_ms"] >= 0
        assert entry["request_id"]


def test_non_routed_calls_are_not_recorded(client: TestClient) -> None:
    response = client.post(f"{PREFIX}/services/does-not-exist/query", json={})
    assert response.status_code == 404

    client.get(f"{PREFIX}/services")  # three health probes, not routed calls

    assert client.get(f"{PREFIX}/audit").json() == []


def test_ring_buffer_is_bounded() -> None:
    store = AuditStore(capacity=2)
    store.record(service="a", kind="query", status_code=200, latency_ms=1.0)
    store.record(service="b", kind="query", status_code=200, latency_ms=1.0)
    store.record(service="c", kind="query", status_code=200, latency_ms=1.0)

    recent = store.recent(10)
    assert len(recent) == 2
    assert [entry.service for entry in recent] == ["c", "b"]


def test_limit_is_validated(client: TestClient) -> None:
    assert client.get(f"{PREFIX}/audit?limit=0").status_code == 422

    client.post(f"{PREFIX}/services/portfolio-assistant/query", json={"question": "hi"})
    client.post(f"{PREFIX}/services/deep-research/query", json={"query": "hi"})

    response = client.get(f"{PREFIX}/audit?limit=1")
    assert len(response.json()) == 1
    assert response.json()[0]["service"] == "deep-research"

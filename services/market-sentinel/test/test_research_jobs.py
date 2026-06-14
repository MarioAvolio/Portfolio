"""Tests for the async research job endpoints.

All tests run without OPENAI_API_KEY or SERPER_API_KEY.
The SentinelService is mocked or the store is pre-populated.
"""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from market_sentinel.webserver.models.job import JobRecord, JobStatus

PREFIX = "/market-sentinel/api/v1"


def test_submit_returns_202_with_job_id(client: TestClient) -> None:
    """POST /research returns 202 Accepted with job_id and pending status."""
    mock_job = JobRecord(
        job_id="test-job-id",
        product="TestProduct",
        competitors=["CompA", "CompB"],
        status=JobStatus.pending,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    with patch(
        "market_sentinel.webserver.services.sentinel_service.SentinelService.submit",
        new_callable=AsyncMock,
        return_value=mock_job,
    ):
        response = client.post(
            f"{PREFIX}/research",
            json={"product": "TestProduct", "competitors": ["CompA", "CompB"]},
        )

    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "pending"


def test_get_unknown_job_returns_404(client: TestClient) -> None:
    """GET /research/jobs/{id} returns 404 for an unknown job_id."""
    response = client.get(f"{PREFIX}/research/jobs/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error_code"] == "job_not_found"


def test_get_known_job_returns_record(client: TestClient) -> None:
    """GET /research/jobs/{id} returns the record when it exists."""
    from market_sentinel.webserver.dependency.deps import get_job_store

    store = get_job_store()
    asyncio.run(store.create("known-id", "ProductX", ["CompA"]))

    response = client.get(f"{PREFIX}/research/jobs/known-id")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "known-id"
    assert data["status"] == "pending"
    assert data["product"] == "ProductX"
    assert data["competitors"] == ["CompA"]


def test_job_transitions_to_failed(client: TestClient) -> None:
    """GET /research/jobs/{id} reflects failed status after workflow error."""
    from market_sentinel.webserver.dependency.deps import get_job_store

    store = get_job_store()
    asyncio.run(store.create("fail-id", "FailProduct", ["CompX"]))
    asyncio.run(store.set_error("fail-id", "network error"))
    asyncio.run(store.update_status("fail-id", JobStatus.failed))

    response = client.get(f"{PREFIX}/research/jobs/fail-id")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error"] == "network error"


def test_history_returns_list(client: TestClient) -> None:
    """GET /research/history returns a list."""
    with patch(
        "market_sentinel.webserver.services.sentinel_service.SentinelService.get_history",
        new_callable=AsyncMock,
        return_value=[],
    ):
        response = client.get(f"{PREFIX}/research/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_submit_rejects_empty_competitors(client: TestClient) -> None:
    """POST /research returns 422 when competitors list is empty."""
    response = client.post(
        f"{PREFIX}/research",
        json={"product": "X", "competitors": []},
    )
    assert response.status_code == 422


def test_submit_rejects_empty_product(client: TestClient) -> None:
    """POST /research returns 422 when product is empty string."""
    response = client.post(
        f"{PREFIX}/research",
        json={"product": "", "competitors": ["CompA"]},
    )
    assert response.status_code == 422

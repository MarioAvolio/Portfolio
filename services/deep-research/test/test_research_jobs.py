"""Tests for the async research job endpoints.

All tests run without OPENAI_API_KEY -- the ResearchService is mocked or
the store is pre-populated via dependency_overrides.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

import asyncio

from deep_research.webserver.models.job import JobRecord, JobStatus, ResearchStep

PREFIX = "/deep-research/api/v1"


def test_submit_research_returns_202_with_job_id(client: TestClient) -> None:
    """POST /research returns 202 Accepted with job_id and pending status."""
    mock_job = JobRecord(
        job_id="test-job-id",
        query="test query",
        status=JobStatus.pending,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with patch(
        "deep_research.webserver.services.research_service.ResearchService.submit",
        new_callable=AsyncMock,
        return_value=mock_job,
    ):
        response = client.post(f"{PREFIX}/research", json={"query": "test query"})

    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "pending"


def test_get_unknown_job_returns_404(client: TestClient) -> None:
    """GET /research/jobs/{id} returns 404 for a job_id that does not exist."""
    response = client.get(f"{PREFIX}/research/jobs/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error_code"] == "job_not_found"


def test_get_known_job_returns_record(client: TestClient) -> None:
    """GET /research/jobs/{id} returns full record when job exists in the store."""
    from deep_research.webserver.dependency.deps import get_job_store

    store = get_job_store()

    job = asyncio.run(store.create("known-id", "test query"))

    response = client.get(f"{PREFIX}/research/jobs/known-id")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "known-id"
    assert data["status"] == "pending"
    assert data["query"] == "test query"
    assert data["steps"] == []
    assert data["report"] is None


def test_job_transitions_to_failed_when_workflow_errors(client: TestClient) -> None:
    """GET /research/jobs/{id} reflects failed status when the background workflow errors."""
    from deep_research.webserver.dependency.deps import get_job_store

    store = get_job_store()
    asyncio.run(store.create("fail-id", "fail query"))
    asyncio.run(store.set_error("fail-id", "something broke"))
    asyncio.run(store.update_status("fail-id", JobStatus.failed))

    response = client.get(f"{PREFIX}/research/jobs/fail-id")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error"] == "something broke"

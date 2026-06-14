"""Research endpoints for market-sentinel."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from market_sentinel.webserver.dependency.deps import get_sentinel_service
from market_sentinel.webserver.models.job import JobRecord
from market_sentinel.webserver.models.query import SentinelQuery
from market_sentinel.webserver.services.sentinel_service import SentinelService

router = APIRouter(tags=["research"])


@router.post("/research", response_model=JobRecord, status_code=202)
async def submit_research(
    payload: SentinelQuery,
    background_tasks: BackgroundTasks,
    service: Annotated[SentinelService, Depends(get_sentinel_service)],
) -> JobRecord:
    """Submits a competitive intelligence job and returns 202 with job_id.

    Args:
        payload: Product and competitors to analyse.
        background_tasks: FastAPI background task queue.
        service: Injected SentinelService.

    Returns:
        JobRecord with status pending.
    """
    return await service.submit(payload.product, payload.competitors, background_tasks)


@router.get("/research/jobs/{job_id}", response_model=JobRecord)
async def get_job(
    job_id: str,
    service: Annotated[SentinelService, Depends(get_sentinel_service)],
) -> JobRecord:
    """Returns the current state of a research job.

    Args:
        job_id: UUID returned by POST /research.
        service: Injected SentinelService.

    Returns:
        Full JobRecord including report text when done.

    Raises:
        JobNotFoundError: If job_id does not exist (404).
    """
    return await service.get_job(job_id)


@router.get("/research/history")
async def get_history(
    service: Annotated[SentinelService, Depends(get_sentinel_service)],
    limit: int = 20,
) -> list[dict]:
    """Returns recent completed reports from SQLite (newest first).

    Args:
        service: Injected SentinelService.
        limit: Maximum number of records to return (default 20).

    Returns:
        List of report summary dicts: job_id, product, competitors, created_at.
    """
    return await service.get_history(limit)

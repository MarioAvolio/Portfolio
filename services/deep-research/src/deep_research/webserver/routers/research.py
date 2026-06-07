"""Async research job router: submit and poll research jobs."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status

from deep_research.webserver.dependency.deps import get_research_service
from deep_research.webserver.errors import ResearchUnavailableError
from deep_research.webserver.models.job import JobRecord, JobSubmitResponse
from deep_research.webserver.models.query import QueryRequest
from deep_research.webserver.services.research_service import ResearchService

router = APIRouter(tags=["research"])


@router.post("/research", status_code=status.HTTP_202_ACCEPTED, response_model=JobSubmitResponse)
async def submit_research(
    payload: QueryRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[ResearchService, Depends(get_research_service)],
) -> JobSubmitResponse:
    """Submits a research query and returns a job_id immediately (202 Accepted).

    The workflow runs in the background. Poll GET /research/jobs/{job_id} for status.

    Args:
        payload: Research query body.
        background_tasks: FastAPI background task queue.
        service: Injected research service.

    Returns:
        JobSubmitResponse with job_id and initial pending status.
    """
    try:
        job = await service.submit(payload.query, background_tasks)
        return JobSubmitResponse(job_id=job.job_id, status=job.status)
    except Exception as exc:
        raise ResearchUnavailableError(detail=str(exc)) from exc


@router.get("/research/jobs/{job_id}", response_model=JobRecord)
async def get_research_job(
    job_id: str,
    service: Annotated[ResearchService, Depends(get_research_service)],
) -> JobRecord:
    """Returns the current state of a research job.

    Poll this endpoint until status is "done" or "failed".
    When done, the response includes steps (agent trace) and report (markdown).

    Args:
        job_id: Job identifier returned by POST /research.
        service: Injected research service.

    Returns:
        Full JobRecord with status, steps, and report/error when complete.

    Raises:
        JobNotFoundError: Translated to 404 when job_id is unknown.
    """
    return await service.get_job(job_id)

"""Core functional router: deep-research query."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from backend.webserver.dependency.deps import get_research_service
from backend.webserver.models.query import QueryRequest, QueryResponse
from backend.webserver.services.research_service import ResearchService

router = APIRouter(tags=["query"])


@router.post("/query", status_code=status.HTTP_200_OK, response_model=QueryResponse)
async def query(
    payload: QueryRequest,
    service: Annotated[ResearchService, Depends(get_research_service)],
) -> QueryResponse:
    """Runs the multi-agent research workflow and returns the final report.

    Raises:
        ResearchUnavailableError: Translated to ``503`` when the workflow is not
            configured (e.g. missing ``OPENAI_API_KEY``).
    """
    report = await service.research(payload.query)
    return QueryResponse(report=report)

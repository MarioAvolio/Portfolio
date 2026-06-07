"""Core functional router: RAG query."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from portfolio_assistant.webserver.dependency.deps import get_rag_service
from portfolio_assistant.webserver.models.query import QueryRequest, QueryResponse
from portfolio_assistant.webserver.services.rag_service import RagService

router = APIRouter(tags=["query"])


@router.post("/query", status_code=status.HTTP_200_OK, response_model=QueryResponse)
async def query(
    payload: QueryRequest,
    service: Annotated[RagService, Depends(get_rag_service)],
) -> QueryResponse:
    """Answers a question against Mario Avolio's portfolio knowledge base.

    Raises:
        RagUnavailableError: Translated to ``503`` when the pipeline is not
            configured (e.g. missing ``OPENAI_API_KEY``).
    """
    answer, sources = service.answer(payload.question)
    return QueryResponse(answer=answer, sources=sources)

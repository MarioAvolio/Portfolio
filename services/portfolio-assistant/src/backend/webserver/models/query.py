"""Request and response models for the portfolio-assistant ``/query`` endpoint."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Body accepted by ``POST /query``.

    Attributes:
        question: Natural-language question about Mario Avolio's portfolio.
    """

    question: str = Field(min_length=1, max_length=2_000)


class QueryResponse(BaseModel):
    """Grounded answer returned by the RAG pipeline.

    Attributes:
        answer: Generated answer grounded in the retrieved context.
        sources: Source paths of the documents used as context.
    """

    answer: str
    sources: list[str]

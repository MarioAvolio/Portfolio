"""Request and response models for the deep-research ``/query`` endpoint."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Body accepted by ``POST /query``.

    Attributes:
        query: The research request to investigate.
    """

    query: str = Field(min_length=1, max_length=2_000)


class QueryResponse(BaseModel):
    """Final research output.

    Attributes:
        report: The generated markdown research report.
    """

    report: str

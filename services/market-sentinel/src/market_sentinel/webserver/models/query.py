"""Request models for the market-sentinel endpoints."""

from pydantic import BaseModel, Field


class SentinelQuery(BaseModel):
    """Input for a competitive intelligence research job.

    Attributes:
        product: Name of the product or service to analyse.
        competitors: Between 1 and 5 competitor names to compare against.
    """

    product: str = Field(..., min_length=1, max_length=200)
    competitors: list[str] = Field(..., min_length=1, max_length=5)

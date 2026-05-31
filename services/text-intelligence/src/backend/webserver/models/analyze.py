"""Request and response models for the ``/analyze`` endpoint."""

from typing import Literal

from pydantic import BaseModel, Field

Sentiment = Literal["positive", "neutral", "negative"]


class AnalyzeRequest(BaseModel):
    """Payload accepted by ``POST /analyze``.

    Attributes:
        text: Free-form text to analyse. Bounded to keep provider calls cheap.
    """

    text: str = Field(min_length=1, max_length=10_000)


class AnalysisResult(BaseModel):
    """Structured analysis returned to the caller.

    Attributes:
        summary: Short summary of the input text.
        sentiment: Overall sentiment label.
        tags: Salient keywords extracted from the text.
        language: Detected ISO-639-1 language code (best effort).
        model: Identifier of the model/provider that produced the result.
    """

    summary: str
    sentiment: Sentiment
    tags: list[str]
    language: str
    model: str

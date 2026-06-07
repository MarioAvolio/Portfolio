"""Configuration models for the portfolio-assistant service."""

from pydantic import BaseModel, Field


class RagConfig(BaseModel):
    """Tuning knobs for the RAG pipeline.

    Attributes:
        embeddings: Embeddings backend, ``openai`` (default) or ``hf`` (local).
        chunking: Chunking strategy, ``simple`` (default) or ``llm``.
        max_documents: Optional cap on indexed documents (``None`` = all).
    """

    embeddings: str = "openai"
    chunking: str = "simple"
    max_documents: int | None = None


class Configs(BaseModel):
    """Top-level configuration for the portfolio-assistant RAG service.

    Attributes:
        app_name: Logical service name.
        version: Service version surfaced by the status endpoint.
        environment: Short environment label.
        api_prefix: Base URL prefix shared by the functional routers.
        model_name: Chat model used by the RAG generation step.
        rag: RAG pipeline tuning block.
    """

    app_name: str = "portfolio-assistant"
    version: str = "0.1.0"
    environment: str = "local"
    api_prefix: str = "/portfolio-assistant/api/v1"
    model_name: str = "gpt-4.1-nano"
    rag: RagConfig = Field(default_factory=RagConfig)

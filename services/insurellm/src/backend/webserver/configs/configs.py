"""Configuration models for the insurellm service."""

from pydantic import BaseModel


class Configs(BaseModel):
    """Top-level configuration for the insurellm RAG service.

    Attributes:
        app_name: Logical service name.
        version: Service version surfaced by the status endpoint.
        environment: Short environment label.
        api_prefix: Base URL prefix shared by the functional routers.
        model_name: Chat model used by the RAG generation step.
    """

    app_name: str = "insurellm"
    version: str = "0.1.0"
    environment: str = "local"
    api_prefix: str = "/insurellm/api/v1"
    model_name: str = "gpt-4.1-nano"

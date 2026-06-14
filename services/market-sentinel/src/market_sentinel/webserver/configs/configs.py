"""Configuration models for the market-sentinel service."""

from pydantic import BaseModel


class Configs(BaseModel):
    """Top-level configuration for the market-sentinel service.

    Attributes:
        app_name: Logical service name.
        version: Service version surfaced by the status endpoint.
        environment: Short environment label.
        api_prefix: Base URL prefix shared by the functional routers.
        db_path: SQLite file path for the report store.
        openai_model: OpenAI model used by CrewAI agents.
    """

    app_name: str = "market-sentinel"
    version: str = "0.1.0"
    environment: str = "local"
    api_prefix: str = "/market-sentinel/api/v1"
    db_path: str = "market_sentinel.db"
    openai_model: str = "gpt-4o-mini"

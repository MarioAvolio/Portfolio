"""Configuration models for the deep-research service."""

from pydantic import BaseModel


class Configs(BaseModel):
    """Top-level configuration for the deep-research service.

    Attributes:
        app_name: Logical service name.
        version: Service version surfaced by the status endpoint.
        environment: Short environment label.
        api_prefix: Base URL prefix shared by the functional routers.
    """

    app_name: str = "deep-research"
    version: str = "0.1.0"
    environment: str = "local"
    api_prefix: str = "/deep-research/api/v1"

"""Configuration models for the text-intelligence service.

The configuration is expressed as plain Pydantic models with sensible
defaults. Values are populated from the environment by
:mod:`backend.webserver.configurations`, keeping the models themselves free of
any I/O concern so they stay trivially testable.
"""

from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Settings selecting and tuning the active LLM provider.

    Attributes:
        name: Provider identifier (``mock``, ``gemini``, ``openai`` ...).
        model: Model name handed to the provider implementation.
        timeout_seconds: Upper bound for a single provider call.
    """

    name: str = "mock"
    model: str = "mock-1"
    timeout_seconds: int = Field(default=30, ge=1)


class Configs(BaseModel):
    """Top-level configuration model for the text-intelligence service.

    Attributes:
        app_name: Logical name of the service, used in metadata and logs.
        version: Service version surfaced by the status endpoint.
        environment: Short environment label (``local``, ``dev``, ``prod`` ...).
        api_prefix: Base URL prefix shared by every functional router.
        provider: Active LLM provider configuration block.
    """

    app_name: str = "text-intelligence"
    version: str = "0.1.0"
    environment: str = "local"
    api_prefix: str = "/text-intelligence/api/v1"

    provider: ProviderConfig = Field(default_factory=ProviderConfig)

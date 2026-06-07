"""FastAPI dependency wiring.

Resolves the active provider from configuration and assembles the service
graph. Routers depend on these factories rather than constructing concrete
classes, so swapping a provider is a configuration change, not a code change.
"""

from typing import Annotated

from fastapi import Depends

from text_intelligence.ai.providers.base import LLMProvider
from text_intelligence.ai.providers.mock import MockProvider
from text_intelligence.webserver import Configs, get_configs
from text_intelligence.webserver.errors import ProviderNotSupportedError
from text_intelligence.webserver.services.analysis import AnalysisService


def get_provider(configs: Annotated[Configs, Depends(get_configs)]) -> LLMProvider:
    """Returns the LLM provider selected by configuration.

    Args:
        configs: Active service configuration.

    Returns:
        A concrete :class:`LLMProvider`.

    Raises:
        ProviderNotSupportedError: If the configured provider has no
            implementation yet (e.g. ``gemini``/``openai`` arrive later).
    """
    name = configs.provider.name
    if name == "mock":
        return MockProvider(model=configs.provider.model)
    raise ProviderNotSupportedError(provider=name)


def get_analysis_service(
    configs: Annotated[Configs, Depends(get_configs)],
    provider: Annotated[LLMProvider, Depends(get_provider)],
) -> AnalysisService:
    """Returns an :class:`AnalysisService` bound to config and provider."""
    return AnalysisService(configs=configs, provider=provider)

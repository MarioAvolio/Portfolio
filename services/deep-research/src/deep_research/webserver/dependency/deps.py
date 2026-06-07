"""FastAPI dependency wiring for the deep-research service."""

from typing import Annotated

from fastapi import Depends

from deep_research.webserver import Configs, get_configs
from deep_research.webserver.services.research_service import ResearchService


def get_research_service(configs: Annotated[Configs, Depends(get_configs)]) -> ResearchService:
    """Returns a :class:`ResearchService` bound to the active configuration."""
    return ResearchService(configs=configs)

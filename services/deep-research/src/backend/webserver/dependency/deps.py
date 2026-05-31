"""FastAPI dependency wiring for the deep-research service."""

from typing import Annotated

from fastapi import Depends

from backend.webserver import Configs, get_configs
from backend.webserver.services.research_service import ResearchService


def get_research_service(configs: Annotated[Configs, Depends(get_configs)]) -> ResearchService:
    """Returns a :class:`ResearchService` bound to the active configuration."""
    return ResearchService(configs=configs)

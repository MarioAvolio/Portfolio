"""FastAPI dependency wiring for the portfolio-assistant service."""

from typing import Annotated

from fastapi import Depends

from backend.webserver import Configs, get_configs
from backend.webserver.services.rag_service import RagService


def get_rag_service(configs: Annotated[Configs, Depends(get_configs)]) -> RagService:
    """Returns a :class:`RagService` bound to the active configuration."""
    return RagService(configs=configs)

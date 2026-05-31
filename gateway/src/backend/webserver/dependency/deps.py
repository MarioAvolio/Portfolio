"""FastAPI dependency wiring for the gateway."""

from typing import Annotated

from fastapi import Depends

from backend.webserver import Configs, get_configs
from backend.webserver.services.gateway_service import GatewayService


def get_gateway_service(
    configs: Annotated[Configs, Depends(get_configs)],
) -> GatewayService:
    """Returns a :class:`GatewayService` bound to the active registry."""
    return GatewayService(configs=configs)

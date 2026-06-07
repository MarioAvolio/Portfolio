"""FastAPI dependency wiring for the gateway."""

from typing import Annotated

import httpx
from fastapi import Depends, Request

from backend.webserver import Configs, get_configs
from backend.webserver.services.gateway_service import GatewayService


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Returns the shared HTTP client created in the application lifespan."""
    return request.app.state.http_client


def get_gateway_service(
    configs: Annotated[Configs, Depends(get_configs)],
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> GatewayService:
    """Returns a :class:`GatewayService` bound to the registry and HTTP client."""
    return GatewayService(configs=configs, client=client)

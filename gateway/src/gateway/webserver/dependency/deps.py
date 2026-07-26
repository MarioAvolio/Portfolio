"""FastAPI dependency wiring for the gateway."""

from typing import Annotated

import httpx
from fastapi import Depends, Request

from gateway.webserver import Configs, get_configs
from gateway.webserver.services.gateway_service import GatewayService
from gateway.webserver.stores.audit_store import AuditStore


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Returns the shared HTTP client created in the application lifespan."""
    return request.app.state.http_client


def get_audit_store(request: Request) -> AuditStore:
    """Returns the audit store created in the application lifespan."""
    return request.app.state.audit_store


def get_gateway_service(
    configs: Annotated[Configs, Depends(get_configs)],
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    audit: Annotated[AuditStore, Depends(get_audit_store)],
) -> GatewayService:
    """Returns a :class:`GatewayService` bound to the registry, HTTP client and audit store."""
    return GatewayService(configs=configs, client=client, audit=audit)

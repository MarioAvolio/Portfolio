"""FastAPI dependency wiring for the gateway."""

import os
import secrets
from typing import Annotated

import httpx
from fastapi import Depends, Request

from gateway.webserver import Configs, get_configs, get_logger
from gateway.webserver.errors import UnauthorizedError
from gateway.webserver.services.gateway_service import GatewayService
from gateway.webserver.stores.audit_store import AuditStore

logger = get_logger(__name__)


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Returns the shared HTTP client created in the application lifespan."""
    return request.app.state.http_client


def get_audit_store(request: Request) -> AuditStore:
    """Returns the audit store created in the application lifespan."""
    return request.app.state.audit_store


def require_api_key(request: Request) -> None:
    """Checks the ``Authorization: Bearer`` header against ``GATEWAY_API_KEY``.

    Reads the expected key from the environment on every call rather than
    from :class:`Configs`, because a secret must never enter the YAML-built
    config object -- and doing it this way lets a test set the env var with
    no config-cache dance. The comparison is constant-time: a naive ``==`` on
    a shared secret leaks how many leading bytes match through timing.

    If ``GATEWAY_API_KEY`` is unset, the check is a no-op -- auth is opt-in,
    matching how a missing ``OPENAI_API_KEY`` already disables one capability
    elsewhere in the hub without breaking it.

    Args:
        request: The inbound request.

    Raises:
        UnauthorizedError: If the header is missing, malformed, or the token
            does not match.
    """
    expected = os.environ.get("GATEWAY_API_KEY")
    if not expected:
        return

    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not secrets.compare_digest(token, expected):
        logger.warning("Rejected unauthorized request to %s", request.url.path)
        raise UnauthorizedError()


def get_gateway_service(
    configs: Annotated[Configs, Depends(get_configs)],
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    audit: Annotated[AuditStore, Depends(get_audit_store)],
) -> GatewayService:
    """Returns a :class:`GatewayService` bound to the registry, HTTP client and audit store."""
    return GatewayService(configs=configs, client=client, audit=audit)

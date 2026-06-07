"""Routing logic: health aggregation and query proxying.

The gateway is a thin reverse proxy over the service registry. It never
interprets a service's payload schema — it forwards the request body verbatim
and returns the downstream response — which keeps it fully decoupled from each
service's contract. All calls go through a shared :class:`httpx.AsyncClient`
created once at startup (connection pooling).
"""

import asyncio

import httpx

from gateway.webserver import Configs, get_logger
from gateway.webserver.configs.configs import ServiceEndpoint
from gateway.webserver.errors import ServiceNotFoundError, ServiceUnavailableError
from gateway.webserver.models.gateway import QueryResponse, ServiceInfo

logger = get_logger(__name__)

# Health probes use a short timeout regardless of the (larger) query timeout.
_HEALTH_TIMEOUT = 5.0


class GatewayService:
    """Resolves registry entries, probes health and proxies queries."""

    def __init__(self, configs: Configs, client: httpx.AsyncClient) -> None:
        """Binds the gateway to its configuration and the shared HTTP client."""
        self._configs = configs
        self._client = client

    def _endpoint(self, name: str) -> ServiceEndpoint:
        """Returns the registry entry for ``name`` or raises.

        Raises:
            ServiceNotFoundError: If ``name`` is not registered.
        """
        for service in self._configs.services:
            if service.name == name:
                return service
        raise ServiceNotFoundError(service=name)

    async def list_services(self) -> list[ServiceInfo]:
        """Returns every registered service with a live health probe."""
        probes = await asyncio.gather(*(self._probe(service) for service in self._configs.services))
        return list(probes)

    async def _probe(self, service: ServiceEndpoint) -> ServiceInfo:
        """Pings a single service's health path, never raising."""
        health = "unreachable"
        try:
            response = await self._client.get(
                f"{service.base_url}{service.health_path}", timeout=_HEALTH_TIMEOUT
            )
            if response.status_code < 400:
                health = "healthy"
        except httpx.HTTPError:
            logger.info("Service '%s' is unreachable at %s", service.name, service.base_url)
        return ServiceInfo(
            name=service.name,
            description=service.description,
            query_path=service.query_path,
            query_example=service.query_example,
            health=health,
        )

    async def query(self, name: str, payload: dict) -> QueryResponse:
        """Forwards ``payload`` to ``name`` and returns its response.

        Args:
            name: Target service identifier.
            payload: JSON body forwarded verbatim to the service.

        Returns:
            A :class:`QueryResponse` wrapping the downstream result.

        Raises:
            ServiceNotFoundError: If ``name`` is not registered.
            ServiceUnavailableError: If the service cannot be reached.
        """
        service = self._endpoint(name)
        url = f"{service.base_url}{service.query_path}"
        try:
            response = await self._client.post(url, json=payload)
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError(service=name) from exc

        try:
            data = response.json()
        except ValueError:
            data = response.text
        return QueryResponse(service=name, status_code=response.status_code, data=data)

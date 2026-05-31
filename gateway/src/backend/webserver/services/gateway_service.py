"""Routing logic: health aggregation and query proxying.

The gateway is a thin reverse proxy over the service registry. It never
interprets a service's payload schema — it forwards the request body verbatim
and returns the downstream response — which keeps it fully decoupled from each
service's contract.
"""

import asyncio

import httpx

from backend.webserver import Configs, get_logger
from backend.webserver.configs.configs import ServiceEndpoint
from backend.webserver.errors import ServiceNotFoundError, ServiceUnavailableError
from backend.webserver.models.gateway import QueryResponse, ServiceInfo

logger = get_logger(__name__)


class GatewayService:
    """Resolves registry entries, probes health and proxies queries."""

    def __init__(self, configs: Configs) -> None:
        """Binds the gateway to its configuration (and thus its registry)."""
        self._configs = configs

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
        async with httpx.AsyncClient(timeout=5.0) as client:
            probes = await asyncio.gather(
                *(self._probe(client, service) for service in self._configs.services)
            )
        return list(probes)

    async def _probe(self, client: httpx.AsyncClient, service: ServiceEndpoint) -> ServiceInfo:
        """Pings a single service's health path, never raising."""
        health = "unreachable"
        try:
            response = await client.get(f"{service.base_url}{service.health_path}")
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
            async with httpx.AsyncClient(timeout=self._configs.request_timeout_seconds) as client:
                response = await client.post(url, json=payload)
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError(service=name) from exc

        try:
            data = response.json()
        except ValueError:
            data = response.text
        return QueryResponse(service=name, status_code=response.status_code, data=data)

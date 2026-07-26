"""Routing logic: health aggregation and query proxying.

The gateway is a thin reverse proxy over the service registry. It never
interprets a service's payload schema -- it forwards the request body verbatim
and returns the downstream response -- which keeps it fully decoupled from each
service's contract. All calls go through a shared :class:`httpx.AsyncClient`
created once at startup (connection pooling).
"""

import asyncio
import time
from typing import Literal

import httpx

from gateway.webserver import Configs, get_logger
from gateway.webserver.configs.configs import ServiceEndpoint
from gateway.webserver.errors import ServiceNotFoundError, ServiceUnavailableError
from gateway.webserver.models.gateway import AuditKind, QueryResponse, ServiceInfo
from gateway.webserver.stores.audit_store import AuditStore

logger = get_logger(__name__)

# Health probes use a short timeout regardless of the (larger) query timeout.
_HEALTH_TIMEOUT = 5.0


class GatewayService:
    """Resolves registry entries, probes health and proxies queries."""

    def __init__(self, configs: Configs, client: httpx.AsyncClient, audit: AuditStore) -> None:
        """Binds the gateway to its configuration, HTTP client and audit store."""
        self._configs = configs
        self._client = client
        self._audit = audit

    def _record(self, name: str, kind: AuditKind, status_code: int, started: float) -> None:
        """Records one routed call in the audit trail.

        Only called for calls that actually reached (or tried to reach) a
        downstream service -- a ``ServiceNotFoundError`` never gets here, since
        no call was routed.

        Args:
            name: Target service identifier.
            kind: Which routed call site produced this entry.
            status_code: HTTP status code returned by (or assumed for) the call.
            started: ``time.perf_counter()`` value taken before the call.
        """
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        self._audit.record(service=name, kind=kind, status_code=status_code, latency_ms=latency_ms)

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
        """Returns every registered service with a live health probe.

        Returns:
            A list of :class:`ServiceInfo` with health status.
        """
        probes = await asyncio.gather(*(self._probe(service) for service in self._configs.services))
        return list(probes)

    async def _probe(self, service: ServiceEndpoint) -> ServiceInfo:
        """Pings a single service's health path, never raising."""
        health: Literal["healthy", "unreachable"] = "unreachable"
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
        started = time.perf_counter()
        try:
            response = await self._client.post(url, json=payload)
        except httpx.HTTPError as exc:
            self._record(name, "query", ServiceUnavailableError.status_code, started)
            raise ServiceUnavailableError(service=name) from exc
        self._record(name, "query", response.status_code, started)

        try:
            data = response.json()
        except ValueError:
            data = response.text
        return QueryResponse(service=name, status_code=response.status_code, data=data)

    async def job_status(self, name: str, job_id: str) -> QueryResponse:
        """Relays the async job document for ``job_id`` from service ``name``.

        Mirrors :meth:`query`: schema-agnostic, forwards nothing but the job id,
        and returns the downstream body and status code verbatim.

        Args:
            name: Target service identifier.
            job_id: Job identifier previously returned by that service.

        Returns:
            A :class:`QueryResponse` wrapping the downstream job document.

        Raises:
            ServiceNotFoundError: If ``name`` is not registered or does not
                expose async jobs.
            ServiceUnavailableError: If the service cannot be reached.
        """
        service = self._endpoint(name)
        if service.job_path is None:
            raise ServiceNotFoundError(service=name, message="Service does not expose async jobs.")

        url = f"{service.base_url}{service.job_path}/{job_id}"
        started = time.perf_counter()
        try:
            response = await self._client.get(url)
        except httpx.HTTPError as exc:
            self._record(name, "job_status", ServiceUnavailableError.status_code, started)
            raise ServiceUnavailableError(service=name) from exc
        self._record(name, "job_status", response.status_code, started)

        try:
            data = response.json()
        except ValueError:
            data = response.text
        return QueryResponse(service=name, status_code=response.status_code, data=data)

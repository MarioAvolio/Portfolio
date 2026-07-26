"""Models for the gateway API."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

HealthState = Literal["healthy", "unreachable"]
AuditKind = Literal["query", "job_status"]


class ServiceInfo(BaseModel):
    """Registry entry enriched with a live health probe result.

    Attributes:
        name: Service identifier used in gateway routes.
        description: Human-readable summary.
        query_path: Downstream path queries are forwarded to.
        query_example: Example body documenting the service contract.
        health: Outcome of the gateway's liveness probe.
    """

    name: str
    description: str
    query_path: str
    query_example: dict[str, Any]
    health: HealthState


class QueryResponse(BaseModel):
    """Envelope returned when proxying a query to a downstream service.

    Attributes:
        service: Name of the routed service.
        status_code: HTTP status code returned by the downstream service.
        data: Parsed JSON body returned by the downstream service.
    """

    service: str
    status_code: int
    data: Any


class AuditEntry(BaseModel):
    """A single routed call recorded by the gateway's audit trail.

    Attributes:
        service: Name of the routed service.
        kind: Which routed call site produced this entry.
        status_code: HTTP status code returned by (or assumed for) the call.
        latency_ms: Wall-clock time spent waiting on the downstream call.
        timestamp: When the call was recorded (UTC).
        request_id: Correlation id shared with the gateway's log lines.
    """

    service: str
    kind: AuditKind
    status_code: int
    latency_ms: float
    timestamp: datetime
    request_id: str

"""Configuration models for the gateway service.

The gateway owns a small **service registry**: the set of downstream
microservices it can route to. Each entry is static metadata plus a base URL
that is overridable per environment (local, docker-compose, cloud), so the same
image routes correctly wherever it runs.
"""

from pydantic import BaseModel, Field


class ServiceEndpoint(BaseModel):
    """A single downstream microservice the gateway can reach.

    Attributes:
        name: Stable identifier used in gateway routes (``/services/{name}``).
        description: Human-readable summary shown by ``GET /services``.
        base_url: Root URL of the service (host:port), env-overridable.
        health_path: Path the gateway pings to assess liveness.
        query_path: Path the gateway forwards a query payload to.
        query_example: Example request body documenting the service contract.
    """

    name: str
    description: str
    base_url: str
    health_path: str = "/ping"
    query_path: str
    query_example: dict = Field(default_factory=dict)


class Configs(BaseModel):
    """Top-level gateway configuration.

    Attributes:
        app_name: Logical service name.
        version: Service version surfaced by the status endpoint.
        environment: Short environment label.
        api_prefix: Base URL prefix shared by the functional routers.
        request_timeout_seconds: Timeout applied to every downstream call.
        services: The routing registry.
    """

    app_name: str = "gateway"
    version: str = "0.1.0"
    environment: str = "local"
    api_prefix: str = "/gateway/api/v1"
    request_timeout_seconds: float = 60.0

    services: list[ServiceEndpoint] = Field(default_factory=list)

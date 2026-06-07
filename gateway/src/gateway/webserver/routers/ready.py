"""Readiness probe router."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from gateway.webserver.dependency.deps import get_gateway_service
from gateway.webserver.services.gateway_service import GatewayService

router = APIRouter(tags=["ready"])


@router.get("/ready")
async def ready(
    service: Annotated[GatewayService, Depends(get_gateway_service)],
) -> JSONResponse:
    """Readiness probe.

    The gateway is ready when at least one downstream service is reachable;
    otherwise it reports ``503`` so an orchestrator can hold traffic.
    """
    services = await service.list_services()
    healthy = [s.name for s in services if s.health == "healthy"]
    code = 200 if healthy else 503
    return JSONResponse(status_code=code, content={"ready": bool(healthy), "healthy": healthy})

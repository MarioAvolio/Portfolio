"""Core gateway router: service discovery and query routing."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse

from gateway.webserver.dependency.deps import get_gateway_service
from gateway.webserver.models.gateway import ServiceInfo
from gateway.webserver.services.gateway_service import GatewayService

router = APIRouter(tags=["services"])


@router.get("/services", status_code=status.HTTP_200_OK, response_model=list[ServiceInfo])
async def list_services(
    service: Annotated[GatewayService, Depends(get_gateway_service)],
) -> list[ServiceInfo]:
    """Lists every registered service with a live health probe."""
    return await service.list_services()


@router.post("/services/{name}/query")
async def query_service(
    name: str,
    service: Annotated[GatewayService, Depends(get_gateway_service)],
    payload: Annotated[dict, Body(...)],
) -> JSONResponse:
    """Forwards ``payload`` to service ``name`` and relays its response.

    The downstream status code is preserved so the caller sees the true result
    of the routed call.

    Args:
        name: Target service identifier.
        service: Injected gateway service.
        payload: JSON body forwarded verbatim to the downstream service.

    Returns:
        The downstream response wrapped in the gateway envelope.
    """
    result = await service.query(name, payload)
    return JSONResponse(status_code=result.status_code, content=result.model_dump())

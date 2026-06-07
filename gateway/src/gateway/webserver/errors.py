"""Domain errors for the gateway and their HTTP translation."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from gateway.webserver import get_logger

logger = get_logger(__name__)


class GatewayError(Exception):
    """Base class for gateway domain errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    message: str = "Internal error."

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message
        super().__init__(self.message)

    def extra_payload(self) -> dict[str, Any]:
        return {}


class ServiceNotFoundError(GatewayError):
    """Raised when the requested service name is not in the registry.

    Attributes:
        service: The unknown service name.
    """

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "service_not_found"
    message = "Unknown service."

    def __init__(self, service: str, message: str | None = None) -> None:
        super().__init__(message)
        self.service = service

    def extra_payload(self) -> dict[str, Any]:
        return {"service": self.service}


class ServiceUnavailableError(GatewayError):
    """Raised when a downstream service cannot be reached or timed out.

    Attributes:
        service: The unreachable service name.
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "service_unavailable"
    message = "Downstream service is unreachable."

    def __init__(self, service: str, message: str | None = None) -> None:
        super().__init__(message)
        self.service = service

    def extra_payload(self) -> dict[str, Any]:
        return {"service": self.service}


def register_exception_handlers(app: FastAPI) -> None:
    """Registers a handler translating :class:`GatewayError` subclasses."""

    @app.exception_handler(GatewayError)
    async def _handle_gateway_error(_: Request, exc: GatewayError) -> JSONResponse:
        logger.warning("Gateway error -> %s [%s]: %s", exc.status_code, exc.error_code, exc.message)
        body: dict[str, Any] = {"error_code": exc.error_code, "message": exc.message}
        body.update(exc.extra_payload())
        return JSONResponse(status_code=exc.status_code, content=body)

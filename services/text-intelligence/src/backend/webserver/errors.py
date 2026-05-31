"""Domain errors and their HTTP translation.

The service layer stays framework-light by raising plain domain exceptions.
The FastAPI application maps each of them to a deterministic status code and a
canonical JSON envelope via :func:`register_exception_handlers`, keeping
transport concerns out of the business logic.

The envelope returned to the caller is::

    {"error_code": "provider_failed", "message": "Provider call failed."}
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.webserver import get_logger

logger = get_logger(__name__)


class ServiceError(Exception):
    """Base class for every domain error produced by the service.

    Attributes:
        status_code: HTTP status code the error maps to.
        error_code: Machine-readable identifier returned in the envelope.
        message: Human-readable explanation returned to the caller.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    message: str = "Internal error."

    def __init__(self, message: str | None = None) -> None:
        """Initializes the error with an optional overriding message."""
        if message:
            self.message = message
        super().__init__(self.message)

    def extra_payload(self) -> dict[str, Any]:
        """Hook for subclasses to attach additional fields to the JSON body."""
        return {}


class EmptyTextError(ServiceError):
    """Raised when the submitted text is empty or only whitespace."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "empty_text"
    message = "Input text must not be empty."


class ProviderNotSupportedError(ServiceError):
    """Raised when the configured provider name has no implementation.

    Attributes:
        provider: The unsupported provider name read from configuration.
    """

    status_code = status.HTTP_501_NOT_IMPLEMENTED
    error_code = "provider_not_supported"
    message = "Configured LLM provider is not supported."

    def __init__(self, provider: str, message: str | None = None) -> None:
        """Captures the offending provider name for transparent reporting."""
        super().__init__(message)
        self.provider = provider

    def extra_payload(self) -> dict[str, Any]:
        return {"provider": self.provider}


class ProviderFailedError(ServiceError):
    """Raised when the underlying provider call fails or times out."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "provider_failed"
    message = "Provider call failed."


def register_exception_handlers(app: FastAPI) -> None:
    """Registers a single handler translating :class:`ServiceError` subclasses.

    Args:
        app: FastAPI application the handler is attached to.
    """

    @app.exception_handler(ServiceError)
    async def _handle_service_error(_: Request, exc: ServiceError) -> JSONResponse:
        """Serializes a domain error into its mapped HTTP response."""
        logger.warning("Service error -> %s [%s]: %s", exc.status_code, exc.error_code, exc.message)
        body: dict[str, Any] = {"error_code": exc.error_code, "message": exc.message}
        body.update(exc.extra_payload())
        return JSONResponse(status_code=exc.status_code, content=body)

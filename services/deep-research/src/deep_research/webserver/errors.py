"""Domain errors for the deep-research service and their HTTP translation."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from deep_research.webserver import get_logger

logger = get_logger(__name__)


class ServiceError(Exception):
    """Base class for deep-research domain errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    message: str = "Internal error."

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message
        super().__init__(self.message)

    def extra_payload(self) -> dict[str, Any]:
        return {}


class ResearchUnavailableError(ServiceError):
    """Raised when the research workflow cannot run.

    Typical causes: a missing ``OPENAI_API_KEY`` or missing agent dependencies.

    Attributes:
        detail: Low-level cause, surfaced to aid debugging.
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "research_unavailable"
    message = "Research workflow unavailable (check OPENAI_API_KEY / dependencies)."

    def __init__(self, detail: str, message: str | None = None) -> None:
        super().__init__(message)
        self.detail = detail

    def extra_payload(self) -> dict[str, Any]:
        return {"detail": self.detail}


def register_exception_handlers(app: FastAPI) -> None:
    """Registers a handler translating :class:`ServiceError` subclasses."""

    @app.exception_handler(ServiceError)
    async def _handle_service_error(_: Request, exc: ServiceError) -> JSONResponse:
        logger.warning("Service error -> %s [%s]: %s", exc.status_code, exc.error_code, exc.message)
        body: dict[str, Any] = {"error_code": exc.error_code, "message": exc.message}
        body.update(exc.extra_payload())
        return JSONResponse(status_code=exc.status_code, content=body)

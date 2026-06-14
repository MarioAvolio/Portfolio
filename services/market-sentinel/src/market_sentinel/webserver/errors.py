"""Domain errors for market-sentinel and their HTTP translation."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from market_sentinel.webserver import get_logger

logger = get_logger(__name__)


class ServiceError(Exception):
    """Base class for market-sentinel domain errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    message: str = "Internal error."

    def __init__(self, message: str | None = None) -> None:
        """Sets optional override message.

        Args:
            message: Human-readable error message override.
        """
        if message:
            self.message = message
        super().__init__(self.message)

    def extra_payload(self) -> dict[str, Any]:
        """Returns extra fields merged into the error JSON body.

        Returns:
            Extra key-value pairs for the error response.
        """
        return {}


class ResearchUnavailableError(ServiceError):
    """Raised when the CrewAI workflow cannot run."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "research_unavailable"
    message = "Research workflow unavailable (check OPENAI_API_KEY / SERPER_API_KEY)."

    def __init__(self, detail: str, message: str | None = None) -> None:
        """Stores the low-level detail alongside the user-facing message.

        Args:
            detail: Technical cause of the failure.
            message: Optional override for the user-facing message.
        """
        super().__init__(message)
        self.detail = detail

    def extra_payload(self) -> dict[str, Any]:
        """Returns extra fields merged into the error JSON body.

        Returns:
            Dict with ``detail`` key.
        """
        return {"detail": self.detail}


class JobNotFoundError(ServiceError):
    """Raised when a job_id does not exist in the in-memory store."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "job_not_found"
    message = "Job not found."

    def __init__(self, job_id: str) -> None:
        """Stores the unknown job id.

        Args:
            job_id: The id that was not found.
        """
        super().__init__()
        self.job_id = job_id

    def extra_payload(self) -> dict[str, Any]:
        """Returns extra fields merged into the error JSON body.

        Returns:
            Dict with ``job_id`` key.
        """
        return {"job_id": self.job_id}


def register_exception_handlers(app: FastAPI) -> None:
    """Registers a handler translating :class:`ServiceError` subclasses to JSON.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(ServiceError)
    async def _handle(request: Request, exc: ServiceError) -> JSONResponse:
        logger.warning("Service error -> %s [%s]: %s", exc.status_code, exc.error_code, exc.message)
        body: dict[str, Any] = {"error_code": exc.error_code, "message": exc.message}
        body.update(exc.extra_payload())
        return JSONResponse(status_code=exc.status_code, content=body)

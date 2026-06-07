"""Readiness probe router."""

from fastapi import APIRouter, status

router = APIRouter(tags=["ready"])


@router.get("/ready", status_code=status.HTTP_200_OK, response_model=dict)
async def ready() -> dict:
    """Readiness probe.

    The service has no blocking startup dependencies (the LLM provider is
    resolved lazily per request), so it is ready as soon as it is serving.
    """
    return {"ready": True}

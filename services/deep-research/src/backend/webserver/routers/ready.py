"""Readiness probe router."""

from fastapi import APIRouter, status

router = APIRouter(tags=["ready"])


@router.get("/ready", status_code=status.HTTP_200_OK, response_model=dict)
async def ready() -> dict:
    """Readiness probe.

    The agent workflow runs lazily per request, so the service is ready to
    accept traffic as soon as it is serving.
    """
    return {"ready": True}

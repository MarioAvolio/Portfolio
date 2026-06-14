"""Readiness probe -- confirms the service is ready to handle traffic."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/ready", tags=["probes"])
async def ready() -> dict[str, str]:
    """Returns ready when the service is fully initialised.

    Returns:
        Dict with ``status: ready``.
    """
    return {"status": "ready"}

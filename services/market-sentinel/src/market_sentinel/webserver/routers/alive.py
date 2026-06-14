"""Liveness probe -- always returns pong, no dependencies checked."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", tags=["probes"])
async def ping() -> dict[str, str]:
    """Returns pong to confirm the process is running.

    Returns:
        Dict with ``status: pong``.
    """
    return {"status": "pong"}

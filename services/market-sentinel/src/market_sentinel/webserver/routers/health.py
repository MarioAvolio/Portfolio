"""Health probe -- confirms the service is accepting requests."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["probes"])
async def health() -> dict[str, str]:
    """Returns healthy when the process is running.

    Returns:
        Dict with ``status: healthy``.
    """
    return {"status": "healthy"}

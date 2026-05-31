"""Liveness probe router."""

from fastapi import APIRouter, status

router = APIRouter(tags=["alive"])


@router.get("/ping", status_code=status.HTTP_200_OK)
async def ping() -> str:
    """Liveness probe."""
    return "Alive"

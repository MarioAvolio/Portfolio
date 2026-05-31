"""Health probe router."""

from fastapi import APIRouter, status

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK, response_model=dict)
async def health_check() -> dict:
    """Health check."""
    return {"health": "OK"}

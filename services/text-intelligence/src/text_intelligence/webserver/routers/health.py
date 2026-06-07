"""Health probe router."""

from fastapi import APIRouter, status

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK, response_model=dict)
async def health_check() -> dict:
    """Health check.

    Returns:
        A JSON object reporting the service health.
    """
    return {"health": "OK"}

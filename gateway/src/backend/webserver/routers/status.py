"""Service status router."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from backend.webserver import Configs, get_configs

router = APIRouter(tags=["status"])


@router.get("/status", status_code=status.HTTP_200_OK, response_model=dict)
async def service_status(configs: Annotated[Configs, Depends(get_configs)]) -> dict:
    """Reports gateway metadata and the number of registered services."""
    return {
        "app_name": configs.app_name,
        "version": configs.version,
        "environment": configs.environment,
        "registered_services": [s.name for s in configs.services],
    }

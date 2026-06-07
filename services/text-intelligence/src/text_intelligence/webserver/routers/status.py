"""Service status router."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from text_intelligence.webserver import Configs, get_configs

router = APIRouter(tags=["status"])


@router.get("/status", status_code=status.HTTP_200_OK, response_model=dict)
async def service_status(configs: Annotated[Configs, Depends(get_configs)]) -> dict:
    """Reports identifying metadata about the running service.

    Args:
        configs: Active service configuration.

    Returns:
        Service name, version, environment and active provider.
    """
    return {
        "app_name": configs.app_name,
        "version": configs.version,
        "environment": configs.environment,
        "provider": configs.provider.name,
    }

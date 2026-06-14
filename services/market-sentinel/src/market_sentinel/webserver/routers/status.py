"""Status endpoint -- surfaces service metadata."""

from typing import Annotated

from fastapi import APIRouter, Depends

from market_sentinel.webserver import Configs
from market_sentinel.webserver.configurations import get_configs

router = APIRouter()


@router.get("/status", tags=["probes"])
async def service_status(
    configs: Annotated[Configs, Depends(get_configs)],
) -> dict[str, str]:
    """Returns app metadata from the active configuration.

    Args:
        configs: Injected service configuration.

    Returns:
        Dict with ``app_name``, ``version``, and ``environment``.
    """
    return {
        "app_name": configs.app_name,
        "version": configs.version,
        "environment": configs.environment,
    }

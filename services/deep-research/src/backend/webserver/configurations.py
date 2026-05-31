"""Environment-driven loader for the deep-research configuration."""

import os
from functools import lru_cache

from .configs.configs import Configs


@lru_cache
def get_configs() -> Configs:
    """Builds the cached service configuration from the environment."""
    return Configs(
        environment=os.getenv("ENVIRONMENT", "local"),
        api_prefix=os.getenv("API_PREFIX", "/deep-research/api/v1"),
    )

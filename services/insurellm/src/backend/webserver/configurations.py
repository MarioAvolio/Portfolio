"""Environment-driven loader for the insurellm configuration."""

import os
from functools import lru_cache

from .configs.configs import Configs


@lru_cache
def get_configs() -> Configs:
    """Builds the cached service configuration from the environment."""
    return Configs(
        environment=os.getenv("ENVIRONMENT", "local"),
        api_prefix=os.getenv("API_PREFIX", "/insurellm/api/v1"),
        model_name=os.getenv("MODEL_NAME", "gpt-4.1-nano"),
    )

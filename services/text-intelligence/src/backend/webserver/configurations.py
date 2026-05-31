"""Environment-driven loader for the service configuration.

``get_configs`` builds a :class:`Configs` instance from environment variables
and caches it for the process lifetime. Centralising the lookup here keeps the
rest of the codebase decoupled from ``os.environ`` and makes the active
configuration overridable in tests by clearing the cache.
"""

import os
from functools import lru_cache

from .configs.configs import Configs, ProviderConfig


@lru_cache
def get_configs() -> Configs:
    """Builds the cached service configuration from the environment.

    Returns:
        The process-wide :class:`Configs` singleton.
    """
    return Configs(
        environment=os.getenv("ENVIRONMENT", "local"),
        api_prefix=os.getenv("API_PREFIX", "/text-intelligence/api/v1"),
        provider=ProviderConfig(
            name=os.getenv("LLM_PROVIDER", "mock"),
            model=os.getenv("LLM_MODEL", "mock-1"),
            timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        ),
    )

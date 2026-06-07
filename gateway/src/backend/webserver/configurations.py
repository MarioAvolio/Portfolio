"""Configuration loader for the gateway.

Builds the cached :class:`Configs` from the YAML file selected by the active
environment, overlaying it on the Pydantic defaults. Each downstream service's
``base_url`` can additionally be overridden with a ``<NAME>_URL`` environment
variable (e.g. ``TEXT_INTELLIGENCE_URL``), which is how docker-compose injects
the in-network service hostnames.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .configs import CONFIG_FILE, CURRENT_ENV, MODE, ModeExecution
from .configs.configs import Configs

# Maps a registered service name to the env var overriding its base URL.
_URL_ENV = {
    "text-intelligence": "TEXT_INTELLIGENCE_URL",
    "portfolio-assistant": "PORTFOLIO_ASSISTANT_URL",
    "deep-research": "DEEP_RESEARCH_URL",
}


def _read_yaml(path: Path) -> dict[str, Any]:
    """Reads a YAML file and returns the parsed mapping (empty when blank)."""
    with open(path, "r", encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}


@lru_cache(maxsize=1)
def get_configs() -> Configs:
    """Builds and caches the active gateway configuration.

    Returns:
        The process-wide :class:`Configs` singleton.
    """
    overrides: dict[str, Any] = {}
    if MODE == ModeExecution.DEFAULT.value and Path(CONFIG_FILE).exists():
        overrides = _read_yaml(Path(CONFIG_FILE))

    overrides.setdefault("environment", CURRENT_ENV)
    configs = Configs(**overrides)

    for service in configs.services:
        env_url = os.environ.get(_URL_ENV.get(service.name, ""))
        if env_url:
            service.base_url = env_url
    return configs

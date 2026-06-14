"""Configuration loader for the market-sentinel service."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .configs import CONFIG_FILE, CURRENT_ENV, MODE, ModeExecution
from .configs.configs import Configs


def _read_yaml(path: Path) -> dict[str, Any]:
    """Reads a YAML file and returns the parsed mapping.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed dict, empty dict when file is blank.
    """
    with open(path, encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}


@lru_cache(maxsize=1)
def get_configs() -> Configs:
    """Builds and caches the active service configuration.

    Returns:
        The process-wide :class:`Configs` singleton.
    """
    overrides: dict[str, Any] = {}
    if MODE == ModeExecution.DEFAULT.value and Path(CONFIG_FILE).exists():
        overrides = _read_yaml(Path(CONFIG_FILE))
    overrides.setdefault("environment", CURRENT_ENV)
    return Configs(**overrides)

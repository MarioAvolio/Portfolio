"""Environment-derived configuration anchors for the market-sentinel service."""

import os
from enum import StrEnum
from pathlib import Path


class ModeExecution(StrEnum):
    """Supported execution modes.

    Attributes:
        DEFAULT: Standard mode reading configuration from the YAML file.
    """

    DEFAULT = "default"


DEFAULT_ENV = "local"
CURRENT_ENV = os.environ.get("ENVIRONMENT", DEFAULT_ENV)
MODE = os.environ.get("MODE", ModeExecution.DEFAULT.value)

CONFIG_FILES_ANCHOR = (Path(__file__).parent / "files").absolute()
CONFIG_FILE = (
    CONFIG_FILES_ANCHOR / f"{CURRENT_ENV}.yml" if CURRENT_ENV == DEFAULT_ENV else Path("/app/settings/config.yaml")
)

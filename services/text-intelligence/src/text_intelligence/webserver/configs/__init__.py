"""Environment-derived configuration anchors.

No ``.env`` file is used. The active environment is read from the ``ENVIRONMENT``
variable and selects which YAML configuration file the loader overlays on the
Pydantic defaults:

* ``local`` (default) — the bundled ``files/local.yml``.
* any other environment — ``/app/settings/config.yaml`` (e.g. a configmap mounted
  by the platform at deploy time).

Secrets are never stored in these files; they are read from the environment by
the code that needs them.
"""

import os
from enum import Enum
from pathlib import Path


class ModeExecution(str, Enum):
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
    CONFIG_FILES_ANCHOR / f"{CURRENT_ENV}.yml"
    if CURRENT_ENV == DEFAULT_ENV
    else Path("/app/settings/config.yaml")
)

"""Webserver package facade.

Re-exports the handful of symbols the rest of the application depends on so
callers can simply ``from backend.webserver import Configs, get_configs,
get_logger`` without reaching into submodules.
"""

import logging

from .configs.configs import Configs
from .configurations import get_configs

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"

logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    """Returns a module-scoped logger sharing the service log format.

    Args:
        name: Usually ``__name__`` of the calling module.

    Returns:
        A configured :class:`logging.Logger`.
    """
    return logging.getLogger(name)


__all__ = ["Configs", "get_configs", "get_logger"]

"""Webserver package facade for the deep-research service."""

import logging

from .configs.configs import Configs
from .configurations import get_configs

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"

logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    """Returns a module-scoped logger sharing the service log format."""
    return logging.getLogger(name)


__all__ = ["Configs", "get_configs", "get_logger"]

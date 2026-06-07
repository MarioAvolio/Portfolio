"""Webserver package facade for the portfolio-assistant service.

Re-exports the symbols the application depends on and configures structured
logging. A per-request id (set by the request-id middleware) is injected into
every log line via :data:`request_id_ctx`.
"""

import logging
from contextvars import ContextVar

from .configs.configs import Configs
from .configurations import get_configs

#: Correlation id of the in-flight request, surfaced in every log record.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | req=%(request_id)s | %(message)s"
_ROOT_LOGGER = "backend"


class _RequestIdFilter(logging.Filter):
    """Injects the current request id into each log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        setattr(record, "request_id", request_id_ctx.get())
        return True


def _configure() -> None:
    """Configures the ``backend`` logger once (handler, format, level)."""
    root = logging.getLogger(_ROOT_LOGGER)
    if root.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    handler.addFilter(_RequestIdFilter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    root.propagate = False


def get_logger(name: str | None = None) -> logging.Logger:
    """Returns the service logger, or a module-scoped child of it.

    Args:
        name: Usually ``__name__``; module loggers (``backend.*``) propagate to
            the configured ``backend`` logger.

    Returns:
        A configured :class:`logging.Logger`.
    """
    _configure()
    return logging.getLogger(name or _ROOT_LOGGER)


__all__ = ["Configs", "get_configs", "get_logger", "request_id_ctx"]

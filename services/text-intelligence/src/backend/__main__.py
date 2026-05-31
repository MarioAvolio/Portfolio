"""Application entrypoint and FastAPI app factory.

Mirrors the structure used across the production microservices: a ``get_app``
factory wires routers, error handlers and middleware, a ``lifespan`` hook logs
startup/shutdown, and the module is runnable with ``python -m backend`` to serve
the factory through uvicorn.
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from .webserver import get_configs, get_logger
from .webserver.errors import register_exception_handlers
from .webserver.routers import alive, analyze, health, status

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Logs startup and shutdown around the application's serving window.

    Args:
        app: FastAPI application instance owned by the runtime.
    """
    configs = get_configs()
    logger.info(
        "Starting %s (environment=%s, provider=%s, prefix=%s)",
        configs.app_name,
        configs.environment,
        configs.provider.name,
        configs.api_prefix,
    )
    try:
        yield
    finally:
        logger.info("Shutting down %s", configs.app_name)


def get_app() -> FastAPI:
    """Builds and returns the configured FastAPI application.

    The liveness probe (``/ping``) is mounted at the root, while functional and
    health routers live under the configured API prefix.

    Returns:
        Configured :class:`FastAPI` instance.
    """
    configs = get_configs()

    app = FastAPI(
        title=configs.app_name,
        version=configs.version,
        lifespan=lifespan,
    )

    app.include_router(alive.router)
    app.include_router(health.router, prefix=configs.api_prefix)
    app.include_router(status.router, prefix=configs.api_prefix)
    app.include_router(analyze.router, prefix=configs.api_prefix)

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


if __name__ == "__main__":

    async def _serve() -> None:
        """Boots uvicorn against the :func:`get_app` factory."""
        config = Config("backend.__main__:get_app", host="0.0.0.0", port=5000, factory=True)
        await Server(config).serve()

    asyncio.run(_serve())

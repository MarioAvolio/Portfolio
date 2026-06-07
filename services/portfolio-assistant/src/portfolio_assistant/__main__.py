"""Application entrypoint and FastAPI app factory for the portfolio-assistant service."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from .webserver import get_configs, get_logger
from .webserver.errors import register_exception_handlers
from .webserver.middleware import RequestIdMiddleware
from .webserver.routers import alive, health, query, ready, status

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Logs startup and shutdown."""
    configs = get_configs()
    logger.info("Starting %s (environment=%s)", configs.app_name, configs.environment)
    try:
        yield
    finally:
        logger.info("Shutting down %s", configs.app_name)


def get_app() -> FastAPI:
    """Builds and returns the configured portfolio-assistant application."""
    configs = get_configs()

    app = FastAPI(title=configs.app_name, version=configs.version, lifespan=lifespan)

    app.include_router(alive.router)
    app.include_router(health.router, prefix=configs.api_prefix)
    app.include_router(ready.router, prefix=configs.api_prefix)
    app.include_router(status.router, prefix=configs.api_prefix)
    app.include_router(query.router, prefix=configs.api_prefix)

    register_exception_handlers(app)

    app.add_middleware(RequestIdMiddleware)
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
        config = Config("portfolio_assistant.__main__:get_app", host="0.0.0.0", port=5001, factory=True)
        await Server(config).serve()

    asyncio.run(_serve())

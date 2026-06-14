"""Application entrypoint and FastAPI app factory for market-sentinel."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from market_sentinel.webserver import get_configs, get_logger
from market_sentinel.webserver.dependency.deps import get_report_store
from market_sentinel.webserver.errors import register_exception_handlers
from market_sentinel.webserver.middleware import RequestIdMiddleware
from market_sentinel.webserver.routers import alive, health, ready, research, status

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Logs startup/shutdown and initialises the SQLite schema."""
    configs = get_configs()
    logger.info("Starting %s (environment=%s)", configs.app_name, configs.environment)
    await get_report_store().init()
    try:
        yield
    finally:
        logger.info("Shutting down %s", configs.app_name)


def get_app() -> FastAPI:
    """Builds and returns the configured market-sentinel application.

    Returns:
        Configured FastAPI instance.
    """
    configs = get_configs()
    app = FastAPI(title=configs.app_name, version=configs.version, lifespan=lifespan)

    app.include_router(alive.router)
    app.include_router(health.router, prefix=configs.api_prefix)
    app.include_router(ready.router, prefix=configs.api_prefix)
    app.include_router(status.router, prefix=configs.api_prefix)
    app.include_router(research.router, prefix=configs.api_prefix)

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
        """Boots uvicorn against the get_app factory."""
        from uvicorn import Config, Server

        config = Config("market_sentinel.__main__:get_app", host="0.0.0.0", port=5003, factory=True)  # nosec B104
        await Server(config).serve()

    asyncio.run(_serve())

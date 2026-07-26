"""Application entrypoint and FastAPI app factory for the gateway."""

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from .webserver import get_configs, get_logger
from .webserver.errors import register_exception_handlers
from .webserver.middleware import RequestIdMiddleware
from .webserver.routers import alive, audit, health, ready, services, status
from .webserver.stores.audit_store import AuditStore

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manages the shared HTTP client and logs startup/shutdown.

    A single :class:`httpx.AsyncClient` is created for the process and reused by
    every routed call (connection pooling), then closed on shutdown.
    """
    configs = get_configs()
    guarded = "on" if os.environ.get("GATEWAY_API_KEY") else "off"
    logger.info(
        "Starting %s (environment=%s, services=%s, api_key_check=%s)",
        configs.app_name,
        configs.environment,
        [s.name for s in configs.services],
        guarded,
    )
    app.state.http_client = httpx.AsyncClient(timeout=configs.request_timeout_seconds)
    app.state.audit_store = AuditStore(capacity=configs.audit_capacity)
    try:
        yield
    finally:
        await app.state.http_client.aclose()
        logger.info("Shutting down %s", configs.app_name)


def get_app() -> FastAPI:
    """Builds and returns the configured gateway application."""
    configs = get_configs()

    app = FastAPI(title=configs.app_name, version=configs.version, lifespan=lifespan)

    app.include_router(alive.router)
    app.include_router(health.router, prefix=configs.api_prefix)
    app.include_router(ready.router, prefix=configs.api_prefix)
    app.include_router(status.router, prefix=configs.api_prefix)
    app.include_router(services.router, prefix=configs.api_prefix)
    app.include_router(audit.router, prefix=configs.api_prefix)

    register_exception_handlers(app)

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    static_dir = Path(__file__).parent / "webserver" / "static"
    app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="ui")

    return app


if __name__ == "__main__":

    async def _serve() -> None:
        """Boots uvicorn against the :func:`get_app` factory."""
        config = Config("gateway.__main__:get_app", host="0.0.0.0", port=8000, factory=True)
        await Server(config).serve()

    asyncio.run(_serve())

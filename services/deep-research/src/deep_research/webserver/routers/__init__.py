"""Router registry for the deep-research service."""

from deep_research.webserver.routers.alive import router as alive_router
from deep_research.webserver.routers.health import router as health_router
from deep_research.webserver.routers.query import router as query_router
from deep_research.webserver.routers.ready import router as ready_router
from deep_research.webserver.routers.research import router as research_router
from deep_research.webserver.routers.status import router as status_router

__all__ = [
    "alive_router",
    "health_router",
    "query_router",
    "ready_router",
    "research_router",
    "status_router",
]

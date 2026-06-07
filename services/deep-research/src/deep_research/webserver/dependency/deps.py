"""FastAPI dependency wiring for the deep-research service."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from deep_research.webserver import Configs, get_configs
from deep_research.webserver.services.research_service import ResearchService
from deep_research.webserver.stores.job_store import JobStore


@lru_cache(maxsize=1)
def _job_store_singleton() -> JobStore:
    """Returns the process-wide JobStore singleton."""
    return JobStore()


def get_job_store() -> JobStore:
    """Returns the shared in-memory job store.

    Returns:
        The process-wide JobStore instance.
    """
    return _job_store_singleton()


def get_research_service(
    configs: Annotated[Configs, Depends(get_configs)],
    job_store: Annotated[JobStore, Depends(get_job_store)],
) -> ResearchService:
    """Returns a ResearchService bound to the active configuration and job store.

    Args:
        configs: Injected service configuration.
        job_store: Injected job store singleton.

    Returns:
        A configured ResearchService instance.
    """
    return ResearchService(configs=configs, job_store=job_store)

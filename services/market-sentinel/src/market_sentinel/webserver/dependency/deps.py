"""FastAPI dependency wiring for market-sentinel."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from market_sentinel.webserver import Configs, get_configs
from market_sentinel.webserver.services.sentinel_service import SentinelService
from market_sentinel.webserver.stores.job_store import JobStore
from market_sentinel.webserver.stores.report_store import ReportStore


@lru_cache(maxsize=1)
def _job_store_singleton() -> JobStore:
    """Returns the process-wide JobStore singleton."""
    return JobStore()


@lru_cache(maxsize=1)
def _report_store_singleton() -> ReportStore:
    """Returns the process-wide ReportStore singleton."""
    configs = get_configs()
    return ReportStore(db_path=configs.db_path)


def get_job_store() -> JobStore:
    """Returns the shared in-memory job store.

    Returns:
        The process-wide JobStore instance.
    """
    return _job_store_singleton()


def get_report_store() -> ReportStore:
    """Returns the shared SQLite report store.

    Returns:
        The process-wide ReportStore instance.
    """
    return _report_store_singleton()


def get_sentinel_service(
    configs: Annotated[Configs, Depends(get_configs)],
    job_store: Annotated[JobStore, Depends(get_job_store)],
    report_store: Annotated[ReportStore, Depends(get_report_store)],
) -> SentinelService:
    """Returns a SentinelService bound to its dependencies.

    Args:
        configs: Injected service configuration.
        job_store: Injected job store.
        report_store: Injected report store.

    Returns:
        Configured SentinelService.
    """
    return SentinelService(configs=configs, job_store=job_store, report_store=report_store)

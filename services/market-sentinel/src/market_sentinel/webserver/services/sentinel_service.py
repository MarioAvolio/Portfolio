"""Business logic for the market-sentinel service."""

import asyncio
from uuid import uuid4

from fastapi import BackgroundTasks

from market_sentinel.webserver import Configs, get_logger
from market_sentinel.webserver.errors import JobNotFoundError
from market_sentinel.webserver.models.job import JobRecord, JobStatus
from market_sentinel.webserver.stores.job_store import JobStore
from market_sentinel.webserver.stores.report_store import ReportStore

logger = get_logger(__name__)


class SentinelService:
    """Orchestrates job submission, polling, and history retrieval."""

    def __init__(self, configs: Configs, job_store: JobStore, report_store: ReportStore) -> None:
        """Binds the service to its configuration and stores.

        Args:
            configs: Active service configuration.
            job_store: Shared in-memory job tracking store.
            report_store: SQLite persistence store for completed reports.
        """
        self._configs = configs
        self._job_store = job_store
        self._report_store = report_store

    async def submit(self, product: str, competitors: list[str], background_tasks: BackgroundTasks) -> JobRecord:
        """Creates a job and schedules the crew as a background task.

        Args:
            product: Product name to analyse.
            competitors: Competitor names.
            background_tasks: FastAPI BackgroundTasks to enqueue work.

        Returns:
            The newly created JobRecord (status: pending).
        """
        job_id = str(uuid4())
        job = await self._job_store.create(job_id, product, competitors)
        background_tasks.add_task(self._run_job, job_id, product, competitors)
        return job

    async def get_job(self, job_id: str) -> JobRecord:
        """Returns a job record by ID.

        Args:
            job_id: Unique job identifier.

        Returns:
            The matching JobRecord.

        Raises:
            JobNotFoundError: If job_id does not exist.
        """
        job = await self._job_store.get(job_id)
        if job is None:
            raise JobNotFoundError(job_id=job_id)
        return job

    async def get_history(self, limit: int = 20) -> list[dict]:
        """Returns recent completed reports from SQLite.

        Args:
            limit: Maximum number of results.

        Returns:
            List of report summary dicts (no full report text).
        """
        return await self._report_store.list_recent(limit)

    async def _run_job(self, job_id: str, product: str, competitors: list[str]) -> None:
        """Executes the CrewAI crew and updates the job store at each step.

        Runs the synchronous crew in a thread pool so the event loop is not
        blocked while the agents make LLM and search API calls.

        Args:
            job_id: Job to update.
            product: Product being analysed.
            competitors: Competitor names.
        """
        await self._job_store.update_status(job_id, JobStatus.running)
        try:
            from market_sentinel.ai.crew import SentinelCrew

            report = await asyncio.to_thread(SentinelCrew(self._configs.openai_model).run, product, competitors)
            await self._job_store.set_result(job_id, report)
            await self._report_store.save(job_id, product, competitors, report)
            await self._job_store.update_status(job_id, JobStatus.done)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Sentinel job %s failed", job_id)
            await self._job_store.set_error(job_id, str(exc))
            await self._job_store.update_status(job_id, JobStatus.failed)

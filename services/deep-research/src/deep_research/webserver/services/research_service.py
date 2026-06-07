"""Business logic for the deep-research service."""

from uuid import uuid4

from fastapi import BackgroundTasks

from deep_research.webserver import Configs, get_logger
from deep_research.webserver.errors import JobNotFoundError, ResearchUnavailableError
from deep_research.webserver.models.job import JobRecord, JobStatus, ResearchStep
from deep_research.webserver.stores.job_store import JobStore

logger = get_logger(__name__)


class ResearchService:
    """Runs the multi-agent research workflow for a query."""

    def __init__(self, configs: Configs, job_store: JobStore) -> None:
        """Binds the service to its configuration and job store.

        Args:
            configs: Active service configuration.
            job_store: Shared in-memory job store.
        """
        self._configs = configs
        self._job_store = job_store

    async def research(self, query: str) -> str:
        """Runs the workflow synchronously and returns the final markdown report.

        Used by the legacy POST /query endpoint.

        Args:
            query: Research question.

        Returns:
            Markdown report string.

        Raises:
            ResearchUnavailableError: If the workflow cannot run.
        """
        try:
            from deep_research.ai.research_manager import ResearchManager

            report = ""
            async for event in ResearchManager().run(query):
                if event["type"] == "report":
                    report = event["content"]
            return report
        except Exception as exc:
            logger.exception("Research workflow failed")
            raise ResearchUnavailableError(detail=str(exc)) from exc

    async def submit(self, query: str, background_tasks: BackgroundTasks) -> JobRecord:
        """Creates a job and schedules the workflow as a background task.

        Args:
            query: Research question.
            background_tasks: FastAPI BackgroundTasks to enqueue work.

        Returns:
            The newly created JobRecord (status: pending).
        """
        job_id = str(uuid4())
        job = await self._job_store.create(job_id, query)
        background_tasks.add_task(self._run_job, job_id, query)
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

    async def _run_job(self, job_id: str, query: str) -> None:
        """Executes the research workflow and updates the job store at each step.

        Args:
            job_id: Job to update.
            query: Research question.
        """
        await self._job_store.update_status(job_id, JobStatus.running)
        try:
            from datetime import datetime

            from deep_research.ai.research_manager import ResearchManager

            async for event in ResearchManager().run(query):
                if event["type"] == "step":
                    step = ResearchStep(
                        agent=event["agent"],
                        content=event["content"],
                        timestamp=datetime.utcnow(),
                    )
                    await self._job_store.add_step(job_id, step)
                elif event["type"] == "report":
                    await self._job_store.set_result(job_id, event["content"])
            await self._job_store.update_status(job_id, JobStatus.done)
        except Exception as exc:
            logger.exception("Background research job %s failed", job_id)
            await self._job_store.set_error(job_id, str(exc))
            await self._job_store.update_status(job_id, JobStatus.failed)

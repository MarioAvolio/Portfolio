"""In-memory job store for async research jobs."""

import asyncio
from datetime import UTC, datetime

from deep_research.webserver.models.job import JobRecord, JobStatus, ResearchStep


class JobStore:
    """Thread-safe in-memory store for research jobs.

    Uses asyncio.Lock so concurrent coroutines do not corrupt state.
    """

    def __init__(self) -> None:
        """Initialises an empty store."""
        self._jobs: dict[str, JobRecord] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def create(self, job_id: str, query: str) -> JobRecord:
        """Creates and stores a new job in pending state.

        Args:
            job_id: Unique identifier for the job.
            query: Original research question.

        Returns:
            The newly created JobRecord.
        """
        now = datetime.now(UTC)
        job = JobRecord(
            job_id=job_id,
            query=query,
            status=JobStatus.pending,
            created_at=now,
            updated_at=now,
        )
        async with self._lock:
            self._jobs[job_id] = job
        return job

    async def get(self, job_id: str) -> JobRecord | None:
        """Returns the job record or None if not found.

        Args:
            job_id: Unique identifier to look up.

        Returns:
            JobRecord or None.
        """
        return self._jobs.get(job_id)

    async def update_status(self, job_id: str, status: JobStatus) -> None:
        """Updates the status field of an existing job.

        Args:
            job_id: Job to update.
            status: New status value.
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                self._jobs[job_id] = job.model_copy(
                    update={"status": status, "updated_at": datetime.now(UTC)}
                )

    async def add_step(self, job_id: str, step: ResearchStep) -> None:
        """Appends a step to the job's step list.

        Args:
            job_id: Job to update.
            step: Step to append.
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                self._jobs[job_id] = job.model_copy(
                    update={"steps": [*job.steps, step], "updated_at": datetime.now(UTC)}
                )

    async def set_result(self, job_id: str, report: str) -> None:
        """Stores the final markdown report.

        Args:
            job_id: Job to update.
            report: Markdown report string.
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                self._jobs[job_id] = job.model_copy(
                    update={"report": report, "updated_at": datetime.now(UTC)}
                )

    async def set_error(self, job_id: str, error: str) -> None:
        """Stores an error message when the job fails.

        Args:
            job_id: Job to update.
            error: Error description.
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                self._jobs[job_id] = job.model_copy(
                    update={"error": error, "updated_at": datetime.now(UTC)}
                )

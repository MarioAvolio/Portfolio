"""In-memory job store for async research jobs."""

import asyncio
from datetime import UTC, datetime

from market_sentinel.webserver.models.job import JobRecord, JobStatus


class JobStore:
    """Thread-safe in-memory store for research jobs."""

    def __init__(self) -> None:
        """Initialises an empty store."""
        self._jobs: dict[str, JobRecord] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def create(self, job_id: str, product: str, competitors: list[str]) -> JobRecord:
        """Creates and stores a new job in pending state.

        Args:
            job_id: Unique identifier for the job.
            product: Product being analysed.
            competitors: Competitor names.

        Returns:
            The newly created JobRecord.
        """
        now = datetime.now(UTC)
        job = JobRecord(
            job_id=job_id,
            product=product,
            competitors=competitors,
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
                self._jobs[job_id] = job.model_copy(update={"status": status, "updated_at": datetime.now(UTC)})

    async def set_result(self, job_id: str, report: str) -> None:
        """Stores the final markdown report on the job.

        Args:
            job_id: Job to update.
            report: Markdown report string.
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                self._jobs[job_id] = job.model_copy(update={"report": report, "updated_at": datetime.now(UTC)})

    async def set_error(self, job_id: str, error: str) -> None:
        """Stores an error message when the job fails.

        Args:
            job_id: Job to update.
            error: Error description.
        """
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                self._jobs[job_id] = job.model_copy(update={"error": error, "updated_at": datetime.now(UTC)})

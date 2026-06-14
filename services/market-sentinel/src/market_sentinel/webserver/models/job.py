"""Job record models for async research jobs."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class JobStatus(StrEnum):
    """Lifecycle states of an async research job.

    Attributes:
        pending: Accepted but not yet started.
        running: CrewAI crew is executing.
        done: Report generated and persisted.
        failed: Workflow raised an exception.
    """

    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class JobRecord(BaseModel):
    """Snapshot of a single research job.

    Attributes:
        job_id: UUID assigned at submission.
        product: The product being analysed.
        competitors: List of competitor names.
        status: Current lifecycle state.
        report: Markdown report (set when status is done).
        error: Error message (set when status is failed).
        created_at: UTC timestamp of submission.
        updated_at: UTC timestamp of last state change.
    """

    job_id: str
    product: str
    competitors: list[str]
    status: JobStatus
    report: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime

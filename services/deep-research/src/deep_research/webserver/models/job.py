"""Job and step models for the async research endpoint."""

from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel, Field


class JobStatus(str, enum.Enum):
    """Research job lifecycle states."""

    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class ResearchStep(BaseModel):
    """One agent step captured during research.

    Attributes:
        agent: Name of the agent that produced this step.
        content: Human-readable description of what the agent did.
        timestamp: UTC time when the step was recorded.
    """

    agent: str
    content: str
    timestamp: datetime


class JobRecord(BaseModel):
    """Full state of a research job.

    Attributes:
        job_id: Unique identifier (UUID4).
        query: The original research question.
        status: Current lifecycle state.
        steps: Agent steps recorded so far (empty until running).
        report: Final markdown report (present only when done).
        error: Error message (present only when failed).
        created_at: UTC creation time.
        updated_at: UTC last-update time.
    """

    job_id: str
    query: str
    status: JobStatus
    steps: list[ResearchStep] = Field(default_factory=list)
    report: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class JobSubmitResponse(BaseModel):
    """Immediate response to POST /research.

    Attributes:
        job_id: Unique job identifier to use for polling.
        status: Always "pending" on submission.
    """

    job_id: str
    status: JobStatus

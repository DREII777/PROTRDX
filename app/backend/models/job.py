"""Job model definition."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from .job_result import JobResult


class Job(SQLModel, table=True):
    """Represents an execution of the pipeline."""

    id: int | None = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    finished_at: datetime | None = None
    status: str = Field(default="RUNNING")
    summary: str | None = None

    results: list["JobResult"] = Relationship(back_populates="job")

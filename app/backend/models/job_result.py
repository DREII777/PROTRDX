"""Job result model definition."""
from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class JobResult(SQLModel, table=True):
    """Per-ticker results for a job."""

    id: int | None = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    ticker: str
    decision: str
    metrics: dict | None = Field(default=None, sa_column_kwargs={"nullable": True})
    chart_path: str | None = None
    sources: list[str] | None = Field(default=None, sa_column_kwargs={"nullable": True})
    raw_llm: dict | None = Field(default=None, sa_column_kwargs={"nullable": True})
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    job: "Job" = Relationship(back_populates="results")

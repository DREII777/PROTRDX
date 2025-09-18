"""Job schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class JobCreateResponse(BaseModel):
    job_id: int
    status: str


class JobResultRead(BaseModel):
    id: int
    ticker: str
    decision: str
    metrics: dict | None
    chart_path: str | None
    sources: list[str] | None
    raw_llm: dict | None
    created_at: datetime


class JobRead(BaseModel):
    id: int
    started_at: datetime
    finished_at: datetime | None
    status: str
    summary: str | None


class JobWithResults(JobRead):
    results: list[JobResultRead]

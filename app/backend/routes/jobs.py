"""Job listing endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..core.database import get_session
from ..core.security import optional_admin_header
from ..models.job import Job
from ..schemas.job import JobRead, JobWithResults

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs", dependencies=[Depends(optional_admin_header)])
def list_jobs(session: Session = Depends(get_session)) -> list[JobRead]:
    jobs = session.exec(select(Job).order_by(Job.started_at.desc())).all()
    return [
        JobRead(
            id=job.id,
            started_at=job.started_at,
            finished_at=job.finished_at,
            status=job.status,
            summary=job.summary,
        )
        for job in jobs
    ]


@router.get("/jobs/{job_id}", dependencies=[Depends(optional_admin_header)])
def get_job(job_id: int, session: Session = Depends(get_session)) -> JobWithResults:
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    from ..schemas.job import JobResultRead

    return JobWithResults(
        id=job.id,
        started_at=job.started_at,
        finished_at=job.finished_at,
        status=job.status,
        summary=job.summary,
        results=[
            JobResultRead(
                id=result.id,
                ticker=result.ticker,
                decision=result.decision,
                metrics=result.metrics,
                chart_path=result.chart_path,
                sources=result.sources,
                raw_llm=result.raw_llm,
                created_at=result.created_at,
            )
            for result in job.results
        ],
    )

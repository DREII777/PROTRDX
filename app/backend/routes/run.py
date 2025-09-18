"""Endpoints to trigger pipeline runs."""
from __future__ import annotations

import asyncio
from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..core.database import get_session
from ..core.security import admin_required_dependency
from ..models.job import Job
from ..services.pipeline import run_pipeline

router = APIRouter(prefix="/api", tags=["run"])


@router.post("/run", dependencies=[admin_required_dependency()])
async def run_watchlist(session: Session = Depends(get_session)) -> dict:
    job = Job(status="RUNNING")
    session.add(job)
    session.commit()
    session.refresh(job)
    asyncio.create_task(run_pipeline(job_id=job.id))
    return {"job_id": job.id, "status": job.status}


@router.post("/run/{ticker}", dependencies=[admin_required_dependency()])
async def run_single(ticker: str, session: Session = Depends(get_session)) -> dict:
    job = Job(status="RUNNING")
    session.add(job)
    session.commit()
    session.refresh(job)
    asyncio.create_task(run_pipeline(single_ticker=ticker, job_id=job.id))
    return {"job_id": job.id, "status": job.status}

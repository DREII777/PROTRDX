"""APScheduler integration."""
from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..core.config import get_settings
from .pipeline import run_pipeline

logger = logging.getLogger(__name__)


class PipelineScheduler:
    """Wrapper controlling APScheduler lifecycle."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.started = False

    def start(self) -> None:
        if self.started:
            return
        settings = get_settings()
        trigger = CronTrigger(hour=settings.cron_hour, minute=0, timezone=settings.timezone)
        self.scheduler.add_job(self._job_wrapper, trigger=trigger, id="daily-pipeline")
        self.scheduler.start()
        self.started = True
        logger.info("Scheduler started (cron %s:00 %s)", settings.cron_hour, settings.timezone)

    @staticmethod
    def _job_wrapper() -> None:
        from ..core.database import session_scope
        from ..models.job import Job

        with session_scope() as session:
            job = Job()
            session.add(job)
            session.commit()
            session.refresh(job)
            job_id = job.id
        asyncio.create_task(run_pipeline(job_id=job_id))


pipeline_scheduler = PipelineScheduler()

"""FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import init_db
from .routes import charts, jobs, run, settings, watchlist
from .services.scheduler import pipeline_scheduler

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title="PROTRDX Pipeline")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(run.router)
    app.include_router(jobs.router)
    app.include_router(settings.router)
    app.include_router(watchlist.router)
    app.include_router(charts.router)

    @app.on_event("startup")
    async def startup_event() -> None:  # noqa: D401
        """Start scheduler on startup."""

        pipeline_scheduler.start()
        logger.info("Scheduler initialised")

    return app


app = create_app()

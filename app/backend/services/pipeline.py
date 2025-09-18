"""Pipeline orchestrator."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from sqlmodel import select

from ..core.database import session_scope
from ..models.job import Job
from ..models.job_result import JobResult
from ..models.ticker import Ticker
from ..models.setting import Setting
from .backtest import quick_backtest
from .features import build_feature_bundle
from .gatekeeper import apply_gatekeeper
from .research import fetch_news_for_watchlist
from .report import send_report
from .strategy import generate_strategy

logger = logging.getLogger(__name__)


async def run_pipeline(single_ticker: str | None = None, job_id: int | None = None) -> Job:
    """Execute orchestrated pipeline for active tickers."""

    logger.info("Starting pipeline for %s", single_ticker or "watchlist")
    with session_scope() as session:
        if job_id is not None:
            job = session.get(Job, job_id)
        else:
            job = Job()
            session.add(job)
            session.commit()
            session.refresh(job)
        if job is None:
            raise ValueError("Job not found")

    try:
        with session_scope() as session:
            tickers_query = select(Ticker).where(Ticker.active == True)  # noqa: E712
            if single_ticker:
                tickers_query = tickers_query.where(Ticker.symbol == single_ticker)
            tickers = session.exec(tickers_query).all()
            settings = session.get(Setting, 1)
            if not settings:
                settings = Setting()
                session.add(settings)
                session.commit()
        watchlist_payload = [
            {"symbol": ticker.symbol, "market": ticker.market}
            for ticker in tickers
        ]
        research = await fetch_news_for_watchlist([ticker.symbol for ticker in tickers])
        features: dict[str, Any] = {}
        charts: dict[str, str | None] = {}
        dataframes: dict[str, Any] = {}
        for ticker in tickers:
            try:
                bundle = build_feature_bundle(ticker.symbol)
            except Exception as exc:  # noqa: BLE001
                logger.error("Feature generation failed for %s: %s", ticker.symbol, exc)
                continue
            features[ticker.symbol] = bundle.features
            charts[ticker.symbol] = bundle.chart_path
            dataframes[ticker.symbol] = bundle.dataframe
        backtests: dict[str, Any] = {}
        for symbol, df in dataframes.items():
            result = quick_backtest(df)
            backtests[symbol] = result.metrics
        try:
            llm_payload = await generate_strategy(watchlist_payload, research, features, backtests)
        except Exception as exc:  # noqa: BLE001
            logger.error("Strategy generation failed: %s", exc)
            llm_payload = {
                "asof_utc": datetime.utcnow().isoformat(),
                "decisions": [
                    {
                        "ticker": symbol,
                        "playbook": "NO_TRADE",
                        "gatekeeper": {"precheck": "BLOCK", "reasons": ["llm_failed"]},
                    }
                    for symbol in features.keys()
                ],
                "discoveries": [],
                "notes": "LLM unavailable",
            }
        decisions = {item["ticker"]: item for item in llm_payload.get("decisions", []) if item.get("ticker")}
        with session_scope() as session:
            job = session.get(Job, job.id)
            assert job is not None
            job.summary = json.dumps({"discoveries": llm_payload.get("discoveries", [])})
            for ticker in tickers:
                feature_data = features.get(ticker.symbol, {})
                bt_metrics = backtests.get(ticker.symbol, {"status": "INSUFFICIENT_DATA"})
                gatekeeper_status, reasons = apply_gatekeeper(feature_data, bt_metrics)
                decision = decisions.get(ticker.symbol, {
                    "ticker": ticker.symbol,
                    "playbook": "NO_TRADE",
                    "gatekeeper": {"precheck": gatekeeper_status, "reasons": reasons},
                })
                decision.setdefault("gatekeeper", {"precheck": gatekeeper_status, "reasons": reasons})
                if decision["gatekeeper"].get("precheck") != gatekeeper_status:
                    decision["gatekeeper"] = {"precheck": gatekeeper_status, "reasons": reasons}
                job_result = JobResult(
                    job_id=job.id,
                    ticker=ticker.symbol,
                    decision="TRADE_OK" if gatekeeper_status == "PASS" and decision.get("playbook") != "NO_TRADE" else "NO_TRADE",
                    metrics=bt_metrics,
                    chart_path=charts.get(ticker.symbol),
                    sources=decision.get("sources"),
                    raw_llm=decision,
                )
                session.add(job_result)
                if charts.get(ticker.symbol):
                    asyncio.create_task(
                        send_report(
                            ticker.symbol,
                            feature_data,
                            bt_metrics,
                            decision,
                            charts[ticker.symbol],
                        )
                    )
            job.status = "SUCCESS"
            job.finished_at = datetime.utcnow()
            session.add(job)
            session.commit()
            session.refresh(job)
        return job
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline failed: %s", exc)
        with session_scope() as session:
            job = session.get(Job, job.id)
            if job:
                job.status = "FAIL"
                job.summary = str(exc)
                job.finished_at = datetime.utcnow()
                session.add(job)
                session.commit()
                session.refresh(job)
        raise

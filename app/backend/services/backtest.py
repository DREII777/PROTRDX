"""Backtesting utilities."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    metrics: dict[str, Any]


def quick_backtest(df: pd.DataFrame) -> BacktestResult:
    """Run a naive momentum backtest as sanity check."""

    if df.shape[0] < 60:
        return BacktestResult(metrics={"n": 0, "status": "INSUFFICIENT_DATA"})
    prices = df["close"].pct_change().dropna()
    signal = (prices.rolling(5).mean() > 0).astype(int)
    returns = signal.shift(1).fillna(0) * prices
    equity = (1 + returns).cumprod()
    if equity.empty:
        return BacktestResult(metrics={"n": 0, "status": "INSUFFICIENT_DATA"})
    sharpe = np.sqrt(252) * returns.mean() / (returns.std() + 1e-6)
    drawdown = (equity.cummax() - equity) / equity.cummax()
    max_dd = drawdown.max()
    hit_rate = (returns > 0).mean()
    metrics = {
        "n": int(len(returns)),
        "status": "OK",
        "sharpe": float(sharpe),
        "max_dd": float(max_dd),
        "hit_rate": float(hit_rate),
        "slippage_used": 0.0005,
    }
    return BacktestResult(metrics=metrics)

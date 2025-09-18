"""Gatekeeper applying risk filters."""
from __future__ import annotations

from typing import Any

from ..core.config import get_settings


def apply_gatekeeper(features: dict[str, Any], backtest_metrics: dict[str, Any]) -> tuple[str, list[str]]:
    """Return PASS/BLOCK decision with reasons."""

    settings = get_settings()
    reasons: list[str] = []
    spread = float(features.get("spread_pct", 0.0))
    vol_rel = float(features.get("vol_rel", 0.0))
    if spread > settings.max_spread_pct:
        reasons.append("spread above threshold")
    if vol_rel < settings.min_vol_rel:
        reasons.append("vol_rel below minimum")
    if backtest_metrics.get("status") == "INSUFFICIENT_DATA":
        reasons.append("insufficient data")
    else:
        if backtest_metrics.get("n", 0) < settings.min_sample:
            reasons.append("sample too small")
        if float(backtest_metrics.get("sharpe", -1.0)) < settings.min_sharpe:
            reasons.append("sharpe below min")
        if float(backtest_metrics.get("max_dd", 1.0)) > settings.max_dd:
            reasons.append("drawdown above max")
        if float(backtest_metrics.get("hit_rate", 0.0)) < settings.min_hit_rate:
            reasons.append("hit rate below min")
    status = "PASS" if not reasons else "BLOCK"
    return status, reasons

"""Feature computation service."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pandas_ta as ta
import yfinance as yf

logger = logging.getLogger(__name__)

CHARTS_DIR = Path("charts")
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class FeatureResult:
    features: dict
    chart_path: str | None
    dataframe: pd.DataFrame


def get_ohlcv(symbol: str, lookback_days: int = 120) -> pd.DataFrame:
    """Load OHLCV data using yfinance."""

    df = yf.download(symbol, period=f"{lookback_days}d", interval="1d", progress=False)
    if df.empty:
        raise ValueError("No OHLCV data fetched")
    df = df.rename(columns=str.lower)
    df.index = pd.to_datetime(df.index)
    return df


def compute_indicators(df: pd.DataFrame) -> dict:
    """Compute RSI, ATR pct, volume metrics."""

    enriched = df.copy()
    enriched["rsi"] = ta.rsi(enriched["close"], length=14)
    enriched["atr"] = ta.atr(enriched["high"], enriched["low"], enriched["close"], length=14)
    enriched["atr_pct"] = enriched["atr"] / enriched["close"]
    enriched["gap_pct"] = enriched["close"].pct_change()
    vol_avg = enriched["volume"].rolling(20).mean()
    enriched["vol_rel"] = enriched["volume"] / vol_avg
    enriched["spread_pct"] = (enriched["high"] - enriched["low"]) / enriched["close"]
    latest = enriched.iloc[-1].to_dict()
    latest["levels"] = {
        "sma_20": float(enriched["close"].rolling(20).mean().iloc[-1]),
        "sma_50": float(enriched["close"].rolling(50).mean().iloc[-1]),
    }
    return latest


def plot_chart(df: pd.DataFrame, symbol: str) -> str:
    """Generate PNG chart with RSI subplot."""

    fig, (ax_price, ax_rsi) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    df["close"].plot(ax=ax_price, label="Close")
    df["close"].rolling(20).mean().plot(ax=ax_price, label="SMA20")
    ax_price.set_title(f"{symbol} Close")
    ax_price.legend()

    rsi = ta.rsi(df["close"], length=14)
    ax_rsi.plot(df.index, rsi, label="RSI")
    ax_rsi.axhline(70, color="red", linestyle="--", linewidth=0.8)
    ax_rsi.axhline(30, color="green", linestyle="--", linewidth=0.8)
    ax_rsi.set_title("RSI")
    ax_rsi.set_ylim(0, 100)

    fig.tight_layout()
    filename = f"{symbol}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
    path = CHARTS_DIR / filename
    fig.savefig(path)
    plt.close(fig)
    return str(path)


def build_feature_bundle(symbol: str) -> FeatureResult:
    """End-to-end feature computation pipeline."""

    try:
        df = get_ohlcv(symbol)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to download OHLCV for %s: %s", symbol, exc)
        raise
    indicators = compute_indicators(df)
    try:
        chart_path = plot_chart(df.tail(120), symbol)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to generate chart for %s: %s", symbol, exc)
        chart_path = None
    return FeatureResult(features=indicators, chart_path=chart_path, dataframe=df)

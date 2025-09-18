"""Research service retrieving recent news for tickers."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

import httpx

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class NewsProvider(Protocol):
    """Interface for news providers."""

    async def get_news(self, ticker: str) -> list[dict]:
        """Return structured news items for the ticker."""


@dataclass
class _BaseNewsProvider:
    api_key: str | None

    async def _request(self, url: str, payload: dict[str, str]) -> list[dict]:
        if not self.api_key:
            logger.warning("News provider missing API key; returning empty response")
            return []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers={"Authorization": f"Bearer {self.api_key}"})
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # noqa: BLE001
            logger.error("News provider request failed: %s", exc)
            return []
        items = data if isinstance(data, list) else data.get("results", [])
        parsed: list[dict] = []
        for item in items:
            published = item.get("published_at") or item.get("date")
            try:
                published_dt = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else datetime.now(timezone.utc)
            except Exception:  # noqa: BLE001
                published_dt = datetime.now(timezone.utc)
            parsed.append(
                {
                    "title": item.get("title", ""),
                    "date_utc": published_dt.astimezone(timezone.utc).isoformat(),
                    "url": item.get("url") or item.get("link"),
                    "sentiment": item.get("sentiment", "neutral"),
                    "impact_score": float(item.get("impact_score", 0.0)),
                }
            )
        return parsed


class PerplexityNewsProvider(_BaseNewsProvider):
    """Simplified Perplexity API wrapper."""

    async def get_news(self, ticker: str) -> list[dict]:
        payload = {"query": f"Latest market moving news for {ticker}", "size": 5}
        url = "https://api.perplexity.ai/search"
        return await self._request(url, payload)


class TavilyNewsProvider(_BaseNewsProvider):
    """Simplified Tavily API wrapper."""

    async def get_news(self, ticker: str) -> list[dict]:
        payload = {"query": f"{ticker} breaking news", "search_depth": "basic"}
        url = "https://api.tavily.com/search"
        return await self._request(url, payload)


def _provider_factory(provider: str, api_key: str | None) -> NewsProvider:
    if provider == "perplexity":
        return PerplexityNewsProvider(api_key)
    return TavilyNewsProvider(api_key)


async def fetch_news_for_ticker(ticker: str) -> list[dict]:
    """Fetch and filter fresh news for a ticker."""

    settings = get_settings()
    provider = _provider_factory(settings.news_provider, settings.news_api_key)
    items = await provider.get_news(ticker)
    cutoff = datetime.now(timezone.utc) - timedelta(days=1)
    fresh_items = [item for item in items if datetime.fromisoformat(item["date_utc"]).replace(tzinfo=timezone.utc) >= cutoff]
    fresh_items.sort(key=lambda item: (item.get("impact_score", 0.0)), reverse=True)
    return fresh_items


async def fetch_news_for_watchlist(tickers: list[str]) -> dict[str, list[dict]]:
    """Fetch news for each ticker returning JSON serialisable dict."""

    results: dict[str, list[dict]] = {}
    for ticker in tickers:
        try:
            news = await fetch_news_for_ticker(ticker)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to fetch news for %s: %s", ticker, exc)
            news = []
        results[ticker] = news
    return results

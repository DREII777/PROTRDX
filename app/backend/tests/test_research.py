from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from ..services import research


class DummyProvider:
    def __init__(self, items: list[dict]):
        self.items = items

    async def get_news(self, ticker: str) -> list[dict]:
        return self.items


@pytest.mark.asyncio
async def test_fetch_news_filters_old_items(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime.now(timezone.utc)
    items = [
        {
            "title": "Fresh",
            "date_utc": (now - timedelta(hours=1)).isoformat(),
            "url": "http://example.com/fresh",
            "impact_score": 5,
        },
        {
            "title": "Stale",
            "date_utc": (now - timedelta(days=2)).isoformat(),
            "url": "http://example.com/stale",
            "impact_score": 10,
        },
    ]
    monkeypatch.setattr(research, "_provider_factory", lambda provider, api_key: DummyProvider(items))
    result = await research.fetch_news_for_ticker("AAPL")
    assert len(result) == 1
    assert result[0]["title"] == "Fresh"

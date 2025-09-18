from __future__ import annotations

import pytest

from ..services import strategy


@pytest.mark.asyncio
async def test_generate_strategy_builds_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_call(messages, retries=1):  # type: ignore[no-untyped-def]
        assert messages[0]["role"] == "system"
        return {
            "asof_utc": "2024-01-01T00:00:00Z",
            "decisions": [],
            "discoveries": [],
        }

    monkeypatch.setattr(strategy, "call_openai_with_retry", fake_call)
    result = await strategy.generate_strategy([], {}, {}, {})
    assert "decisions" in result

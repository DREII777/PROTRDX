"""Strategy service interacting with LLM."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from ..core.config import get_settings

logger = logging.getLogger(__name__)
PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


async def call_openai_with_retry(messages: list[dict[str, str]], retries: int = 1) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY missing")
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    attempt = 0
    while True:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.2,
                messages=messages,
                response_format={"type": "json_object"},
            )
            message = response.choices[0].message.content
            if not message:
                raise ValueError("Empty response")
            return json.loads(message)
        except Exception as exc:  # noqa: BLE001
            if attempt >= retries:
                raise
            logger.warning("OpenAI call failed (%s); retrying", exc)
            attempt += 1


async def generate_strategy(
    watchlist: list[dict[str, Any]],
    research: dict[str, Any],
    features: dict[str, Any],
    backtests: dict[str, Any],
) -> dict[str, Any]:
    """Generate trading plan via OpenAI."""

    system_prompt = _load_prompt("system_prompt.txt")
    user_template = _load_prompt("user_prompt_template.txt")
    settings = get_settings()
    now_utc = datetime.now(timezone.utc).isoformat()
    user_prompt = user_template.replace("{{now_utc}}", now_utc)
    user_prompt = user_prompt.replace("{{settings_json}}", json.dumps(settings_as_payload(settings)))
    user_prompt = user_prompt.replace("{{watchlist_json}}", json.dumps(watchlist))
    user_prompt = user_prompt.replace("{{research_json}}", json.dumps(research))
    user_prompt = user_prompt.replace("{{features_json}}", json.dumps(features))
    user_prompt = user_prompt.replace("{{backtests_json}}", json.dumps(backtests))
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    try:
        response = await call_openai_with_retry(messages, retries=1)
    except Exception as exc:  # noqa: BLE001
        logger.error("LLM generation failed: %s", exc)
        raise
    return response


def settings_as_payload(settings: Any) -> dict[str, Any]:
    return {
        "size_risk_pct": settings.size_risk_pct,
        "max_spread_pct": settings.max_spread_pct,
        "min_vol_rel": settings.min_vol_rel,
        "min_sharpe": settings.min_sharpe,
        "max_dd": settings.max_dd,
        "min_hit_rate": settings.min_hit_rate,
        "min_sample": settings.min_sample,
    }

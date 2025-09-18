"""Setting model definition."""
from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class Setting(SQLModel, table=True):
    """Persistent singleton settings."""

    id: int | None = Field(default=1, primary_key=True)
    provider: str = Field(default="perplexity")
    news_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    timezone: str = Field(default="Europe/Brussels")
    cron_hour: int = Field(default=7)
    size_risk_pct: float = Field(default=0.75)
    max_spread_pct: float = Field(default=0.15)
    min_vol_rel: float = Field(default=1.2)
    min_sharpe: float = Field(default=0.8)
    max_dd: float = Field(default=0.08)
    min_hit_rate: float = Field(default=0.48)
    min_sample: int = Field(default=30)

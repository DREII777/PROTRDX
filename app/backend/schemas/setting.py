"""Pydantic schemas for settings."""
from __future__ import annotations

from pydantic import BaseModel, Field, validator


class SettingRead(BaseModel):
    provider: str
    news_api_key: str | None = None
    openai_api_key: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    timezone: str
    cron_hour: int
    size_risk_pct: float
    max_spread_pct: float
    min_vol_rel: float
    min_sharpe: float
    max_dd: float
    min_hit_rate: float
    min_sample: int


class SettingUpdate(BaseModel):
    provider: str = Field(..., regex="^(perplexity|tavily)$")
    news_api_key: str | None = None
    openai_api_key: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    timezone: str = Field(default="Europe/Brussels")
    cron_hour: int = Field(default=7, ge=0, le=23)
    size_risk_pct: float = Field(default=0.75, gt=0, lt=5)
    max_spread_pct: float = Field(default=0.15, gt=0, lt=5)
    min_vol_rel: float = Field(default=1.2, gt=0, lt=10)
    min_sharpe: float = Field(default=0.8, gt=-5, lt=5)
    max_dd: float = Field(default=0.08, gt=0, lt=1)
    min_hit_rate: float = Field(default=0.48, gt=0, lt=1)
    min_sample: int = Field(default=30, ge=1)

    @validator("timezone")
    def timezone_not_empty(cls, value: str) -> str:  # noqa: D417
        if not value:
            raise ValueError("timezone cannot be empty")
        return value

"""Configuration utilities for the backend application."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    admin_password: str = Field(..., alias="ADMIN_PASSWORD")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    news_provider: str = Field("perplexity", alias="NEWS_PROVIDER")
    news_api_key: str | None = Field(default=None, alias="NEWS_API_KEY")
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(default=None, alias="TELEGRAM_CHAT_ID")
    timezone: str = Field("Europe/Brussels", alias="TZ")
    cron_hour: int = Field(7, alias="CRON_HOUR")

    size_risk_pct: float = Field(0.75, alias="SIZE_RISK_PCT")
    max_spread_pct: float = Field(0.15, alias="MAX_SPREAD_PCT")
    min_vol_rel: float = Field(1.2, alias="MIN_VOL_REL")
    min_sharpe: float = Field(0.8, alias="MIN_SHARPE")
    max_dd: float = Field(0.08, alias="MAX_DD")
    min_hit_rate: float = Field(0.48, alias="MIN_HIT_RATE")
    min_sample: int = Field(30, alias="MIN_SAMPLE")

    database_url: str = Field(
        default=f"sqlite:///{Path('data').absolute() / 'app.db'}",
        alias="DATABASE_URL",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        allow_population_by_field_name = True

    @validator("news_provider")
    def validate_provider(cls, value: str) -> str:  # noqa: D417
        provider = value.lower()
        if provider not in {"perplexity", "tavily"}:
            raise ValueError("NEWS_PROVIDER must be either 'perplexity' or 'tavily'")
        return provider


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


def settings_as_dict() -> dict[str, Any]:
    """Return settings as serialisable dict for prompts/logging."""

    settings = get_settings()
    return {
        "news_provider": settings.news_provider,
        "timezone": settings.timezone,
        "cron_hour": settings.cron_hour,
        "size_risk_pct": settings.size_risk_pct,
        "max_spread_pct": settings.max_spread_pct,
        "min_vol_rel": settings.min_vol_rel,
        "min_sharpe": settings.min_sharpe,
        "max_dd": settings.max_dd,
        "min_hit_rate": settings.min_hit_rate,
        "min_sample": settings.min_sample,
    }

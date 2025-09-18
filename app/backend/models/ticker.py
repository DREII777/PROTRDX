"""Ticker model definition."""
from __future__ import annotations

from sqlmodel import Field, SQLModel

from .base import TimestampMixin


class Ticker(TimestampMixin, table=True):
    """Tracked instrument in watchlist."""

    id: int | None = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    market: str = Field(default="stock")
    active: bool = Field(default=True)

"""Ticker schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TickerBase(BaseModel):
    symbol: str = Field(..., min_length=1)
    market: str = Field(default="stock", regex="^(stock|crypto|fx)$")
    active: bool = True


class TickerCreate(TickerBase):
    pass


class TickerRead(TickerBase):
    id: int
    created_at: datetime


class TickerUpdate(BaseModel):
    active: bool | None = None

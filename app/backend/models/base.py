"""Base SQLModel definitions."""
from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin providing created_at timestamp."""

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

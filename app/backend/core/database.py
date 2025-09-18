"""Database utilities."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings

_engine = create_engine(get_settings().database_url, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Create database tables if they do not exist."""

    SQLModel.metadata.create_all(_engine)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""

    with Session(_engine) as session:
        yield session


def get_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI endpoints."""

    with Session(_engine) as session:
        yield session

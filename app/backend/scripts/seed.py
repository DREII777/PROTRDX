"""Seed database with initial tickers."""
from __future__ import annotations

from sqlmodel import Session

from ..core.database import init_db, session_scope
from ..models.ticker import Ticker

DEFAULT_TICKERS = [
    ("AAPL", "stock"),
    ("NVDA", "stock"),
    ("MSFT", "stock"),
    ("BTC-USD", "crypto"),
    ("EURUSD=X", "fx"),
]


def seed() -> None:
    init_db()
    with session_scope() as session:
        for symbol, market in DEFAULT_TICKERS:
            _get_or_create(session, symbol, market)
        session.commit()


def _get_or_create(session: Session, symbol: str, market: str) -> None:
    existing = session.exec(
        "SELECT id FROM ticker WHERE symbol = :symbol", {"symbol": symbol}
    ).first()
    if existing:
        return
    ticker = Ticker(symbol=symbol, market=market, active=True)
    session.add(ticker)


if __name__ == "__main__":
    seed()

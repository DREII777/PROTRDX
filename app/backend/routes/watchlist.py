"""Watchlist CRUD endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..core.database import get_session
from ..core.security import admin_required_dependency
from ..models.ticker import Ticker
from ..schemas.ticker import TickerCreate, TickerRead

router = APIRouter(prefix="/api", tags=["watchlist"])


@router.get("/watchlist", response_model=list[TickerRead], dependencies=[admin_required_dependency()])
def list_watchlist(session: Session = Depends(get_session)) -> list[Ticker]:
    tickers = session.exec(select(Ticker).order_by(Ticker.symbol.asc())).all()
    return tickers


@router.post("/watchlist", response_model=TickerRead, dependencies=[admin_required_dependency()])
def create_ticker(payload: TickerCreate, session: Session = Depends(get_session)) -> Ticker:
    existing = session.exec(select(Ticker).where(Ticker.symbol == payload.symbol)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ticker already exists")
    ticker = Ticker(symbol=payload.symbol, market=payload.market, active=payload.active)
    session.add(ticker)
    session.commit()
    session.refresh(ticker)
    return ticker


@router.delete("/watchlist/{ticker_id}", dependencies=[admin_required_dependency()])
def delete_ticker(ticker_id: int, session: Session = Depends(get_session)) -> dict[str, str]:
    ticker = session.get(Ticker, ticker_id)
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
    session.delete(ticker)
    session.commit()
    return {"status": "deleted"}

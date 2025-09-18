"""Reporting utilities for Telegram notifications."""
from __future__ import annotations

import logging
from typing import Any

from telegram import InputFile
from telegram.error import TelegramError
from telegram.ext import Application

from ..core.config import get_settings

logger = logging.getLogger(__name__)


async def send_report(ticker: str, features: dict[str, Any], backtest: dict[str, Any], decision: dict[str, Any], chart_path: str | None) -> None:
    """Send Telegram notification summarising result."""

    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram credentials missing; skipping notification")
        return
    caption_lines = [
        f"Ticker: {ticker}",
        f"Close: {features.get('close', 'n/a'):.2f} | RSI: {features.get('rsi', 0):.1f}",
        f"Decision: {decision.get('playbook', 'NO_TRADE')} ({decision.get('gatekeeper', {}).get('precheck', 'n/a')})",
        f"Reason: {decision.get('reason', '')}",
        f"Backtest: sharpe={backtest.get('sharpe', 'n/a')} hit={backtest.get('hit_rate', 'n/a')} n={backtest.get('n', 0)}",
    ]
    caption = "\n".join(caption_lines)
    try:
        app = Application.builder().token(settings.telegram_bot_token).build()
        if chart_path:
            await app.bot.send_photo(chat_id=settings.telegram_chat_id, photo=InputFile(chart_path), caption=caption)
        else:
            await app.bot.send_message(chat_id=settings.telegram_chat_id, text=caption)
    except TelegramError as exc:
        logger.error("Failed to send Telegram message: %s", exc)
    finally:
        await app.shutdown()

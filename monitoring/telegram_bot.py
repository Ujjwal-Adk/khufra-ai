"""
Khufra Trading System - Telegram Bot
Real-time alerts, daily reports, and kill switch.
"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Telegram notification system.
    Sends trade alerts, regime changes, daily summaries, and handles commands.
    """

    def __init__(self, config):
        self.config = config
        self.bot = None
        self.chat_id = config.secrets.telegram_chat_id
        self.enabled = bool(config.secrets.telegram_bot_token and self.chat_id)
        self._kill_switch_callback = None

    async def start(self):
        """Initialize and start the Telegram bot."""
        if not self.enabled:
            logger.warning("Telegram not configured — notifications disabled")
            return

        try:
            from telegram import Bot
            self.bot = Bot(token=self.config.secrets.telegram_bot_token)
            logger.info("Telegram bot initialized")
            await self.send_message("Khufra Trading System started")
        except ImportError:
            logger.warning("python-telegram-bot not installed — Telegram disabled")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Telegram: {e}")
            self.enabled = False

    async def send_message(self, text: str):
        """Send a message to the configured chat."""
        if not self.enabled or not self.bot:
            logger.debug(f"[TELEGRAM] {text}")
            return

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    async def send_regime_change(self, old_regime: str, new_regime: str, factors: dict):
        """Alert on regime change."""
        msg = (
            f"<b>REGIME CHANGE</b>\n"
            f"{old_regime} -> <b>{new_regime.upper()}</b>\n\n"
            f"ADX: {factors.get('adx', 0):.1f}\n"
            f"ATR Ratio: {factors.get('atr_ratio', 0):.2f}\n"
            f"BB%: {factors.get('bb_percentile', 0):.0f}"
        )
        await self.send_message(msg)

    async def send_trade_alert(self, trade_data: dict, action: str = "OPEN"):
        """Alert on trade entry/exit."""
        if action == "OPEN":
            msg = (
                f"<b>TRADE {action}</b>\n"
                f"ID: {trade_data.get('trade_id', 'N/A')}\n"
                f"Dir: {trade_data.get('direction', '').upper()}\n"
                f"Entry: ${trade_data.get('entry_price', 0):.2f}\n"
                f"SL: ${trade_data.get('stop_loss', 0):.2f}\n"
                f"TP: ${trade_data.get('take_profit', 0):.2f}\n"
                f"Score: {trade_data.get('confidence_score', 0)}\n"
                f"Regime: {trade_data.get('regime', 'N/A')}"
            )
        else:
            pnl = trade_data.get('net_pnl', 0)
            emoji = "+" if pnl >= 0 else ""
            msg = (
                f"<b>TRADE CLOSED</b>\n"
                f"ID: {trade_data.get('trade_id', 'N/A')}\n"
                f"Exit: ${trade_data.get('exit_price', 0):.2f}\n"
                f"Reason: {trade_data.get('exit_reason', 'N/A')}\n"
                f"P&L: {emoji}${pnl:.2f} ({trade_data.get('pnl_pct', 0):.2%})"
            )
        await self.send_message(msg)

    async def send_daily_summary(self, stats: dict):
        """Send daily performance summary."""
        msg = (
            f"<b>DAILY SUMMARY</b>\n"
            f"{'='*20}\n"
            f"Trades: {stats.get('total_trades', 0)}\n"
            f"Win Rate: {stats.get('win_rate', 0):.1f}%\n"
            f"Net P&L: ${stats.get('total_pnl', 0):.2f}\n"
            f"Equity: ${stats.get('equity', 0):.2f}\n"
            f"Return: {stats.get('return_pct', 0):.2f}%\n"
            f"Open: {stats.get('open_positions', 0)}"
        )
        await self.send_message(msg)

    async def send_emergency(self, message: str):
        """Send emergency alert."""
        msg = f"<b>EMERGENCY</b>\n{message}"
        await self.send_message(msg)

    def set_kill_switch_callback(self, callback):
        """Register callback for /kill command."""
        self._kill_switch_callback = callback

    async def stop(self):
        """Stop the Telegram bot."""
        if self.enabled:
            await self.send_message("Khufra Trading System stopped")

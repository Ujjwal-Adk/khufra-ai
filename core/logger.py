"""
Khufra Trading System - Logging Configuration
Sets up comprehensive logging for the entire application.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import colorlog


def setup_logger(
    log_level: str = "INFO",
    log_dir: Path = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> None:
    """Setup logging configuration for the entire application."""
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s %(levelname)-8s%(reset)s %(blue)s[%(name)s]%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    detailed_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | Line:%(lineno)-4d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    if log_dir:
        general_handler = RotatingFileHandler(
            log_dir / "khufra.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        general_handler.setLevel(numeric_level)
        general_handler.setFormatter(file_formatter)
        root_logger.addHandler(general_handler)

        error_handler = RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)

        daily_handler = TimedRotatingFileHandler(
            log_dir / f"daily_{datetime.now().strftime('%Y%m%d')}.log",
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(file_formatter)
        root_logger.addHandler(daily_handler)

    # Silence noisy libraries
    for lib in ["urllib3", "asyncio", "sqlalchemy", "requests", "aiohttp", "websockets"]:
        logging.getLogger(lib).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)


class TradeLogger:
    """Specialized logger for trade-related events."""

    def __init__(self, logger_name: str = "khufra.trades"):
        self.logger = logging.getLogger(logger_name)

    def log_signal_received(self, signal_data: dict):
        self.logger.info(
            f"SIGNAL | Source: {signal_data.get('source')} | "
            f"Pair: {signal_data.get('pair')} | Dir: {signal_data.get('direction')} | "
            f"Confidence: {signal_data.get('confidence', 0):.0f}"
        )

    def log_trade_entry(self, trade_data: dict):
        self.logger.info(
            f"ENTRY | ID: {trade_data.get('trade_id')} | "
            f"Pair: {trade_data.get('pair')} | Dir: {trade_data.get('direction')} | "
            f"Price: ${trade_data.get('entry_price'):.2f} | "
            f"Size: {trade_data.get('position_size'):.4f} | "
            f"SL: ${trade_data.get('stop_loss', 0):.2f} | TP: ${trade_data.get('take_profit', 0):.2f}"
        )

    def log_trade_exit(self, trade_data: dict):
        pnl = trade_data.get('profit_loss', 0)
        status = "WIN" if pnl > 0 else "LOSS"
        self.logger.info(
            f"EXIT [{status}] | ID: {trade_data.get('trade_id')} | "
            f"Price: ${trade_data.get('exit_price'):.2f} | "
            f"P&L: ${pnl:.2f} ({trade_data.get('profit_loss_percent', 0):.2f}%)"
        )

    def log_regime_change(self, old_regime: str, new_regime: str, factors: dict):
        self.logger.info(
            f"REGIME CHANGE | {old_regime} -> {new_regime} | "
            f"ADX: {factors.get('adx', 0):.1f} | ATR ratio: {factors.get('atr_ratio', 0):.2f} | "
            f"BB%: {factors.get('bb_percentile', 0):.0f}"
        )

    def log_confidence_score(self, score: int, breakdown: dict, action: str):
        self.logger.info(
            f"CONFIDENCE | Score: {score}/100 | Action: {action} | "
            f"Regime: {breakdown.get('regime', 0)} | Behavioral: {breakdown.get('behavioral', 0)} | "
            f"Whale: {breakdown.get('whale', 0)} | OB: {breakdown.get('order_book', 0)} | "
            f"FR: {breakdown.get('funding_rate', 0)} | Vol: {breakdown.get('volume', 0)}"
        )

    def log_risk_check(self, passed: bool, reason: str = ""):
        if passed:
            self.logger.info(f"RISK CHECK | PASSED")
        else:
            self.logger.warning(f"RISK CHECK | FAILED | {reason}")

    def log_daily_summary(self, summary: dict):
        self.logger.info("=" * 60)
        self.logger.info("DAILY SUMMARY")
        self.logger.info(f"  Trades: {summary.get('total_trades', 0)}")
        self.logger.info(f"  Win Rate: {summary.get('win_rate', 0):.1f}%")
        self.logger.info(f"  Net P&L: ${summary.get('net_pnl', 0):.2f}")
        self.logger.info(f"  Return: {summary.get('return_percent', 0):.2f}%")
        self.logger.info("=" * 60)

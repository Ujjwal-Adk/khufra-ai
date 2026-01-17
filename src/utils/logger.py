"""
Project Khufra AI - Logging Configuration
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
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> None:
    """
    Setup logging configuration for the entire application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup log files to keep
    """
    # Create log directory if it doesn't exist
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

    # Get numeric log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatters
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

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handlers (if log directory is provided)
    if log_dir:
        # General log file (rotating by size)
        general_log = log_dir / "khufra_ai.log"
        general_handler = RotatingFileHandler(
            general_log,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        general_handler.setLevel(numeric_level)
        general_handler.setFormatter(file_formatter)
        root_logger.addHandler(general_handler)

        # Error log file (only errors and above)
        error_log = log_dir / "errors.log"
        error_handler = RotatingFileHandler(
            error_log,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)

        # Daily log file (rotating by day)
        daily_log = log_dir / f"daily_{datetime.now().strftime('%Y%m%d')}.log"
        daily_handler = TimedRotatingFileHandler(
            daily_log,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(file_formatter)
        root_logger.addHandler(daily_handler)

    # Silence noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    # Log initialization message
    root_logger.info("=" * 60)
    root_logger.info(f"Logging initialized - Level: {log_level}")
    if log_dir:
        root_logger.info(f"Log files location: {log_dir}")
    root_logger.info("=" * 60)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (usually __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


class TradeLogger:
    """
    Specialized logger for trade-related events.
    Provides structured logging for trades with consistent formatting.
    """

    def __init__(self, logger_name: str = "khufra.trades"):
        self.logger = logging.getLogger(logger_name)

    def log_signal_received(self, signal_data: dict):
        """Log when a trading signal is received."""
        self.logger.info(
            f"📊 SIGNAL RECEIVED | "
            f"Source: {signal_data.get('source')} | "
            f"Pair: {signal_data.get('pair')} | "
            f"Direction: {signal_data.get('direction')} | "
            f"Confidence: {signal_data.get('confidence', 0):.2f}"
        )

    def log_trade_entry(self, trade_data: dict):
        """Log when entering a trade."""
        self.logger.info(
            f"🚀 TRADE ENTRY | "
            f"ID: {trade_data.get('trade_id')} | "
            f"Pair: {trade_data.get('pair')} | "
            f"Direction: {trade_data.get('direction')} | "
            f"Entry: ${trade_data.get('entry_price'):.2f} | "
            f"Size: {trade_data.get('position_size'):.4f} | "
            f"SL: ${trade_data.get('stop_loss', 0):.2f} | "
            f"TP: ${trade_data.get('take_profit', 0):.2f}"
        )

    def log_trade_exit(self, trade_data: dict):
        """Log when exiting a trade."""
        pnl = trade_data.get('profit_loss', 0)
        pnl_emoji = "✅" if pnl > 0 else "❌"

        self.logger.info(
            f"{pnl_emoji} TRADE EXIT | "
            f"ID: {trade_data.get('trade_id')} | "
            f"Pair: {trade_data.get('pair')} | "
            f"Exit: ${trade_data.get('exit_price'):.2f} | "
            f"P&L: ${pnl:.2f} ({trade_data.get('profit_loss_percent', 0):.2f}%) | "
            f"Duration: {trade_data.get('duration', 'N/A')}"
        )

    def log_stop_loss_hit(self, trade_data: dict):
        """Log when stop loss is triggered."""
        self.logger.warning(
            f"🛑 STOP LOSS HIT | "
            f"ID: {trade_data.get('trade_id')} | "
            f"Pair: {trade_data.get('pair')} | "
            f"Loss: ${trade_data.get('profit_loss', 0):.2f}"
        )

    def log_take_profit_hit(self, trade_data: dict):
        """Log when take profit is reached."""
        self.logger.info(
            f"🎯 TAKE PROFIT HIT | "
            f"ID: {trade_data.get('trade_id')} | "
            f"Pair: {trade_data.get('pair')} | "
            f"Profit: ${trade_data.get('profit_loss', 0):.2f}"
        )

    def log_risk_check_failed(self, reason: str, details: dict = None):
        """Log when a risk management check fails."""
        self.logger.warning(
            f"⚠️  RISK CHECK FAILED | Reason: {reason} | Details: {details or {}}"
        )

    def log_ai_decision(self, decision: str, reasoning: str, confidence: float):
        """Log AI trading decision."""
        self.logger.info(
            f"🤖 AI DECISION | "
            f"Decision: {decision} | "
            f"Confidence: {confidence:.2f} | "
            f"Reasoning: {reasoning[:100]}..."
        )

    def log_daily_summary(self, summary: dict):
        """Log daily performance summary."""
        self.logger.info("=" * 60)
        self.logger.info("📈 DAILY SUMMARY")
        self.logger.info(f"  Trades: {summary.get('total_trades', 0)}")
        self.logger.info(f"  Winners: {summary.get('winners', 0)}")
        self.logger.info(f"  Losers: {summary.get('losers', 0)}")
        self.logger.info(f"  Win Rate: {summary.get('win_rate', 0):.1f}%")
        self.logger.info(f"  Net P&L: ${summary.get('net_pnl', 0):.2f}")
        self.logger.info(f"  Return: {summary.get('return_percent', 0):.2f}%")
        self.logger.info("=" * 60)


# Example usage in other modules:
# from src.utils.logger import get_logger, TradeLogger
#
# logger = get_logger(__name__)
# trade_logger = TradeLogger()

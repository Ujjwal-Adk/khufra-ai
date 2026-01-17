"""
Project Khufra AI - Helper Functions
Common utility functions used across the application.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Union
import uuid


def generate_trade_id() -> str:
    """
    Generate unique trade ID.

    Returns:
        Unique trade identifier
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(4)
    return f"TRADE_{timestamp}_{random_suffix}"


def generate_signal_id() -> str:
    """
    Generate unique signal ID.

    Returns:
        Unique signal identifier
    """
    return f"SIGNAL_{uuid.uuid4().hex[:12]}"


def calculate_profit_loss(
    entry_price: float,
    exit_price: float,
    position_size: float,
    direction: str,
    fees: float = 0.0
) -> dict:
    """
    Calculate profit/loss for a trade.

    Args:
        entry_price: Entry price
        exit_price: Exit price
        position_size: Position size
        direction: 'long' or 'short'
        fees: Trading fees paid

    Returns:
        Dict with P&L calculations
    """
    if direction.lower() == "long":
        raw_pnl = (exit_price - entry_price) * position_size
    else:  # SHORT
        raw_pnl = (entry_price - exit_price) * position_size

    net_pnl = raw_pnl - fees

    if entry_price > 0:
        pnl_percent = ((exit_price - entry_price) / entry_price) * 100
        if direction.lower() == "short":
            pnl_percent *= -1
    else:
        pnl_percent = 0.0

    return {
        "raw_profit_loss": raw_pnl,
        "net_profit_loss": net_pnl,
        "profit_loss_percent": pnl_percent,
        "fees_paid": fees
    }


def calculate_risk_reward_ratio(
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    direction: str
) -> float:
    """
    Calculate risk/reward ratio for a trade.

    Args:
        entry_price: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
        direction: 'long' or 'short'

    Returns:
        Risk/reward ratio
    """
    if direction.lower() == "long":
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
    else:  # SHORT
        risk = abs(stop_loss - entry_price)
        reward = abs(entry_price - take_profit)

    if risk == 0:
        return 0.0

    return reward / risk


def format_currency(amount: float, decimals: int = 2) -> str:
    """
    Format number as currency.

    Args:
        amount: Amount to format
        decimals: Number of decimal places

    Returns:
        Formatted currency string
    """
    return f"${amount:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format number as percentage.

    Args:
        value: Value to format (as decimal, e.g., 0.05 for 5%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_win_rate(winning_trades: int, total_trades: int) -> float:
    """
    Calculate win rate percentage.

    Args:
        winning_trades: Number of winning trades
        total_trades: Total number of trades

    Returns:
        Win rate as percentage (0-100)
    """
    if total_trades == 0:
        return 0.0
    return (winning_trades / total_trades) * 100


def validate_trading_pair(pair: str) -> bool:
    """
    Validate trading pair format.

    Args:
        pair: Trading pair (e.g., 'BTC/USDT')

    Returns:
        True if valid format
    """
    if not pair or "/" not in pair:
        return False

    parts = pair.split("/")
    if len(parts) != 2:
        return False

    return all(part.strip() and part.isupper() for part in parts)


def hash_string(text: str) -> str:
    """
    Generate SHA-256 hash of string.

    Args:
        text: Text to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(text.encode()).hexdigest()


def is_market_hours(symbol: str = "BTC/USDT") -> bool:
    """
    Check if market is open (crypto markets are 24/7).

    Args:
        symbol: Trading pair

    Returns:
        True (crypto markets always open)
    """
    # Crypto markets are 24/7, but you could add logic for specific markets
    return True


def round_to_precision(value: float, precision: int = 8) -> float:
    """
    Round value to specified precision.

    Args:
        value: Value to round
        precision: Number of decimal places

    Returns:
        Rounded value
    """
    return round(value, precision)


def calculate_sharpe_ratio(
    returns: list,
    risk_free_rate: float = 0.0
) -> float:
    """
    Calculate Sharpe ratio for performance evaluation.

    Args:
        returns: List of period returns
        risk_free_rate: Risk-free rate (default 0)

    Returns:
        Sharpe ratio
    """
    if not returns or len(returns) < 2:
        return 0.0

    import statistics

    avg_return = statistics.mean(returns)
    std_dev = statistics.stdev(returns)

    if std_dev == 0:
        return 0.0

    return (avg_return - risk_free_rate) / std_dev


def get_time_until_next_period(period: str = "day") -> timedelta:
    """
    Get time remaining until next time period.

    Args:
        period: 'hour', 'day', 'week', or 'month'

    Returns:
        Timedelta until next period
    """
    now = datetime.now()

    if period == "hour":
        next_period = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    elif period == "day":
        next_period = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        days_ahead = 6 - now.weekday()
        next_period = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        if now.month == 12:
            next_period = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_period = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        return timedelta(0)

    return next_period - now

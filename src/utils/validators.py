"""
Project Khufra AI - Input Validators
Validates inputs to prevent errors and security issues.
"""

from typing import Optional, Union
import re


def validate_price(price: Union[float, str], allow_zero: bool = False) -> tuple[bool, str]:
    """
    Validate price input.

    Args:
        price: Price to validate
        allow_zero: If True, allow zero prices

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        price_float = float(price)

        if price_float < 0:
            return False, "Price cannot be negative"

        if not allow_zero and price_float == 0:
            return False, "Price cannot be zero"

        return True, ""

    except (ValueError, TypeError):
        return False, "Invalid price format"


def validate_position_size(
    size: Union[float, str],
    min_size: float = 0.0,
    max_size: Optional[float] = None
) -> tuple[bool, str]:
    """
    Validate position size.

    Args:
        size: Position size to validate
        min_size: Minimum allowed size
        max_size: Maximum allowed size (optional)

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        size_float = float(size)

        if size_float <= 0:
            return False, "Position size must be positive"

        if size_float < min_size:
            return False, f"Position size too small (min: {min_size})"

        if max_size and size_float > max_size:
            return False, f"Position size too large (max: {max_size})"

        return True, ""

    except (ValueError, TypeError):
        return False, "Invalid position size format"


def validate_percentage(
    percentage: Union[float, str],
    min_percent: float = 0.0,
    max_percent: float = 100.0
) -> tuple[bool, str]:
    """
    Validate percentage value.

    Args:
        percentage: Percentage to validate (0-100)
        min_percent: Minimum allowed percentage
        max_percent: Maximum allowed percentage

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        percent_float = float(percentage)

        if percent_float < min_percent:
            return False, f"Percentage too low (min: {min_percent}%)"

        if percent_float > max_percent:
            return False, f"Percentage too high (max: {max_percent}%)"

        return True, ""

    except (ValueError, TypeError):
        return False, "Invalid percentage format"


def validate_trading_pair(pair: str) -> tuple[bool, str]:
    """
    Validate trading pair format.

    Args:
        pair: Trading pair (e.g., 'BTC/USDT')

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pair:
        return False, "Trading pair cannot be empty"

    if "/" not in pair:
        return False, "Trading pair must contain '/'"

    parts = pair.split("/")

    if len(parts) != 2:
        return False, "Invalid trading pair format"

    base, quote = parts

    if not base or not quote:
        return False, "Base and quote currencies cannot be empty"

    if not base.isupper() or not quote.isupper():
        return False, "Currencies must be uppercase"

    if len(base) < 2 or len(base) > 10:
        return False, "Invalid base currency length"

    if len(quote) < 2 or len(quote) > 10:
        return False, "Invalid quote currency length"

    return True, ""


def validate_api_key(api_key: str, min_length: int = 16) -> tuple[bool, str]:
    """
    Validate API key format.

    Args:
        api_key: API key to validate
        min_length: Minimum key length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "API key cannot be empty"

    if len(api_key) < min_length:
        return False, f"API key too short (min: {min_length})"

    if not re.match(r'^[A-Za-z0-9_\-]+$', api_key):
        return False, "API key contains invalid characters"

    return True, ""


def validate_trade_direction(direction: str) -> tuple[bool, str]:
    """
    Validate trade direction.

    Args:
        direction: 'long' or 'short'

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_directions = ["long", "short", "buy", "sell"]

    if not direction:
        return False, "Direction cannot be empty"

    if direction.lower() not in valid_directions:
        return False, f"Invalid direction. Must be one of: {', '.join(valid_directions)}"

    return True, ""


def validate_timeframe(timeframe: str) -> tuple[bool, str]:
    """
    Validate timeframe format.

    Args:
        timeframe: Timeframe (e.g., '5m', '1h', '1d')

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_timeframes = [
        "1m", "5m", "15m", "30m",
        "1h", "2h", "4h", "6h", "12h",
        "1d", "1w", "1M"
    ]

    if not timeframe:
        return False, "Timeframe cannot be empty"

    if timeframe not in valid_timeframes:
        return False, f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}"

    return True, ""


def validate_stop_loss_take_profit(
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    direction: str
) -> tuple[bool, str]:
    """
    Validate stop loss and take profit levels.

    Args:
        entry_price: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
        direction: 'long' or 'short'

    Returns:
        Tuple of (is_valid, error_message)
    """
    if entry_price <= 0:
        return False, "Entry price must be positive"

    if stop_loss <= 0:
        return False, "Stop loss must be positive"

    if take_profit <= 0:
        return False, "Take profit must be positive"

    if direction.lower() in ["long", "buy"]:
        if stop_loss >= entry_price:
            return False, "Stop loss must be below entry price for long positions"

        if take_profit <= entry_price:
            return False, "Take profit must be above entry price for long positions"

    elif direction.lower() in ["short", "sell"]:
        if stop_loss <= entry_price:
            return False, "Stop loss must be above entry price for short positions"

        if take_profit >= entry_price:
            return False, "Take profit must be below entry price for short positions"

    else:
        return False, "Invalid direction"

    return True, ""

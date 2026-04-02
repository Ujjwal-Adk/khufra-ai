"""
Khufra Trading System - Risk Manager
Dynamic position sizing + hard safety limits.
V2 Spec Section 8.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class PositionSize:
    """Calculated position sizing."""
    risk_pct: float        # % of equity at risk
    position_usd: float    # position size in USD
    leverage: int
    stop_distance_pct: float
    reasoning: str


class RiskManager:
    """
    Enforces all safety limits and calculates dynamic position sizing.
    NON-NEGOTIABLE limits that cannot be overridden by any strategy.
    """

    def __init__(self, config):
        self.config = config
        self.r = config.risk

        # State tracking
        self.daily_pnl: float = 0.0
        self.daily_start_equity: float = 0.0
        self.day_start: datetime = datetime.utcnow().replace(hour=0, minute=0, second=0)
        self.open_positions: int = 0
        self.consecutive_losses: int = 0
        self.consecutive_api_failures: int = 0
        self.last_data_time: datetime = datetime.utcnow()
        self.trading_halted: bool = False
        self.halt_reason: str = ""

    def set_day_start_equity(self, equity: float):
        """Set starting equity for the day (call at start of each day)."""
        self.daily_start_equity = equity
        self.daily_pnl = 0.0
        self.day_start = datetime.utcnow().replace(hour=0, minute=0, second=0)

    def can_trade(self) -> tuple[bool, str]:
        """
        Check all safety rules. Returns (allowed, reason).
        This is called BEFORE any order is placed.
        """
        # Check trading halt
        if self.trading_halted:
            return False, f"Trading halted: {self.halt_reason}"

        # Check daily drawdown
        if self.daily_start_equity > 0:
            drawdown = abs(self.daily_pnl) / self.daily_start_equity
            if self.daily_pnl < 0 and drawdown >= self.r.max_daily_drawdown:
                self.halt_trading(f"Daily drawdown limit hit: {drawdown:.1%}")
                return False, f"Daily drawdown exceeded: {drawdown:.1%} >= {self.r.max_daily_drawdown:.0%}"

        # Check concurrent positions
        if self.open_positions >= self.r.max_concurrent_positions:
            return False, f"Max concurrent positions: {self.open_positions}/{self.r.max_concurrent_positions}"

        # Check consecutive losses
        if self.consecutive_losses >= self.r.stop_after_consecutive_losses:
            return False, f"Consecutive losses: {self.consecutive_losses}"

        # Check stale data
        data_age = (datetime.utcnow() - self.last_data_time).total_seconds()
        if data_age > self.r.stale_data_timeout_seconds:
            return False, f"Stale data: {data_age:.0f}s since last update"

        # Check API circuit breaker
        if self.consecutive_api_failures >= self.r.error_circuit_breaker:
            self.halt_trading(f"API circuit breaker: {self.consecutive_api_failures} failures")
            return False, f"API circuit breaker tripped: {self.consecutive_api_failures} consecutive failures"

        return True, "OK"

    def calculate_position_size(
        self,
        equity: float,
        risk_pct: float,
        entry_price: float,
        stop_loss: float,
        regime: str,
    ) -> PositionSize:
        """
        Calculate position size from risk parameters.

        Args:
            equity: Current account equity in USD
            risk_pct: Risk % from confidence engine
            entry_price: Planned entry price
            stop_loss: Planned stop loss price
            regime: Current market regime

        Returns:
            PositionSize with calculated values
        """
        # Enforce max risk cap
        effective_risk = min(risk_pct, self.r.max_risk_pct)

        # Calculate stop distance
        stop_distance = abs(entry_price - stop_loss)
        stop_distance_pct = stop_distance / entry_price if entry_price > 0 else 0

        if stop_distance_pct <= 0:
            return PositionSize(
                risk_pct=0, position_usd=0, leverage=1,
                stop_distance_pct=0, reasoning="Invalid stop distance"
            )

        # Risk amount in USD
        risk_usd = equity * effective_risk

        # Position size = risk_amount / stop_distance_pct
        position_usd = risk_usd / stop_distance_pct

        # Apply leverage cap
        max_leverage = self.r.max_leverage
        required_leverage = position_usd / equity if equity > 0 else 999
        leverage = min(int(required_leverage) + 1, max_leverage)

        # Cap position to max leverage * equity
        max_position = equity * max_leverage
        if position_usd > max_position:
            position_usd = max_position

        reasoning = (
            f"Risk: {effective_risk:.1%} of ${equity:.0f} = ${risk_usd:.2f} | "
            f"Stop: {stop_distance_pct:.2%} | Position: ${position_usd:.0f} | "
            f"Leverage: {leverage}x"
        )

        logger.info(f"POSITION SIZE: {reasoning}")

        return PositionSize(
            risk_pct=effective_risk,
            position_usd=position_usd,
            leverage=leverage,
            stop_distance_pct=stop_distance_pct,
            reasoning=reasoning,
        )

    def record_trade_result(self, pnl: float):
        """Update state after a trade closes."""
        self.daily_pnl += pnl
        self.open_positions = max(0, self.open_positions - 1)

        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

    def record_position_opened(self):
        """Track new open position."""
        self.open_positions += 1

    def record_data_received(self):
        """Update last data timestamp."""
        self.last_data_time = datetime.utcnow()

    def record_api_success(self):
        """Reset API failure counter."""
        self.consecutive_api_failures = 0

    def record_api_failure(self):
        """Increment API failure counter."""
        self.consecutive_api_failures += 1

    def halt_trading(self, reason: str):
        """Emergency halt all trading."""
        self.trading_halted = True
        self.halt_reason = reason
        logger.critical(f"TRADING HALTED: {reason}")

    def resume_trading(self):
        """Resume trading after halt."""
        self.trading_halted = False
        self.halt_reason = ""
        self.consecutive_api_failures = 0
        logger.info("Trading resumed")

    def new_day_reset(self, equity: float):
        """Reset daily counters (call at UTC midnight)."""
        self.daily_pnl = 0.0
        self.daily_start_equity = equity
        self.day_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        self.consecutive_losses = 0

        # Auto-resume if halted due to daily limit
        if self.trading_halted and "daily" in self.halt_reason.lower():
            self.resume_trading()
            logger.info("Auto-resumed: new trading day")

    def get_status(self) -> dict:
        """Get current risk manager status."""
        return {
            'trading_halted': self.trading_halted,
            'halt_reason': self.halt_reason,
            'daily_pnl': self.daily_pnl,
            'daily_drawdown': abs(self.daily_pnl) / self.daily_start_equity
                if self.daily_start_equity > 0 else 0,
            'open_positions': self.open_positions,
            'consecutive_losses': self.consecutive_losses,
            'consecutive_api_failures': self.consecutive_api_failures,
            'data_age_seconds': (datetime.utcnow() - self.last_data_time).total_seconds(),
        }

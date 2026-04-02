"""
Khufra Trading System - Paper Trader
Simulated trade execution for paper trading mode.
Full logging as if real but no actual orders.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from utils.helpers import generate_trade_id

logger = logging.getLogger(__name__)


@dataclass
class PaperPosition:
    """A simulated open position."""
    trade_id: str
    symbol: str
    direction: str
    entry_price: float
    position_size_usd: float
    leverage: int
    stop_loss: float
    take_profit: float
    entry_time: datetime
    regime: str
    strategy: str
    confidence_score: int
    score_breakdown: dict = field(default_factory=dict)
    behavioral_pattern: str = ""
    kill_zone: str = ""
    trailing_stop: Optional[float] = None

    @property
    def is_long(self) -> bool:
        return self.direction == "long"


class PaperTrader:
    """
    Simulated trade execution.
    Tracks open positions, checks stops/targets on each price update.
    """

    def __init__(self, config):
        self.config = config
        self.positions: list[PaperPosition] = []
        self.closed_trades: list[dict] = []
        self.equity: float = 3650.0  # $5000 CAD ~ $3650 USD
        self.starting_equity: float = self.equity

    def open_position(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        position_size_usd: float,
        leverage: int,
        stop_loss: float,
        take_profit: float,
        regime: str,
        strategy: str,
        confidence_score: int,
        score_breakdown: dict = None,
        behavioral_pattern: str = "",
        kill_zone: str = "",
    ) -> PaperPosition:
        """Open a simulated position."""
        position = PaperPosition(
            trade_id=generate_trade_id(),
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            position_size_usd=position_size_usd,
            leverage=leverage,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_time=datetime.utcnow(),
            regime=regime,
            strategy=strategy,
            confidence_score=confidence_score,
            score_breakdown=score_breakdown or {},
            behavioral_pattern=behavioral_pattern,
            kill_zone=kill_zone,
        )

        self.positions.append(position)

        logger.info(
            f"PAPER OPEN | {position.trade_id} | {direction.upper()} {symbol} | "
            f"Entry: ${entry_price:.2f} | Size: ${position_size_usd:.0f} | "
            f"SL: ${stop_loss:.2f} | TP: ${take_profit:.2f} | "
            f"Score: {confidence_score} | Regime: {regime}"
        )

        return position

    def check_positions(self, current_price: float) -> list[dict]:
        """
        Check all open positions against current price.
        Close positions that hit SL/TP.
        Returns list of closed trade results.
        """
        results = []
        still_open = []

        for pos in self.positions:
            result = self._check_position(pos, current_price)
            if result:
                results.append(result)
                self.closed_trades.append(result)
                self.equity += result['pnl_usd']
            else:
                # Update trailing stop if applicable
                self._update_trailing_stop(pos, current_price)
                still_open.append(pos)

        self.positions = still_open
        return results

    def _check_position(self, pos: PaperPosition, price: float) -> Optional[dict]:
        """Check if position should be closed."""
        exit_reason = None
        exit_price = price

        if pos.is_long:
            if price <= pos.stop_loss:
                exit_reason = "sl_hit"
                exit_price = pos.stop_loss
            elif price >= pos.take_profit:
                exit_reason = "tp_hit"
                exit_price = pos.take_profit
            elif pos.trailing_stop and price <= pos.trailing_stop:
                exit_reason = "trailing_stop"
                exit_price = pos.trailing_stop
        else:
            if price >= pos.stop_loss:
                exit_reason = "sl_hit"
                exit_price = pos.stop_loss
            elif price <= pos.take_profit:
                exit_reason = "tp_hit"
                exit_price = pos.take_profit
            elif pos.trailing_stop and price >= pos.trailing_stop:
                exit_reason = "trailing_stop"
                exit_price = pos.trailing_stop

        if exit_reason:
            return self._close_position(pos, exit_price, exit_reason)

        return None

    def _close_position(self, pos: PaperPosition, exit_price: float, reason: str) -> dict:
        """Close a position and calculate P&L."""
        if pos.is_long:
            pnl_pct = (exit_price - pos.entry_price) / pos.entry_price
        else:
            pnl_pct = (pos.entry_price - exit_price) / pos.entry_price

        pnl_usd = pnl_pct * pos.position_size_usd

        # Estimate fees (Bitget: 0.02% maker, 0.06% taker)
        fees = pos.position_size_usd * 0.0006 * 2  # entry + exit taker fees

        net_pnl = pnl_usd - fees

        result = {
            'trade_id': pos.trade_id,
            'symbol': pos.symbol,
            'direction': pos.direction,
            'entry_price': pos.entry_price,
            'exit_price': exit_price,
            'entry_time': pos.entry_time,
            'exit_time': datetime.utcnow(),
            'position_size_usd': pos.position_size_usd,
            'leverage': pos.leverage,
            'pnl_pct': pnl_pct,
            'pnl_usd': pnl_usd,
            'fees': fees,
            'net_pnl': net_pnl,
            'exit_reason': reason,
            'regime': pos.regime,
            'strategy': pos.strategy,
            'confidence_score': pos.confidence_score,
            'score_breakdown': pos.score_breakdown,
            'behavioral_pattern': pos.behavioral_pattern,
            'kill_zone': pos.kill_zone,
        }

        status = "WIN" if net_pnl > 0 else "LOSS"
        logger.info(
            f"PAPER CLOSE [{status}] | {pos.trade_id} | {reason} | "
            f"Entry: ${pos.entry_price:.2f} -> Exit: ${exit_price:.2f} | "
            f"P&L: ${net_pnl:.2f} ({pnl_pct:.2%})"
        )

        return result

    def _update_trailing_stop(self, pos: PaperPosition, price: float):
        """Update trailing stop once in profit."""
        if not hasattr(self.config, 'regime'):
            return

        atr_trail = 0  # Would need ATR value; simplified for now
        risk = abs(pos.entry_price - pos.stop_loss)

        if pos.is_long:
            profit = price - pos.entry_price
            if profit >= risk * 1.5:
                # Move stop to breakeven
                new_stop = max(pos.stop_loss, pos.entry_price)
                if pos.trailing_stop is None or new_stop > pos.trailing_stop:
                    pos.trailing_stop = new_stop
        else:
            profit = pos.entry_price - price
            if profit >= risk * 1.5:
                new_stop = min(pos.stop_loss, pos.entry_price)
                if pos.trailing_stop is None or new_stop < pos.trailing_stop:
                    pos.trailing_stop = new_stop

    def force_close_all(self, current_price: float, reason: str = "kill_switch") -> list[dict]:
        """Force close all positions (kill switch)."""
        results = []
        for pos in self.positions:
            result = self._close_position(pos, current_price, reason)
            results.append(result)
            self.closed_trades.append(result)
            self.equity += result['pnl_usd']

        self.positions = []
        logger.warning(f"FORCE CLOSED all positions | Reason: {reason}")
        return results

    def get_stats(self) -> dict:
        """Get paper trading statistics."""
        if not self.closed_trades:
            return {
                'total_trades': 0, 'equity': self.equity,
                'open_positions': len(self.positions),
            }

        wins = [t for t in self.closed_trades if t['net_pnl'] > 0]
        losses = [t for t in self.closed_trades if t['net_pnl'] <= 0]

        return {
            'total_trades': len(self.closed_trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(self.closed_trades) * 100 if self.closed_trades else 0,
            'total_pnl': sum(t['net_pnl'] for t in self.closed_trades),
            'avg_win': sum(t['net_pnl'] for t in wins) / len(wins) if wins else 0,
            'avg_loss': sum(t['net_pnl'] for t in losses) / len(losses) if losses else 0,
            'equity': self.equity,
            'return_pct': (self.equity - self.starting_equity) / self.starting_equity * 100,
            'open_positions': len(self.positions),
        }

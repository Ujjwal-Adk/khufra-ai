"""
Khufra Trading System - Mean Reversion Strategy
Deployed during RANGING regime.
Buy at range bottom, sell at range top, tight stops outside range.
"""

import logging
from typing import Optional
import pandas as pd
import numpy as np

from brain.strategies.base import BaseStrategy, TradeSignal

logger = logging.getLogger(__name__)


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion: trade between support and resistance in ranging markets.
    - Buy near range bottom (support) with stop below
    - Short near range top (resistance) with stop above
    """

    name = "mean_reversion"
    regime = "ranging"

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: dict,
        current_price: float,
    ) -> Optional[TradeSignal]:
        if len(df) < 30:
            return None

        atr = indicators['atr'].iloc[-1]
        bb_upper = indicators['bb_upper'].iloc[-1]
        bb_lower = indicators['bb_lower'].iloc[-1]
        bb_middle = indicators['bb_middle'].iloc[-1]

        if any(np.isnan(v) for v in [atr, bb_upper, bb_lower, bb_middle]):
            return None

        # Define range from recent highs/lows
        lookback = 20
        range_high = df['high'].iloc[-lookback:].max()
        range_low = df['low'].iloc[-lookback:].min()
        range_size = range_high - range_low

        if range_size <= 0:
            return None

        # Position within range (0 = bottom, 1 = top)
        position_in_range = (current_price - range_low) / range_size

        # Long near bottom (within 20% of range bottom)
        if position_in_range <= 0.2:
            return self._long_at_support(
                df, current_price, range_low, range_high, bb_middle, atr
            )

        # Short near top (within 20% of range top)
        if position_in_range >= 0.8:
            return self._short_at_resistance(
                df, current_price, range_low, range_high, bb_middle, atr
            )

        return None

    def _long_at_support(
        self, df, price, range_low, range_high, bb_middle, atr
    ) -> Optional[TradeSignal]:
        """Long at range bottom with confirmation."""
        # Need bullish candle confirmation (close > open)
        if df['close'].iloc[-1] <= df['open'].iloc[-1]:
            return None

        stop_loss = range_low - (range_low * 0.005)  # 0.5% below range
        take_profit = bb_middle  # Target middle of range

        risk = price - stop_loss
        if risk <= 0:
            return None

        rr = (take_profit - price) / risk
        if rr < 1.5:
            return None  # Need at least 1.5:1 R:R

        logger.info(
            f"MEAN_REVERSION LONG | Near range bottom {range_low:.2f} | "
            f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
        )

        return TradeSignal(
            direction="long",
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy_name=self.name,
            regime="ranging",
            timeframe=self.config.regime.primary_timeframe,
            reasoning=f"Price at range bottom ({range_low:.0f}-{range_high:.0f}). Bullish candle confirmation.",
        )

    def _short_at_resistance(
        self, df, price, range_low, range_high, bb_middle, atr
    ) -> Optional[TradeSignal]:
        """Short at range top with confirmation."""
        if df['close'].iloc[-1] >= df['open'].iloc[-1]:
            return None

        stop_loss = range_high + (range_high * 0.005)
        take_profit = bb_middle

        risk = stop_loss - price
        if risk <= 0:
            return None

        rr = (price - take_profit) / risk
        if rr < 1.5:
            return None

        logger.info(
            f"MEAN_REVERSION SHORT | Near range top {range_high:.2f} | "
            f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
        )

        return TradeSignal(
            direction="short",
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy_name=self.name,
            regime="ranging",
            timeframe=self.config.regime.primary_timeframe,
            reasoning=f"Price at range top ({range_low:.0f}-{range_high:.0f}). Bearish candle confirmation.",
        )

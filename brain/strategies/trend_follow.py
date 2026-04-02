"""
Khufra Trading System - Trend Following Strategy
Deployed during TRENDING_UP and TRENDING_DOWN regimes.
Enter on pullbacks to EMA, trail stop, ride the trend.
"""

import logging
from typing import Optional
import pandas as pd
import numpy as np

from brain.strategies.base import BaseStrategy, TradeSignal

logger = logging.getLogger(__name__)


class TrendFollowStrategy(BaseStrategy):
    """
    Trend Following: enter on pullbacks to EMA in trending markets.
    - TRENDING_UP: Buy pullbacks to EMA 21/50, stop below swing low
    - TRENDING_DOWN: Short rallies to EMA 21/50, stop above swing high
    """

    name = "trend_follow"
    regime = "trending"

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: dict,
        current_price: float,
    ) -> Optional[TradeSignal]:
        if len(df) < 50:
            return None

        ema_fast = indicators['ema_fast'].iloc[-1]
        ema_slow = indicators['ema_slow'].iloc[-1]
        atr = indicators['atr'].iloc[-1]
        adx = indicators['adx'].iloc[-1]

        if np.isnan(ema_fast) or np.isnan(ema_slow) or np.isnan(atr):
            return None

        # Determine trend direction
        is_uptrend = current_price > ema_fast and current_price > ema_slow
        is_downtrend = current_price < ema_fast and current_price < ema_slow

        if is_uptrend:
            return self._long_pullback(df, current_price, ema_fast, ema_slow, atr, adx)
        elif is_downtrend:
            return self._short_rally(df, current_price, ema_fast, ema_slow, atr, adx)

        return None

    def _long_pullback(
        self, df, price, ema_fast, ema_slow, atr, adx
    ) -> Optional[TradeSignal]:
        """Look for long entry on pullback to EMA in uptrend."""
        # Price should be near EMA 21 (within 0.5 ATR) — pullback zone
        distance_to_ema = abs(price - ema_fast)
        if distance_to_ema > atr * 0.5:
            return None  # Not in pullback zone

        # Confirm: price just bounced (current close > previous close)
        if df['close'].iloc[-1] <= df['close'].iloc[-2]:
            return None  # Not bouncing yet

        # Find recent swing low for stop loss
        recent_lows = df['low'].iloc[-10:]
        swing_low = recent_lows.min()
        stop_loss = swing_low - (atr * 0.3)  # Small buffer

        # Take profit at 2x risk
        risk = price - stop_loss
        take_profit = price + (risk * 2.5)

        logger.info(
            f"TREND_FOLLOW LONG | Price near EMA21 ({ema_fast:.2f}) | "
            f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
        )

        return TradeSignal(
            direction="long",
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy_name=self.name,
            regime="trending_up",
            timeframe=self.config.regime.primary_timeframe,
            reasoning=f"Uptrend pullback to EMA21. ADX={adx:.1f}. Bounce confirmed.",
        )

    def _short_rally(
        self, df, price, ema_fast, ema_slow, atr, adx
    ) -> Optional[TradeSignal]:
        """Look for short entry on rally to EMA in downtrend."""
        distance_to_ema = abs(price - ema_fast)
        if distance_to_ema > atr * 0.5:
            return None

        if df['close'].iloc[-1] >= df['close'].iloc[-2]:
            return None  # Not rejecting yet

        recent_highs = df['high'].iloc[-10:]
        swing_high = recent_highs.max()
        stop_loss = swing_high + (atr * 0.3)

        risk = stop_loss - price
        take_profit = price - (risk * 2.5)

        logger.info(
            f"TREND_FOLLOW SHORT | Price near EMA21 ({ema_fast:.2f}) | "
            f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
        )

        return TradeSignal(
            direction="short",
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy_name=self.name,
            regime="trending_down",
            timeframe=self.config.regime.primary_timeframe,
            reasoning=f"Downtrend rally to EMA21. ADX={adx:.1f}. Rejection confirmed.",
        )

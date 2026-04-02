"""
Khufra Trading System - Cascade Reversal Strategy
Deployed during VOLATILE regime.
Play the reversal after liquidation cascade exhaustion.
"""

import logging
from typing import Optional
import pandas as pd
import numpy as np

from brain.strategies.base import BaseStrategy, TradeSignal

logger = logging.getLogger(__name__)


class CascadeReversalStrategy(BaseStrategy):
    """
    Volatile regime strategy: wait for cascade exhaustion then play reversal.
    - Reduced position size (handled by regime multiplier)
    - Look for exhaustion signs: declining volume, candle body shrinking
    - Enter reversal with tight stop at cascade extreme
    """

    name = "cascade_reversal"
    regime = "volatile"

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: dict,
        current_price: float,
    ) -> Optional[TradeSignal]:
        if len(df) < 10:
            return None

        atr = indicators['atr'].iloc[-1]
        vol_spike = indicators.get('volume_spike')

        if np.isnan(atr):
            return None

        # Check for exhaustion pattern
        return self._detect_exhaustion(df, current_price, atr, vol_spike)

    def _detect_exhaustion(
        self, df, price, atr, vol_spike
    ) -> Optional[TradeSignal]:
        """
        Detect cascade exhaustion:
        1. Big directional move (>2 ATR in last 5 candles)
        2. Volume declining from spike
        3. Candle bodies getting smaller (momentum fading)
        """
        last_5 = df.iloc[-5:]
        price_move = last_5['close'].iloc[-1] - last_5['close'].iloc[0]
        move_magnitude = abs(price_move)

        # Need significant move
        if move_magnitude < atr * 2:
            return None

        # Check volume declining
        volumes = last_5['volume'].values
        if len(volumes) < 3:
            return None

        vol_declining = volumes[-1] < volumes[-2] < volumes[-3]
        if not vol_declining:
            return None

        # Check candle bodies shrinking
        bodies = abs(last_5['close'] - last_5['open']).values
        bodies_shrinking = bodies[-1] < bodies[-2]
        if not bodies_shrinking:
            return None

        # Direction: reverse the cascade
        if price_move < 0:
            # Cascade was down → play long reversal
            stop_loss = last_5['low'].min() - (atr * 0.3)
            risk = price - stop_loss
            take_profit = price + (risk * 2)

            logger.info(
                f"CASCADE_REVERSAL LONG | Bearish cascade exhaustion | "
                f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
            )

            return TradeSignal(
                direction="long",
                entry_price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                strategy_name=self.name,
                regime="volatile",
                timeframe=self.config.regime.primary_timeframe,
                reasoning=f"Bearish cascade exhaustion. Move: {move_magnitude:.0f}. Volume declining.",
            )
        else:
            # Cascade was up → play short reversal
            stop_loss = last_5['high'].max() + (atr * 0.3)
            risk = stop_loss - price
            take_profit = price - (risk * 2)

            logger.info(
                f"CASCADE_REVERSAL SHORT | Bullish cascade exhaustion | "
                f"SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
            )

            return TradeSignal(
                direction="short",
                entry_price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                strategy_name=self.name,
                regime="volatile",
                timeframe=self.config.regime.primary_timeframe,
                reasoning=f"Bullish cascade exhaustion. Move: {move_magnitude:.0f}. Volume declining.",
            )

"""
Khufra Trading System - Regime Detection Engine
Classifies market into 5 regimes + transition state.
V2 Spec Section 3.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd
import numpy as np

from data.indicators import calculate_all_regime_indicators

logger = logging.getLogger(__name__)


class Regime:
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    VOLATILE = "volatile"
    DEAD = "dead"
    TRANSITION = "transition"


@dataclass
class RegimeState:
    """Current regime classification with supporting data."""
    regime: str
    confidence: float  # 0-1 how confident we are in this classification
    adx: float
    atr_ratio: float  # current ATR / avg ATR
    bb_percentile: float
    ema_fast: float
    ema_slow: float
    price: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    @property
    def factors(self) -> dict:
        return {
            'adx': self.adx,
            'atr_ratio': self.atr_ratio,
            'bb_percentile': self.bb_percentile,
            'ema_fast': self.ema_fast,
            'ema_slow': self.ema_slow,
            'price': self.price,
        }


class RegimeDetector:
    """
    Market regime classifier.
    Uses ADX, ATR, EMA 21/50, Bollinger Band width to classify market state.
    Requires N consecutive candle confirmations before changing regime.
    """

    def __init__(self, config):
        self.config = config
        self.current_regime: Optional[str] = None
        self.pending_regime: Optional[str] = None
        self.confirmation_count: int = 0
        self.last_state: Optional[RegimeState] = None

        # Config values
        self.adx_trend_thresh = config.regime.adx_trending_threshold
        self.adx_range_thresh = config.regime.adx_ranging_threshold
        self.atr_volatile_mult = config.regime.atr_volatile_multiplier
        self.atr_dead_mult = config.regime.atr_dead_multiplier
        self.bb_squeeze_pct = config.regime.bb_squeeze_percentile
        self.confirm_candles = config.regime.confirmation_candles

    def classify(self, df: pd.DataFrame) -> RegimeState:
        """
        Classify current market regime from OHLCV data.

        Args:
            df: DataFrame with columns [open, high, low, close, volume].
                Must have enough history for indicator calculation (~100 rows).

        Returns:
            RegimeState with classification and supporting data.
        """
        if len(df) < 50:
            logger.warning(f"Insufficient data for regime detection: {len(df)} candles")
            return RegimeState(
                regime=Regime.TRANSITION, confidence=0.0,
                adx=0, atr_ratio=1.0, bb_percentile=50,
                ema_fast=0, ema_slow=0, price=df['close'].iloc[-1] if len(df) > 0 else 0
            )

        indicators = calculate_all_regime_indicators(df, self.config)

        # Get latest values
        adx_val = indicators['adx'].iloc[-1]
        atr_val = indicators['atr'].iloc[-1]
        atr_avg_val = indicators['atr_avg'].iloc[-1]
        atr_ratio = atr_val / atr_avg_val if atr_avg_val > 0 else 1.0
        ema_fast_val = indicators['ema_fast'].iloc[-1]
        ema_slow_val = indicators['ema_slow'].iloc[-1]
        bb_pct = indicators['bb_width_percentile'].iloc[-1]
        current_price = df['close'].iloc[-1]

        # Handle NaN values
        if np.isnan(adx_val):
            adx_val = 0
        if np.isnan(bb_pct):
            bb_pct = 50
        if np.isnan(atr_ratio):
            atr_ratio = 1.0

        # Classification logic (V2 Section 3.3)
        raw_regime = self._classify_raw(
            adx_val, atr_ratio, bb_pct, current_price, ema_fast_val, ema_slow_val
        )

        # Apply confirmation logic
        confirmed_regime = self._apply_confirmation(raw_regime)

        confidence = self._calculate_confidence(
            confirmed_regime, adx_val, atr_ratio, bb_pct
        )

        state = RegimeState(
            regime=confirmed_regime,
            confidence=confidence,
            adx=adx_val,
            atr_ratio=atr_ratio,
            bb_percentile=bb_pct,
            ema_fast=ema_fast_val,
            ema_slow=ema_slow_val,
            price=current_price,
        )

        # Log regime change
        if self.last_state and self.last_state.regime != confirmed_regime:
            logger.info(
                f"REGIME CHANGE: {self.last_state.regime} -> {confirmed_regime} | "
                f"ADX={adx_val:.1f} ATR_ratio={atr_ratio:.2f} BB%={bb_pct:.0f}"
            )

        self.last_state = state
        return state

    def _classify_raw(
        self, adx: float, atr_ratio: float, bb_pct: float,
        price: float, ema_fast: float, ema_slow: float
    ) -> str:
        """Raw regime classification without confirmation."""

        # Step 1: Check for DEAD market
        if atr_ratio < self.atr_dead_mult and bb_pct < self.bb_squeeze_pct:
            return Regime.DEAD

        # Step 2: Check for VOLATILE
        if atr_ratio > self.atr_volatile_mult:
            return Regime.VOLATILE

        # Step 3: Check for TRENDING
        if adx > self.adx_trend_thresh:
            if price > ema_fast and price > ema_slow:
                return Regime.TRENDING_UP
            elif price < ema_fast and price < ema_slow:
                return Regime.TRENDING_DOWN

        # Step 4: RANGING
        if adx < self.adx_range_thresh:
            return Regime.RANGING

        # Step 5: Ambiguous (ADX between ranging and trending thresholds)
        return Regime.TRANSITION

    def _apply_confirmation(self, raw_regime: str) -> str:
        """
        Require N consecutive candles confirming the new regime
        before actually changing. Prevents flip-flopping.
        """
        if self.current_regime is None:
            # First classification
            self.current_regime = raw_regime
            self.pending_regime = None
            self.confirmation_count = 0
            return raw_regime

        if raw_regime == self.current_regime:
            # Same regime, reset any pending change
            self.pending_regime = None
            self.confirmation_count = 0
            return self.current_regime

        if raw_regime == self.pending_regime:
            # Consecutive confirmation of new regime
            self.confirmation_count += 1
            if self.confirmation_count >= self.confirm_candles:
                self.current_regime = raw_regime
                self.pending_regime = None
                self.confirmation_count = 0
                return raw_regime
            else:
                # Not confirmed yet, stay in transition
                return Regime.TRANSITION
        else:
            # Different pending regime, start new count
            self.pending_regime = raw_regime
            self.confirmation_count = 1
            if self.confirmation_count >= self.confirm_candles:
                self.current_regime = raw_regime
                self.pending_regime = None
                self.confirmation_count = 0
                return raw_regime
            return Regime.TRANSITION

    def _calculate_confidence(
        self, regime: str, adx: float, atr_ratio: float, bb_pct: float
    ) -> float:
        """Calculate confidence in the regime classification (0-1)."""
        if regime == Regime.TRANSITION:
            return 0.3

        if regime in (Regime.TRENDING_UP, Regime.TRENDING_DOWN):
            # Higher ADX = more confident in trend
            return min(1.0, adx / 50)

        if regime == Regime.RANGING:
            # Lower ADX = more confident in range
            return min(1.0, (self.adx_range_thresh - adx + 10) / 20)

        if regime == Regime.VOLATILE:
            # Higher ATR ratio = more confident
            return min(1.0, atr_ratio / 3.0)

        if regime == Regime.DEAD:
            # Lower ATR ratio + lower BB percentile = more confident
            return min(1.0, (1 - atr_ratio) * (1 - bb_pct / 100))

        return 0.5

    def reset(self):
        """Reset detector state."""
        self.current_regime = None
        self.pending_regime = None
        self.confirmation_count = 0
        self.last_state = None

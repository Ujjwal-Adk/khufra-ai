"""
Khufra Trading System - Market Memory
Tracks and scores key price levels.
V2 Spec Section 6.
"""

import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PriceLevel:
    """A remembered price level with significance."""
    price: float
    level_type: str        # 'support', 'resistance', 'liquidation_cluster'
    touch_count: int = 1
    avg_volume: float = 0.0
    last_regime: str = ""
    last_touched: datetime = None
    created: datetime = None
    significance: float = 1.0

    def __post_init__(self):
        now = datetime.utcnow()
        if self.last_touched is None:
            self.last_touched = now
        if self.created is None:
            self.created = now


class MarketMemory:
    """
    Remembers price reactions at key levels.
    Rolling window with significance decay.
    """

    def __init__(self, config):
        self.config = config
        self.mm = config.market_memory
        self.levels: list[PriceLevel] = []

    def update_from_candles(
        self,
        df: pd.DataFrame,
        regime: str,
        symbol: str = "BTCUSDT"
    ):
        """
        Scan recent candles for significant price reactions and update memory.
        Called periodically (e.g., every hour).
        """
        if len(df) < 20:
            return

        # Detect bounce/rejection levels
        self._detect_bounces(df, regime)

        # Decay old levels
        self._apply_decay()

        # Purge stale levels
        self._purge_old_levels()

    def _detect_bounces(self, df: pd.DataFrame, regime: str):
        """Find price levels where significant reactions occurred."""
        lookback = 5
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        avg_vol = np.mean(volume[-20:]) if len(volume) >= 20 else np.mean(volume)

        for i in range(lookback, len(df) - lookback):
            # Swing low → support
            if low[i] == min(low[i - lookback:i + lookback + 1]):
                vol_ratio = volume[i] / avg_vol if avg_vol > 0 else 1
                if vol_ratio > 1.2:  # Meaningful volume
                    self._add_or_update_level(
                        price=low[i],
                        level_type='support',
                        volume=volume[i],
                        regime=regime,
                    )

            # Swing high → resistance
            if high[i] == max(high[i - lookback:i + lookback + 1]):
                vol_ratio = volume[i] / avg_vol if avg_vol > 0 else 1
                if vol_ratio > 1.2:
                    self._add_or_update_level(
                        price=high[i],
                        level_type='resistance',
                        volume=volume[i],
                        regime=regime,
                    )

    def _add_or_update_level(
        self,
        price: float,
        level_type: str,
        volume: float,
        regime: str,
        tolerance_pct: float = 0.002,
    ):
        """Add new level or update existing one if within tolerance."""
        for level in self.levels:
            if level.level_type == level_type:
                diff = abs(level.price - price) / level.price if level.price > 0 else float('inf')
                if diff < tolerance_pct:
                    # Update existing level
                    level.touch_count += 1
                    level.avg_volume = (level.avg_volume * (level.touch_count - 1) + volume) / level.touch_count
                    level.last_regime = regime
                    level.last_touched = datetime.utcnow()
                    level.significance = min(2.0, level.significance + 0.2)
                    return

        # New level
        self.levels.append(PriceLevel(
            price=price,
            level_type=level_type,
            touch_count=1,
            avg_volume=volume,
            last_regime=regime,
        ))

    def _apply_decay(self):
        """Reduce significance of levels based on age."""
        now = datetime.utcnow()
        halflife = timedelta(days=self.mm.decay_halflife_days)

        for level in self.levels:
            age = now - level.last_touched
            decay_factor = 0.5 ** (age / halflife)
            level.significance *= decay_factor

    def _purge_old_levels(self):
        """Remove levels older than purge threshold."""
        now = datetime.utcnow()
        cutoff = now - timedelta(days=self.mm.purge_after_days)
        min_sig = self.mm.min_significance

        self.levels = [
            l for l in self.levels
            if l.last_touched > cutoff or l.significance >= min_sig
        ]

    def get_support_levels(self, current_price: float, n: int = 5) -> list[float]:
        """Get N most significant support levels below current price."""
        supports = [
            l for l in self.levels
            if l.level_type == 'support' and l.price < current_price
        ]
        supports.sort(key=lambda l: l.significance, reverse=True)
        return [l.price for l in supports[:n]]

    def get_resistance_levels(self, current_price: float, n: int = 5) -> list[float]:
        """Get N most significant resistance levels above current price."""
        resistances = [
            l for l in self.levels
            if l.level_type == 'resistance' and l.price > current_price
        ]
        resistances.sort(key=lambda l: l.significance, reverse=True)
        return [l.price for l in resistances[:n]]

    def get_nearest_support(self, current_price: float) -> Optional[float]:
        """Get the nearest significant support level."""
        supports = self.get_support_levels(current_price, n=1)
        return supports[0] if supports else None

    def get_nearest_resistance(self, current_price: float) -> Optional[float]:
        """Get the nearest significant resistance level."""
        resistances = self.get_resistance_levels(current_price, n=1)
        return resistances[0] if resistances else None

    def get_all_levels(self) -> list[dict]:
        """Get all levels for display/logging."""
        return [
            {
                'price': l.price,
                'type': l.level_type,
                'touches': l.touch_count,
                'significance': round(l.significance, 3),
                'last_touched': l.last_touched.isoformat() if l.last_touched else None,
            }
            for l in sorted(self.levels, key=lambda x: x.significance, reverse=True)
        ]

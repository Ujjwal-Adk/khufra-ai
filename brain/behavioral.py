"""
Khufra Trading System - Behavioral Pattern Detection
Detects exploitable retail trader behaviors.
V2 Spec Section 4.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pandas as pd
import numpy as np

from data.indicators import calculate_volume_spike

logger = logging.getLogger(__name__)


@dataclass
class BehavioralSignal:
    """A detected behavioral pattern signal."""
    pattern: str           # stop_hunt, liquidation_cascade, fomo_trap, funding_extreme
    direction: str         # 'long' or 'short' — the suggested trade direction
    strength: float        # 0-1 how strong the pattern is
    details: dict = field(default_factory=dict)
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class BehavioralDetector:
    """
    Detects predictable retail trader behaviors:
    - Stop hunts / liquidity grabs
    - Liquidation cascades
    - FOMO breakout traps
    - Funding rate extremes
    """

    def __init__(self, config):
        self.config = config
        self.sh = config.behavioral.stop_hunt
        self.lc = config.behavioral.liquidation_cascade
        self.ft = config.behavioral.fomo_trap
        self.fe = config.behavioral.funding_extreme

    def detect_all(
        self,
        df: pd.DataFrame,
        support_levels: list = None,
        resistance_levels: list = None,
        funding_rate: float = None,
        open_interest: pd.Series = None,
        liquidation_volume: float = None,
    ) -> list[BehavioralSignal]:
        """
        Run all behavioral pattern detectors.
        Returns list of detected signals (can be empty).
        """
        signals = []

        sh = self.detect_stop_hunt(df, support_levels, resistance_levels)
        if sh:
            signals.append(sh)

        lc = self.detect_liquidation_cascade(df, open_interest, liquidation_volume)
        if lc:
            signals.append(lc)

        ft = self.detect_fomo_trap(df, resistance_levels, open_interest)
        if ft:
            signals.append(ft)

        fe = self.detect_funding_extreme(funding_rate)
        if fe:
            signals.append(fe)

        return signals

    def detect_stop_hunt(
        self,
        df: pd.DataFrame,
        support_levels: list = None,
        resistance_levels: list = None,
    ) -> Optional[BehavioralSignal]:
        """
        Detect stop hunt / liquidity grab.
        Price breaks key level on high volume, then reverses back inside.
        """
        if len(df) < 5 or not support_levels and not resistance_levels:
            return None

        vol_spike = calculate_volume_spike(df['volume'], period=20)
        current_price = df['close'].iloc[-1]
        min_vol_spike = self.sh.min_volume_spike
        min_break = self.sh.min_break_pct
        max_candles = self.sh.max_reclaim_candles

        # Check recent candles for stop hunt pattern
        check_range = min(max_candles + 1, len(df))

        # Check support levels (bearish stop hunt → bullish signal)
        if support_levels:
            for level in support_levels:
                for i in range(1, check_range):
                    idx = -i - 1
                    if abs(idx) > len(df):
                        continue

                    candle_low = df['low'].iloc[idx]
                    candle_close = df['close'].iloc[idx]
                    break_pct = (level - candle_low) / level if level > 0 else 0

                    # Check: wick broke below support, but closed back above
                    if (break_pct >= min_break and
                            candle_close > level and
                            vol_spike.iloc[idx] >= min_vol_spike):
                        # Confirm: current price is back above level
                        if current_price > level:
                            strength = min(1.0, vol_spike.iloc[idx] / (min_vol_spike * 2))
                            logger.info(
                                f"STOP HUNT detected at support {level:.2f} | "
                                f"Break: {break_pct:.3f} | Vol spike: {vol_spike.iloc[idx]:.1f}x"
                            )
                            return BehavioralSignal(
                                pattern="stop_hunt",
                                direction="long",
                                strength=strength,
                                details={
                                    'level': level,
                                    'level_type': 'support',
                                    'break_pct': break_pct,
                                    'volume_spike': float(vol_spike.iloc[idx]),
                                    'wick_low': float(candle_low),
                                }
                            )

        # Check resistance levels (bullish stop hunt → bearish signal)
        if resistance_levels:
            for level in resistance_levels:
                for i in range(1, check_range):
                    idx = -i - 1
                    if abs(idx) > len(df):
                        continue

                    candle_high = df['high'].iloc[idx]
                    candle_close = df['close'].iloc[idx]
                    break_pct = (candle_high - level) / level if level > 0 else 0

                    if (break_pct >= min_break and
                            candle_close < level and
                            vol_spike.iloc[idx] >= min_vol_spike):
                        if current_price < level:
                            strength = min(1.0, vol_spike.iloc[idx] / (min_vol_spike * 2))
                            logger.info(
                                f"STOP HUNT detected at resistance {level:.2f} | "
                                f"Break: {break_pct:.3f} | Vol spike: {vol_spike.iloc[idx]:.1f}x"
                            )
                            return BehavioralSignal(
                                pattern="stop_hunt",
                                direction="short",
                                strength=strength,
                                details={
                                    'level': level,
                                    'level_type': 'resistance',
                                    'break_pct': break_pct,
                                    'volume_spike': float(vol_spike.iloc[idx]),
                                    'wick_high': float(candle_high),
                                }
                            )

        return None

    def detect_liquidation_cascade(
        self,
        df: pd.DataFrame,
        open_interest: pd.Series = None,
        liquidation_volume: float = None,
    ) -> Optional[BehavioralSignal]:
        """
        Detect liquidation cascade.
        Rapid OI drop + high liquidation volume + accelerating price.
        """
        if open_interest is None or len(open_interest) < 5:
            return None

        # OI drop percentage
        oi_start = open_interest.iloc[-5]
        oi_now = open_interest.iloc[-1]
        if oi_start <= 0:
            return None

        oi_drop = (oi_start - oi_now) / oi_start

        if oi_drop < self.lc.min_oi_drop_pct:
            return None

        # Check liquidation volume threshold
        if liquidation_volume is not None and liquidation_volume < self.lc.min_liquidation_volume:
            return None

        # Determine cascade direction from price movement
        price_change = df['close'].iloc[-1] - df['close'].iloc[-5]
        direction = "long" if price_change < 0 else "short"  # Trade reversal

        strength = min(1.0, oi_drop / (self.lc.min_oi_drop_pct * 3))

        logger.info(
            f"LIQUIDATION CASCADE detected | OI drop: {oi_drop:.3f} | "
            f"Price change: {price_change:.2f} | Direction: {direction}"
        )

        return BehavioralSignal(
            pattern="liquidation_cascade",
            direction=direction,
            strength=strength,
            details={
                'oi_drop_pct': float(oi_drop),
                'liquidation_volume': liquidation_volume,
                'price_change': float(price_change),
            }
        )

    def detect_fomo_trap(
        self,
        df: pd.DataFrame,
        resistance_levels: list = None,
        open_interest: pd.Series = None,
    ) -> Optional[BehavioralSignal]:
        """
        Detect FOMO breakout trap.
        Breakout on high volume but no follow-through, volume declines.
        """
        if len(df) < self.ft.no_followthrough_candles + 2:
            return None

        vol_spike = calculate_volume_spike(df['volume'], period=20)
        n = self.ft.no_followthrough_candles

        # Look for a breakout candle followed by failure
        breakout_idx = -(n + 1)
        if abs(breakout_idx) > len(df):
            return None

        breakout_close = df['close'].iloc[breakout_idx]
        breakout_vol_spike = vol_spike.iloc[breakout_idx]
        current_price = df['close'].iloc[-1]

        if resistance_levels:
            for level in resistance_levels:
                # Breakout: close above resistance on high volume
                if breakout_close > level and breakout_vol_spike >= self.sh.min_volume_spike:
                    # Failure: current price back below level
                    if current_price < level:
                        # Volume decline check
                        recent_vol = df['volume'].iloc[-n:].mean()
                        breakout_vol = df['volume'].iloc[breakout_idx]
                        vol_decline = 1 - (recent_vol / breakout_vol) if breakout_vol > 0 else 0

                        if vol_decline >= self.ft.volume_decline_pct:
                            strength = min(1.0, vol_decline / 0.8)
                            logger.info(
                                f"FOMO TRAP detected at {level:.2f} | "
                                f"Vol decline: {vol_decline:.1%}"
                            )
                            return BehavioralSignal(
                                pattern="fomo_trap",
                                direction="short",
                                strength=strength,
                                details={
                                    'breakout_level': level,
                                    'breakout_price': float(breakout_close),
                                    'current_price': float(current_price),
                                    'volume_decline': float(vol_decline),
                                }
                            )

        return None

    def detect_funding_extreme(
        self, funding_rate: float = None
    ) -> Optional[BehavioralSignal]:
        """
        Detect extreme funding rate.
        High positive = overcrowded longs (bearish).
        High negative = overcrowded shorts (bullish).
        """
        if funding_rate is None:
            return None

        if funding_rate > self.fe.bullish_crowd_threshold:
            # Overcrowded longs → bearish signal
            strength = min(1.0, abs(funding_rate) / (self.fe.bullish_crowd_threshold * 3))
            logger.info(f"FUNDING EXTREME: overcrowded longs | Rate: {funding_rate:.4%}")
            return BehavioralSignal(
                pattern="funding_extreme",
                direction="short",
                strength=strength,
                details={'funding_rate': funding_rate, 'crowd': 'bullish'}
            )

        if funding_rate < self.fe.bearish_crowd_threshold:
            # Overcrowded shorts → bullish signal
            strength = min(1.0, abs(funding_rate) / abs(self.fe.bearish_crowd_threshold * 3))
            logger.info(f"FUNDING EXTREME: overcrowded shorts | Rate: {funding_rate:.4%}")
            return BehavioralSignal(
                pattern="funding_extreme",
                direction="long",
                strength=strength,
                details={'funding_rate': funding_rate, 'crowd': 'bearish'}
            )

        return None

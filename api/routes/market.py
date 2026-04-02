"""
Khufra Trading System - Market Data Routes
Behavioral signals, market memory, indicators, and kill zones.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from api.dependencies import get_engine
from api.schemas import (
    BehavioralSignalResponse,
    MarketMemoryResponse,
    IndicatorsResponse,
    KillZoneResponse,
)
from core.engine import KhufraEngine

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/behavioral", response_model=list[BehavioralSignalResponse])
async def get_behavioral_signals(eng: KhufraEngine = Depends(get_engine)):
    """Get the most recently detected behavioral patterns."""
    if not eng.last_behavioral_signals:
        return []

    results = []
    for bs in eng.last_behavioral_signals:
        results.append(BehavioralSignalResponse(
            pattern=bs.pattern,
            direction=bs.direction,
            strength=bs.strength,
            details=bs.details if bs.details else {},
            timestamp=bs.timestamp.isoformat() if bs.timestamp else datetime.now(timezone.utc).isoformat(),
        ))

    return results


@router.get("/memory", response_model=list[MarketMemoryResponse])
async def get_market_memory(eng: KhufraEngine = Depends(get_engine)):
    """Get remembered price levels from market memory."""
    if not eng.market_memory or not eng.market_memory.levels:
        return []

    results = []
    for level in eng.market_memory.levels:
        results.append(MarketMemoryResponse(
            price_level=level.price,
            level_type=level.level_type,
            touch_count=level.touch_count,
            significance_score=level.significance,
        ))

    return results


@router.get("/indicators", response_model=IndicatorsResponse)
async def get_indicators(eng: KhufraEngine = Depends(get_engine)):
    """Get the latest calculated technical indicators."""
    if eng.last_indicators is None:
        return IndicatorsResponse(
            adx=None, rsi=None, atr=None,
            ema_fast=None, ema_slow=None,
            bb_width=None, volume_spike=None,
        )

    indicators = eng.last_indicators

    def _safe_last(series_or_val, key: str):
        """Safely extract the last value from a pandas Series or scalar."""
        try:
            val = indicators.get(key) if isinstance(indicators, dict) else getattr(indicators, key, None)
            if val is None:
                return None
            if hasattr(val, "iloc"):
                v = float(val.iloc[-1])
            else:
                v = float(val)
            # Check for NaN
            if v != v:
                return None
            return v
        except (IndexError, TypeError, ValueError, KeyError):
            return None

    return IndicatorsResponse(
        adx=_safe_last(indicators, "adx"),
        rsi=_safe_last(indicators, "rsi"),
        atr=_safe_last(indicators, "atr"),
        ema_fast=_safe_last(indicators, "ema_fast"),
        ema_slow=_safe_last(indicators, "ema_slow"),
        bb_width=_safe_last(indicators, "bb_width"),
        volume_spike=_safe_last(indicators, "volume_spike"),
    )


@router.get("/kill-zones", response_model=list[KillZoneResponse])
async def get_kill_zones(eng: KhufraEngine = Depends(get_engine)):
    """Get all configured kill zones and their current active status."""
    now = datetime.now(timezone.utc)
    current_time = now.strftime("%H:%M")

    zones = []

    # Active kill zones
    for zone in eng.config.kill_zones.active:
        is_active = zone.start <= current_time < zone.end
        zones.append(KillZoneResponse(
            name=zone.name,
            start=zone.start,
            end=zone.end,
            is_active=is_active,
        ))

    # Watch-only kill zones
    for zone in eng.config.kill_zones.watch_only:
        is_active = zone.start <= current_time < zone.end
        zones.append(KillZoneResponse(
            name=f"{zone.name} (watch)",
            start=zone.start,
            end=zone.end,
            is_active=is_active,
        ))

    return zones

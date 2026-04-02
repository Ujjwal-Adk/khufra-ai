"""
Khufra Trading System - Regime Routes
Market regime detection endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_engine
from api.schemas import RegimeStateResponse
from core.engine import KhufraEngine

router = APIRouter(prefix="/regime", tags=["regime"])


@router.get("/current", response_model=RegimeStateResponse)
async def get_current_regime(eng: KhufraEngine = Depends(get_engine)):
    """Get the current market regime classification."""
    # If the engine has run a cycle, use cached regime state
    if eng._last_regime is not None:
        # Try to get full regime state from detector
        try:
            df = eng.candles.get_candles("1h")
            if df is not None and len(df) >= 50:
                state = eng.regime_detector.classify(df)
                return RegimeStateResponse(
                    regime=str(state.regime),
                    confidence=state.confidence,
                    adx=state.adx,
                    atr_ratio=state.atr_ratio,
                    bb_percentile=state.bb_percentile,
                    ema_fast=state.ema_fast,
                    ema_slow=state.ema_slow,
                    price=state.price,
                    timestamp=state.timestamp.isoformat() if state.timestamp else datetime.now(timezone.utc).isoformat(),
                )
        except Exception:
            pass

        # Fallback: return minimal data from cached regime
        return RegimeStateResponse(
            regime=str(eng._last_regime),
            confidence=0.0,
            adx=0.0,
            atr_ratio=0.0,
            bb_percentile=0.0,
            ema_fast=0.0,
            ema_slow=0.0,
            price=eng._ticker_price or 0.0,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # No data yet — return defaults
    return RegimeStateResponse(
        regime="unknown",
        confidence=0.0,
        adx=0.0,
        atr_ratio=0.0,
        bb_percentile=0.0,
        ema_fast=0.0,
        ema_slow=0.0,
        price=eng._ticker_price or 0.0,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/history", response_model=list[RegimeStateResponse])
async def get_regime_history(
    limit: int = Query(default=50, ge=1, le=500),
    eng: KhufraEngine = Depends(get_engine),
):
    """Get regime classification history from the database."""
    try:
        if eng.db and eng.db.SessionLocal:
            from database.models import RegimeHistory
            with eng.db.get_session() as session:
                entries = (
                    session.query(RegimeHistory)
                    .order_by(RegimeHistory.timestamp.desc())
                    .limit(limit)
                    .all()
                )
                return [
                    RegimeStateResponse(
                        regime=entry.regime.value if entry.regime else "unknown",
                        confidence=0.0,
                        adx=entry.adx_value or 0.0,
                        atr_ratio=(entry.atr_value / entry.atr_avg) if entry.atr_value and entry.atr_avg else 0.0,
                        bb_percentile=entry.bb_width_percentile or 0.0,
                        ema_fast=entry.ema_fast_value or 0.0,
                        ema_slow=entry.ema_slow_value or 0.0,
                        price=entry.price or 0.0,
                        timestamp=entry.timestamp.isoformat() if entry.timestamp else "",
                    )
                    for entry in entries
                ]
    except Exception:
        pass

    return []

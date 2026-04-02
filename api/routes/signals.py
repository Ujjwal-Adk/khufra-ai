"""
Khufra Trading System - Signal Routes
Trading signal endpoints.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_engine
from api.schemas import SignalResponse, ConfidenceBreakdownResponse
from core.engine import KhufraEngine

router = APIRouter(prefix="/signals", tags=["signals"])


def _build_signal_response(signal, confidence_result, regime, behavioral_pattern: str = "") -> SignalResponse:
    """Helper to build a SignalResponse from engine objects."""
    breakdown = ConfidenceBreakdownResponse(
        regime=0, behavioral=0, whale=0,
        order_book=0, funding_rate=0, volume=0,
    )
    confidence_score = 0

    if confidence_result is not None:
        bd = confidence_result.breakdown or {}
        breakdown = ConfidenceBreakdownResponse(
            regime=bd.get("regime_alignment", bd.get("regime", 0)),
            behavioral=bd.get("behavioral_pattern", bd.get("behavioral", 0)),
            whale=bd.get("whale_onchain", bd.get("whale", 0)),
            order_book=bd.get("order_book", 0),
            funding_rate=bd.get("funding_rate", 0),
            volume=bd.get("volume", 0),
        )
        confidence_score = confidence_result.total_score

    return SignalResponse(
        direction=signal.direction,
        entry_price=signal.entry_price,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profit,
        strategy_name=signal.strategy_name,
        confidence_score=confidence_score,
        confidence_breakdown=breakdown,
        regime=str(regime) if regime else "unknown",
        behavioral_pattern=behavioral_pattern,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/current", response_model=Optional[SignalResponse])
async def get_current_signal(eng: KhufraEngine = Depends(get_engine)):
    """Get the most recent trading signal, if any."""
    if eng.last_signal is None:
        return None

    behavioral_pattern = ""
    if eng.last_behavioral_signals:
        # Find the strongest matching behavioral signal
        for bs in eng.last_behavioral_signals:
            if bs.direction == eng.last_signal.direction:
                behavioral_pattern = bs.pattern
                break

    return _build_signal_response(
        signal=eng.last_signal,
        confidence_result=eng.last_confidence_result,
        regime=eng._last_regime,
        behavioral_pattern=behavioral_pattern,
    )


@router.get("/history", response_model=list[SignalResponse])
async def get_signal_history(
    limit: int = Query(default=50, ge=1, le=500),
    eng: KhufraEngine = Depends(get_engine),
):
    """
    Get historical signals from the trade journal.
    Each journal entry represents a signal that was acted upon.
    """
    try:
        if eng.journal:
            entries = eng.journal.get_recent_trades(limit=limit)
            results = []
            for entry in entries:
                bd = entry.score_breakdown or {}
                breakdown = ConfidenceBreakdownResponse(
                    regime=bd.get("regime_alignment", bd.get("regime", 0)),
                    behavioral=bd.get("behavioral_pattern", bd.get("behavioral", 0)),
                    whale=bd.get("whale_onchain", bd.get("whale", 0)),
                    order_book=bd.get("order_book", 0),
                    funding_rate=bd.get("funding_rate", 0),
                    volume=bd.get("volume", 0),
                )
                results.append(SignalResponse(
                    direction=entry.direction.value if entry.direction else "unknown",
                    entry_price=entry.entry_price or 0.0,
                    stop_loss=entry.stop_loss_price or 0.0,
                    take_profit=entry.take_profit_price or 0.0,
                    strategy_name=entry.strategy or "unknown",
                    confidence_score=entry.confidence_score or 0,
                    confidence_breakdown=breakdown,
                    regime=entry.regime.value if entry.regime else "unknown",
                    behavioral_pattern=entry.behavioral_pattern or "",
                    timestamp=entry.entry_time.isoformat() if entry.entry_time else "",
                ))
            return results
    except Exception:
        pass

    return []

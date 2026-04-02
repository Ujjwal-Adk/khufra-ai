"""
Khufra Trading System - Trade Routes
Trade journal and statistics endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_engine
from api.schemas import TradeJournalResponse, PortfolioSummaryResponse
from core.engine import KhufraEngine

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/journal")
async def get_trade_journal(
    limit: int = Query(default=50, ge=1, le=500),
    direction: Optional[str] = Query(default=None, description="Filter by direction: long or short"),
    regime: Optional[str] = Query(default=None, description="Filter by regime"),
    eng: KhufraEngine = Depends(get_engine),
):
    """Get trade journal entries with optional filters."""
    try:
        if eng.db and eng.db.SessionLocal:
            from database.models import TradeJournal as TradeJournalModel

            with eng.db.get_session() as session:
                query = session.query(TradeJournalModel)

                if direction is not None:
                    query = query.filter(TradeJournalModel.direction == direction)
                if regime is not None:
                    query = query.filter(TradeJournalModel.regime == regime)

                query = query.order_by(TradeJournalModel.entry_time.desc())
                total = query.count()
                entries = query.limit(limit).all()

                trades = []
                for entry in entries:
                    trades.append(TradeJournalResponse(
                        id=entry.id,
                        symbol=entry.symbol or "",
                        direction=entry.direction.value if entry.direction else "unknown",
                        entry_price=entry.entry_price or 0.0,
                        exit_price=entry.exit_price,
                        entry_time=entry.entry_time.isoformat() if entry.entry_time else "",
                        exit_time=entry.exit_time.isoformat() if entry.exit_time else None,
                        position_size=entry.position_size or 0.0,
                        leverage=entry.leverage or 1,
                        pnl_usd=entry.pnl_usd,
                        pnl_pct=entry.pnl_pct,
                        regime=entry.regime.value if entry.regime else "unknown",
                        strategy=entry.strategy or "unknown",
                        confidence_score=entry.confidence_score or 0,
                        behavioral_pattern=entry.behavioral_pattern or "",
                        exit_reason=entry.exit_reason.value if entry.exit_reason else None,
                        is_paper=entry.is_paper if entry.is_paper is not None else True,
                    ))

                return {"trades": trades, "total": total}
    except Exception:
        pass

    return {"trades": [], "total": 0}


@router.get("/stats", response_model=PortfolioSummaryResponse)
async def get_trade_stats(eng: KhufraEngine = Depends(get_engine)):
    """Get portfolio statistics from the paper trader."""
    stats = eng.paper_trader.get_stats()

    return PortfolioSummaryResponse(
        equity=stats.get("equity", eng.paper_trader.equity),
        starting_equity=eng.paper_trader.starting_equity,
        return_pct=stats.get("return_pct", 0.0),
        daily_pnl=eng.risk_manager.daily_pnl,
        total_trades=stats.get("total_trades", 0),
        winning_trades=stats.get("winning_trades", 0),
        losing_trades=stats.get("losing_trades", 0),
        win_rate=stats.get("win_rate", 0.0),
        open_positions=stats.get("open_positions", 0),
    )

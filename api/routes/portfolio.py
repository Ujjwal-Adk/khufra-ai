"""
Khufra Trading System - Portfolio Routes
Portfolio summary and equity curve endpoints.
"""

from fastapi import APIRouter, Depends

from api.dependencies import get_engine
from api.schemas import PortfolioSummaryResponse
from core.engine import KhufraEngine

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(eng: KhufraEngine = Depends(get_engine)):
    """Get current portfolio summary."""
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


@router.get("/equity-curve")
async def get_equity_curve(eng: KhufraEngine = Depends(get_engine)):
    """
    Get equity curve data points.
    Reconstructed from closed trades in chronological order.
    """
    try:
        if eng.paper_trader.closed_trades:
            curve = []
            running_equity = eng.paper_trader.starting_equity

            for trade in eng.paper_trader.closed_trades:
                running_equity += trade.get("net_pnl", trade.get("pnl_usd", 0.0))
                exit_time = trade.get("exit_time")
                timestamp = exit_time.isoformat() if exit_time else ""
                curve.append({
                    "timestamp": timestamp,
                    "equity": round(running_equity, 2),
                })

            return curve
    except Exception:
        pass

    # No trades yet — return single starting point
    return [{"timestamp": "", "equity": eng.paper_trader.starting_equity}]

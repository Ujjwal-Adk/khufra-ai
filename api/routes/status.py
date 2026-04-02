"""
Khufra Trading System - Status Routes
Health check and bot status endpoints.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from api.dependencies import get_engine, engine as global_engine
from api.schemas import BotStatusResponse
from core.engine import KhufraEngine

router = APIRouter(tags=["status"])

# Track API server start time
_server_start_time = time.time()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "engine_initialized": global_engine is not None,
        "uptime": time.time() - _server_start_time,
    }


@router.get("/status", response_model=BotStatusResponse)
async def get_status(eng: KhufraEngine = Depends(get_engine)):
    """Get full bot status including risk manager state."""
    risk_status = eng.risk_manager.get_status()

    uptime = 0.0
    if eng._start_time is not None:
        uptime = (datetime.now(timezone.utc) - eng._start_time).total_seconds()

    current_regime = None
    if eng._last_regime is not None:
        current_regime = str(eng._last_regime)

    return BotStatusResponse(
        running=eng.running,
        mode=eng.config.system.mode,
        uptime_seconds=uptime,
        current_regime=current_regime,
        open_positions=risk_status.get("open_positions", 0),
        equity=eng.paper_trader.equity,
        daily_pnl=risk_status.get("daily_pnl", 0.0),
        daily_drawdown=risk_status.get("daily_drawdown", 0.0),
        consecutive_losses=risk_status.get("consecutive_losses", 0),
        trading_halted=risk_status.get("trading_halted", False),
        halt_reason=risk_status.get("halt_reason", ""),
    )

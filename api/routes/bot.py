"""
Khufra Trading System - Bot Control Routes
Start, stop, kill switch, and mode management.
"""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.dependencies import get_engine
from core.engine import KhufraEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bot", tags=["bot"])


class ModeChangeRequest(BaseModel):
    mode: str  # "paper" or "live"


@router.post("/start")
async def start_bot(eng: KhufraEngine = Depends(get_engine)):
    """Start the trading engine as a background asyncio task."""
    if eng.running:
        raise HTTPException(status_code=409, detail="Bot is already running")

    # Run engine.start() as a background task so it doesn't block
    asyncio.create_task(eng.start())
    logger.info("Bot start initiated via API")

    return {"message": "Bot started"}


@router.post("/stop")
async def stop_bot(eng: KhufraEngine = Depends(get_engine)):
    """Stop the trading engine gracefully."""
    if not eng.running:
        raise HTTPException(status_code=409, detail="Bot is not running")

    await eng.stop()
    logger.info("Bot stopped via API")

    return {"message": "Bot stopped"}


@router.post("/kill-switch")
async def activate_kill_switch(eng: KhufraEngine = Depends(get_engine)):
    """Emergency kill switch: close all positions and halt trading."""
    await eng.kill_switch()
    logger.critical("Kill switch activated via API")

    return {"message": "Kill switch activated"}


@router.put("/mode")
async def change_mode(
    request: ModeChangeRequest,
    eng: KhufraEngine = Depends(get_engine),
):
    """Change trading mode (paper/live). Requires bot to be stopped first."""
    if request.mode not in ("paper", "live"):
        raise HTTPException(
            status_code=400,
            detail="Mode must be 'paper' or 'live'",
        )

    if eng.running:
        raise HTTPException(
            status_code=409,
            detail="Cannot change mode while bot is running. Stop the bot first.",
        )

    eng.config.system.mode = request.mode
    logger.info(f"Mode changed to {request.mode} via API")

    return {"message": f"Mode changed to {request.mode}"}

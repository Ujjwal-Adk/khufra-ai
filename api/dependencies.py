"""
Khufra Trading System - FastAPI Dependencies
Engine dependency injection for route handlers.
"""

import logging
from typing import Optional

from fastapi import HTTPException

from core.engine import KhufraEngine
from core.config import KhufraConfig

logger = logging.getLogger(__name__)

# Global engine instance
engine: Optional[KhufraEngine] = None


async def initialize_engine():
    """Create and store the engine instance. Does NOT start the trading loop."""
    global engine
    try:
        config = KhufraConfig()
        engine = KhufraEngine(config)
        logger.info("KhufraEngine instance created (not started)")
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}", exc_info=True)
        raise


def get_engine() -> KhufraEngine:
    """FastAPI dependency that returns the engine or raises 503 if unavailable."""
    if engine is None:
        raise HTTPException(
            status_code=503,
            detail="Engine not initialized. Server is starting up.",
        )
    return engine


async def shutdown_engine():
    """Stop the engine if it is running."""
    global engine
    if engine is not None and engine.running:
        await engine.stop()
        logger.info("Engine stopped during shutdown")

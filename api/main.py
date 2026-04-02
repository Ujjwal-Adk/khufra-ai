"""
Khufra Trading System - FastAPI Application
REST API wrapper for the AI trading engine.
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import initialize_engine, shutdown_engine
from api.routes import status, regime, signals, trades, bot, portfolio, market

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the engine on startup, clean up on shutdown."""
    logger.info("Starting Khufra API server...")
    await initialize_engine()
    logger.info("Engine initialized — API ready")
    yield
    logger.info("Shutting down Khufra API server...")
    await shutdown_engine()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Khufra AI Trading Engine",
    description="REST API for the Khufra crypto trading system",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js dashboard and dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount route modules
app.include_router(status.router)
app.include_router(regime.router)
app.include_router(signals.router)
app.include_router(trades.router)
app.include_router(bot.router)
app.include_router(portfolio.router)
app.include_router(market.router)


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

"""
Khufra Trading System - API Pydantic Schemas
Request/response models for all FastAPI endpoints.
"""

from typing import Optional
from pydantic import BaseModel


class RegimeStateResponse(BaseModel):
    regime: str
    confidence: float
    adx: float
    atr_ratio: float
    bb_percentile: float
    ema_fast: float
    ema_slow: float
    price: float
    timestamp: str


class ConfidenceBreakdownResponse(BaseModel):
    regime: int
    behavioral: int
    whale: int
    order_book: int
    funding_rate: int
    volume: int


class SignalResponse(BaseModel):
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    strategy_name: str
    confidence_score: int
    confidence_breakdown: ConfidenceBreakdownResponse
    regime: str
    behavioral_pattern: str
    timestamp: str


class TradeJournalResponse(BaseModel):
    id: int
    symbol: str
    direction: str
    entry_price: float
    exit_price: Optional[float]
    entry_time: str
    exit_time: Optional[str]
    position_size: float
    leverage: int
    pnl_usd: Optional[float]
    pnl_pct: Optional[float]
    regime: str
    strategy: str
    confidence_score: int
    behavioral_pattern: str
    exit_reason: Optional[str]
    is_paper: bool


class BotStatusResponse(BaseModel):
    running: bool
    mode: str
    uptime_seconds: float
    current_regime: Optional[str]
    open_positions: int
    equity: float
    daily_pnl: float
    daily_drawdown: float
    consecutive_losses: int
    trading_halted: bool
    halt_reason: str


class PortfolioSummaryResponse(BaseModel):
    equity: float
    starting_equity: float
    return_pct: float
    daily_pnl: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    open_positions: int


class BehavioralSignalResponse(BaseModel):
    pattern: str
    direction: str
    strength: float
    details: dict
    timestamp: str


class MarketMemoryResponse(BaseModel):
    price_level: float
    level_type: str
    touch_count: int
    significance_score: float


class IndicatorsResponse(BaseModel):
    adx: Optional[float]
    rsi: Optional[float]
    atr: Optional[float]
    ema_fast: Optional[float]
    ema_slow: Optional[float]
    bb_width: Optional[float]
    volume_spike: Optional[float]


class KillZoneResponse(BaseModel):
    name: str
    start: str
    end: str
    is_active: bool

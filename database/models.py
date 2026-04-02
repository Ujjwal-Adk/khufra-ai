"""
Khufra Trading System - Database Models v2
Defines schema for trades, market memory, trade journal, and performance.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    Text, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class MarketRegime(str, enum.Enum):
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    VOLATILE = "volatile"
    DEAD = "dead"
    TRANSITION = "transition"


class TradeDirection(str, enum.Enum):
    LONG = "long"
    SHORT = "short"


class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ExitReason(str, enum.Enum):
    TP_HIT = "tp_hit"
    SL_HIT = "sl_hit"
    TRAILING_STOP = "trailing_stop"
    MANUAL = "manual"
    KILL_SWITCH = "kill_switch"
    DAILY_LIMIT = "daily_limit"
    STALE_DATA = "stale_data"


class TradeJournal(Base):
    """
    Full trade journal with WHY context — V2 Section 10.
    Every trade logged with regime, strategy, confidence breakdown.
    """
    __tablename__ = "trade_journal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    direction = Column(SQLEnum(TradeDirection), nullable=False)

    # Entry/Exit
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    position_size = Column(Float, nullable=True)  # in USD
    leverage = Column(Integer, default=1)

    # P&L
    pnl_usd = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)
    fees_paid = Column(Float, default=0.0)

    # CONTEXT — why the trade was taken
    regime = Column(SQLEnum(MarketRegime), nullable=True)
    strategy = Column(String(50), nullable=True)
    confidence_score = Column(Integer, nullable=True)
    score_breakdown = Column(JSON, nullable=True)  # {regime: 20, behavioral: 25, ...}
    behavioral_pattern = Column(String(50), nullable=True)  # stop_hunt, liquidation_cascade, etc.
    whale_signal = Column(String(100), nullable=True)  # Phase 3
    kill_zone = Column(String(30), nullable=True)

    # Risk
    stop_loss_price = Column(Float, nullable=True)
    take_profit_price = Column(Float, nullable=True)
    exit_reason = Column(SQLEnum(ExitReason), nullable=True)

    # Meta
    is_paper = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (f"<TradeJournal(symbol={self.symbol}, dir={self.direction}, "
                f"regime={self.regime}, score={self.confidence_score})>")


class MarketMemory(Base):
    """
    Market Memory — V2 Section 6.
    Tracks key price levels with significance decay.
    """
    __tablename__ = "market_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    price_level = Column(Float, nullable=False)
    level_type = Column(String(30), nullable=True)  # support, resistance, liquidation_cluster
    touch_count = Column(Integer, default=1)
    avg_reaction_volume = Column(Float, nullable=True)
    last_regime = Column(String(20), nullable=True)
    last_touched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    significance_score = Column(Float, default=1.0)

    def __repr__(self):
        return (f"<MarketMemory(symbol={self.symbol}, level={self.price_level}, "
                f"type={self.level_type}, touches={self.touch_count})>")


class PerformanceMetrics(Base):
    """Daily/weekly/monthly performance tracking."""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly

    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, nullable=True)

    total_profit = Column(Float, default=0.0)
    total_loss = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    return_percent = Column(Float, nullable=True)

    max_drawdown = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    avg_risk_reward = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)

    starting_balance = Column(Float, nullable=True)
    ending_balance = Column(Float, nullable=True)

    # Per-regime breakdown
    regime_breakdown = Column(JSON, nullable=True)  # {trending_up: {trades: 5, pnl: 200}, ...}

    created_at = Column(DateTime, default=datetime.utcnow)


class SystemLog(Base):
    """Critical system events and errors."""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    exception_type = Column(String(100), nullable=True)
    stack_trace = Column(Text, nullable=True)
    context_data = Column(JSON, nullable=True)


class RegimeHistory(Base):
    """Track all regime changes for analysis."""
    __tablename__ = "regime_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    regime = Column(SQLEnum(MarketRegime), nullable=False)
    previous_regime = Column(SQLEnum(MarketRegime), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Detection factors
    adx_value = Column(Float, nullable=True)
    atr_value = Column(Float, nullable=True)
    atr_avg = Column(Float, nullable=True)
    ema_fast_value = Column(Float, nullable=True)
    ema_slow_value = Column(Float, nullable=True)
    bb_width_percentile = Column(Float, nullable=True)
    price = Column(Float, nullable=True)

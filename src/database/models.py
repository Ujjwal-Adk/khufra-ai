"""
Project Khufra AI - Database Models
Defines the database schema for storing trades, signals, and performance data.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    Text, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class TradeStatus(str, enum.Enum):
    """Trade status enumeration."""
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TradeDirection(str, enum.Enum):
    """Trade direction enumeration."""
    LONG = "long"
    SHORT = "short"


class SignalSource(str, enum.Enum):
    """Signal source enumeration."""
    TRADINGVIEW = "tradingview"
    NEWS = "news"
    AI = "ai"
    MANUAL = "manual"


class Trade(Base):
    """
    Trade model - stores all trade information.
    """
    __tablename__ = "trades"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Trade identification
    trade_id = Column(String(50), unique=True, nullable=False, index=True)
    exchange = Column(String(50), nullable=False, default="bitget")
    trading_pair = Column(String(20), nullable=False, index=True)

    # Trade details
    direction = Column(SQLEnum(TradeDirection), nullable=False)
    status = Column(SQLEnum(TradeStatus), nullable=False, default=TradeStatus.PENDING, index=True)

    # Entry
    entry_price = Column(Float, nullable=True)
    entry_time = Column(DateTime, nullable=True)
    position_size = Column(Float, nullable=False)
    position_size_usd = Column(Float, nullable=True)

    # Exit
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime, nullable=True)

    # Stop loss & Take profit
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    trailing_stop = Column(Boolean, default=False)
    trailing_stop_percent = Column(Float, nullable=True)

    # Performance metrics
    profit_loss = Column(Float, nullable=True)
    profit_loss_percent = Column(Float, nullable=True)
    fees_paid = Column(Float, nullable=True, default=0.0)
    net_profit_loss = Column(Float, nullable=True)

    # Strategy & signals
    strategy_id = Column(String(50), nullable=True)
    strategy_name = Column(String(100), nullable=True)
    signal_source = Column(SQLEnum(SignalSource), nullable=True)
    confidence_score = Column(Float, nullable=True)

    # AI analysis
    ai_decision = Column(Text, nullable=True)
    ai_reasoning = Column(Text, nullable=True)

    # Risk management
    risk_amount = Column(Float, nullable=True)
    risk_percent = Column(Float, nullable=True)
    risk_reward_ratio = Column(Float, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Trading mode
    is_paper_trade = Column(Boolean, default=True, nullable=False)

    # Relationships
    signals = relationship("Signal", back_populates="trade", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"<Trade(id={self.trade_id}, pair={self.trading_pair}, "
                f"direction={self.direction}, status={self.status})>")

    def calculate_pnl(self):
        """Calculate profit/loss for the trade."""
        if self.entry_price and self.exit_price:
            if self.direction == TradeDirection.LONG:
                raw_pnl = (self.exit_price - self.entry_price) * self.position_size
            else:  # SHORT
                raw_pnl = (self.entry_price - self.exit_price) * self.position_size

            self.profit_loss = raw_pnl
            self.net_profit_loss = raw_pnl - (self.fees_paid or 0)

            if self.entry_price > 0:
                self.profit_loss_percent = ((self.exit_price - self.entry_price) / self.entry_price) * 100
                if self.direction == TradeDirection.SHORT:
                    self.profit_loss_percent *= -1

    def is_profitable(self) -> bool:
        """Check if trade was profitable."""
        return (self.net_profit_loss or 0) > 0

    def duration_seconds(self) -> Optional[float]:
        """Calculate trade duration in seconds."""
        if self.entry_time and self.exit_time:
            return (self.exit_time - self.entry_time).total_seconds()
        return None


class Signal(Base):
    """
    Signal model - stores trading signals from various sources.
    """
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Signal identification
    signal_id = Column(String(50), unique=True, nullable=False, index=True)
    source = Column(SQLEnum(SignalSource), nullable=False, index=True)

    # Signal details
    trading_pair = Column(String(20), nullable=False, index=True)
    direction = Column(SQLEnum(TradeDirection), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Signal data
    price = Column(Float, nullable=True)
    suggested_entry = Column(Float, nullable=True)
    suggested_stop_loss = Column(Float, nullable=True)
    suggested_take_profit = Column(Float, nullable=True)

    # Confidence & validation
    confidence = Column(Float, nullable=True)
    validated = Column(Boolean, default=False)
    validation_notes = Column(Text, nullable=True)

    # Source-specific data
    raw_data = Column(Text, nullable=True)  # JSON string of raw signal data

    # Processing
    processed = Column(Boolean, default=False, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)

    # Relationships
    trade = relationship("Trade", back_populates="signals")

    def __repr__(self):
        return (f"<Signal(id={self.signal_id}, source={self.source}, "
                f"pair={self.trading_pair}, direction={self.direction})>")


class NewsEvent(Base):
    """
    News event model - stores important market news and sentiment.
    """
    __tablename__ = "news_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # News identification
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    source = Column(String(100), nullable=False)

    # News content
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)
    published_at = Column(DateTime, nullable=False, index=True)

    # Sentiment analysis
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    ai_analysis = Column(Text, nullable=True)

    # Impact assessment
    relevance_score = Column(Float, nullable=True)  # 0.0 to 1.0
    market_impact = Column(String(20), nullable=True)  # high, medium, low
    affected_coins = Column(String(200), nullable=True)  # Comma-separated list

    # Processing
    processed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<NewsEvent(id={self.event_id}, sentiment={self.sentiment}, impact={self.market_impact})>"


class PerformanceMetrics(Base):
    """
    Performance metrics model - tracks daily/monthly performance.
    """
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Time period
    date = Column(DateTime, nullable=False, unique=True, index=True)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly

    # Trade statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, nullable=True)

    # Financial metrics
    total_profit = Column(Float, default=0.0)
    total_loss = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    return_percent = Column(Float, nullable=True)

    # Risk metrics
    max_drawdown = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    avg_risk_reward = Column(Float, nullable=True)

    # Portfolio
    starting_balance = Column(Float, nullable=True)
    ending_balance = Column(Float, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (f"<PerformanceMetrics(date={self.date}, trades={self.total_trades}, "
                f"win_rate={self.win_rate:.1f}%)>")


class SystemLog(Base):
    """
    System log model - stores critical system events and errors.
    """
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Log details
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)

    # Additional context
    exception_type = Column(String(100), nullable=True)
    stack_trace = Column(Text, nullable=True)
    context_data = Column(Text, nullable=True)  # JSON string (renamed from metadata to avoid SQLAlchemy conflict)

    def __repr__(self):
        return f"<SystemLog(level={self.level}, module={self.module}, time={self.timestamp})>"

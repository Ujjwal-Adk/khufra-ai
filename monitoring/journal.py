"""
Khufra Trading System - Trade Journal
Logs every trade with full context (WHY it was taken).
V2 Spec Section 10.
"""

import logging
from datetime import datetime
from typing import Optional

from database.models import TradeJournal, MarketRegime, TradeDirection, ExitReason

logger = logging.getLogger(__name__)


class TradeJournalManager:
    """Manages trade journal entries in the database."""

    def __init__(self, db_manager):
        self.db = db_manager

    def record_entry(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        position_size: float,
        leverage: int,
        stop_loss: float,
        take_profit: float,
        regime: str,
        strategy: str,
        confidence_score: int,
        score_breakdown: dict,
        behavioral_pattern: str = "",
        kill_zone: str = "",
        is_paper: bool = True,
    ) -> Optional[int]:
        """Record a trade entry in the journal."""
        try:
            with self.db.get_session() as session:
                entry = TradeJournal(
                    symbol=symbol,
                    direction=TradeDirection(direction),
                    entry_price=entry_price,
                    entry_time=datetime.utcnow(),
                    position_size=position_size,
                    leverage=leverage,
                    stop_loss_price=stop_loss,
                    take_profit_price=take_profit,
                    regime=MarketRegime(regime),
                    strategy=strategy,
                    confidence_score=confidence_score,
                    score_breakdown=score_breakdown,
                    behavioral_pattern=behavioral_pattern,
                    kill_zone=kill_zone,
                    is_paper=is_paper,
                )
                session.add(entry)
                session.flush()
                entry_id = entry.id
                logger.info(f"Journal entry recorded: #{entry_id}")
                return entry_id
        except Exception as e:
            logger.error(f"Failed to record journal entry: {e}", exc_info=True)
            return None

    def record_exit(
        self,
        journal_id: int,
        exit_price: float,
        pnl_usd: float,
        pnl_pct: float,
        fees: float,
        exit_reason: str,
        notes: str = "",
    ):
        """Update journal entry with exit data."""
        try:
            with self.db.get_session() as session:
                entry = session.query(TradeJournal).filter_by(id=journal_id).first()
                if entry:
                    entry.exit_price = exit_price
                    entry.exit_time = datetime.utcnow()
                    entry.pnl_usd = pnl_usd
                    entry.pnl_pct = pnl_pct
                    entry.fees_paid = fees
                    entry.exit_reason = ExitReason(exit_reason)
                    entry.notes = notes
                    logger.info(f"Journal exit recorded: #{journal_id} | P&L: ${pnl_usd:.2f}")
                else:
                    logger.warning(f"Journal entry #{journal_id} not found")
        except Exception as e:
            logger.error(f"Failed to record journal exit: {e}", exc_info=True)

    def get_recent_trades(self, limit: int = 20) -> list:
        """Get recent journal entries."""
        try:
            with self.db.get_session() as session:
                entries = (
                    session.query(TradeJournal)
                    .order_by(TradeJournal.entry_time.desc())
                    .limit(limit)
                    .all()
                )
                return entries
        except Exception as e:
            logger.error(f"Failed to fetch recent trades: {e}")
            return []

    def get_regime_stats(self) -> dict:
        """Get win/loss stats per regime."""
        try:
            with self.db.get_session() as session:
                entries = session.query(TradeJournal).filter(
                    TradeJournal.pnl_usd.isnot(None)
                ).all()

                stats = {}
                for entry in entries:
                    regime = entry.regime.value if entry.regime else 'unknown'
                    if regime not in stats:
                        stats[regime] = {'wins': 0, 'losses': 0, 'total_pnl': 0}
                    if entry.pnl_usd > 0:
                        stats[regime]['wins'] += 1
                    else:
                        stats[regime]['losses'] += 1
                    stats[regime]['total_pnl'] += entry.pnl_usd or 0

                return stats
        except Exception as e:
            logger.error(f"Failed to get regime stats: {e}")
            return {}

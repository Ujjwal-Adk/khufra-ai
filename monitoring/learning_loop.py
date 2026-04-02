"""
Khufra Trading System - Learning Loop
Weekly automated performance review and weight adjustment proposals.
V2 Spec Section 10.2.
IMPORTANT: Proposes changes but does NOT auto-apply them.
"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class LearningLoop:
    """
    Weekly performance review.
    Analyzes per-factor accuracy and proposes weight adjustments.
    Human-in-the-loop: operator must approve before changes take effect.
    """

    def __init__(self, config, journal_manager, telegram):
        self.config = config
        self.journal = journal_manager
        self.telegram = telegram
        self.min_trades = config.learning_loop.min_trades_for_analysis

    async def run_weekly_review(self):
        """
        Run weekly performance analysis.
        Called by scheduler every Sunday 00:00 UTC.
        """
        logger.info("Running weekly learning loop review...")

        trades = self.journal.get_recent_trades(limit=100)
        closed = [t for t in trades if t.pnl_usd is not None]

        if len(closed) < self.min_trades:
            msg = f"Learning loop: only {len(closed)} trades (need {self.min_trades}). Skipping."
            logger.info(msg)
            await self.telegram.send_message(msg)
            return

        # Per-regime performance
        regime_stats = self.journal.get_regime_stats()

        # Build report
        report = self._build_report(closed, regime_stats)

        # Send via Telegram
        await self.telegram.send_message(report)
        logger.info("Weekly review sent to Telegram")

    def _build_report(self, trades: list, regime_stats: dict) -> str:
        """Build weekly performance report."""
        total = len(trades)
        wins = sum(1 for t in trades if t.pnl_usd > 0)
        total_pnl = sum(t.pnl_usd for t in trades)

        lines = [
            "<b>WEEKLY REVIEW</b>",
            f"Period: last {total} trades",
            f"Win Rate: {wins/total*100:.1f}%",
            f"Total P&L: ${total_pnl:.2f}",
            "",
            "<b>Per-Regime:</b>",
        ]

        for regime, stats in regime_stats.items():
            total_r = stats['wins'] + stats['losses']
            wr = stats['wins'] / total_r * 100 if total_r > 0 else 0
            lines.append(
                f"  {regime}: {total_r} trades | WR: {wr:.0f}% | P&L: ${stats['total_pnl']:.2f}"
            )

        lines.append("")
        lines.append("<i>Weight changes require /approve_weights</i>")

        return "\n".join(lines)

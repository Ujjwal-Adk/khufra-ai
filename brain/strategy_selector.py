"""
Khufra Trading System - Strategy Selector
Maps detected regime to the appropriate trading strategy.
"""

import logging
from typing import Optional

from brain.regime_detector import Regime
from brain.strategies.base import BaseStrategy
from brain.strategies.trend_follow import TrendFollowStrategy
from brain.strategies.mean_reversion import MeanReversionStrategy
from brain.strategies.cascade_reversal import CascadeReversalStrategy
from brain.strategies.no_trade import NoTradeStrategy

logger = logging.getLogger(__name__)


class StrategySelector:
    """Maps regime → strategy. Simple and deterministic."""

    def __init__(self, config):
        self.config = config
        self.strategies = {
            Regime.TRENDING_UP: TrendFollowStrategy(config),
            Regime.TRENDING_DOWN: TrendFollowStrategy(config),
            Regime.RANGING: MeanReversionStrategy(config),
            Regime.VOLATILE: CascadeReversalStrategy(config),
            Regime.DEAD: NoTradeStrategy(config),
            Regime.TRANSITION: NoTradeStrategy(config),
        }

    def select(self, regime: str) -> BaseStrategy:
        """Select the strategy for the given regime."""
        strategy = self.strategies.get(regime)
        if strategy is None:
            logger.warning(f"No strategy for regime '{regime}', defaulting to no_trade")
            return self.strategies[Regime.DEAD]

        logger.debug(f"Selected strategy: {strategy.name} for regime: {regime}")
        return strategy

    def get_strategy_name(self, regime: str) -> str:
        """Get strategy name for a regime."""
        strategy = self.select(regime)
        return strategy.name

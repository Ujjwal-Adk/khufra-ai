"""
Khufra Trading System - No Trade Strategy
Deployed during DEAD regime. Capital preservation.
"""

import logging
from typing import Optional
import pandas as pd

from brain.strategies.base import BaseStrategy, TradeSignal

logger = logging.getLogger(__name__)


class NoTradeStrategy(BaseStrategy):
    """
    Dead market handler. No trades — just log and wait.
    Capital preservation is the priority.
    """

    name = "no_trade"
    regime = "dead"

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: dict,
        current_price: float,
    ) -> Optional[TradeSignal]:
        logger.debug("DEAD regime — no trades. Waiting for regime change.")
        return None

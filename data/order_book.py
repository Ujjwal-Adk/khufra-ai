"""
Khufra Trading System - Order Book Analysis
Analyzes order book depth for wall detection, air pockets, and spoofing.
V2 Spec Section 3.2.2.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class OrderBookState:
    """Snapshot of order book analysis."""
    bid_wall_price: Optional[float] = None
    bid_wall_size: float = 0.0
    ask_wall_price: Optional[float] = None
    ask_wall_size: float = 0.0
    bid_depth_ratio: float = 1.0   # bid volume / ask volume
    has_air_pocket_up: bool = False
    has_air_pocket_down: bool = False
    support_score: float = 0.5     # 0-1 how much OB supports longs
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class OrderBookAnalyzer:
    """
    Analyzes order book depth data from WebSocket.
    Detects bid/ask walls, air pockets, and calculates support scores.
    """

    def __init__(self, config):
        self.config = config
        self.last_state: Optional[OrderBookState] = None
        self._bids: list = []
        self._asks: list = []

    async def handle_orderbook(self, data: list, arg: dict):
        """Handle order book update from WebSocket."""
        if not data:
            return

        book = data[0] if isinstance(data, list) and len(data) > 0 else data

        if isinstance(book, dict):
            self._bids = [[float(b[0]), float(b[1])] for b in book.get('bids', [])]
            self._asks = [[float(a[0]), float(a[1])] for a in book.get('asks', [])]
        elif isinstance(book, list):
            # Some formats provide [bids, asks] directly
            pass

        self.last_state = self._analyze()

    def _analyze(self) -> OrderBookState:
        """Analyze current order book state."""
        state = OrderBookState()

        if not self._bids or not self._asks:
            return state

        # Total depth
        total_bid_vol = sum(b[1] for b in self._bids)
        total_ask_vol = sum(a[1] for a in self._asks)

        state.bid_depth_ratio = total_bid_vol / total_ask_vol if total_ask_vol > 0 else 1.0

        # Find bid walls (large orders on buy side)
        avg_bid_size = total_bid_vol / len(self._bids) if self._bids else 0
        for price, size in self._bids:
            if size > avg_bid_size * 5:  # 5x average = wall
                if state.bid_wall_size < size:
                    state.bid_wall_price = price
                    state.bid_wall_size = size

        # Find ask walls
        avg_ask_size = total_ask_vol / len(self._asks) if self._asks else 0
        for price, size in self._asks:
            if size > avg_ask_size * 5:
                if state.ask_wall_size < size:
                    state.ask_wall_price = price
                    state.ask_wall_size = size

        # Air pocket detection (thin zones where price can move quickly)
        if len(self._asks) >= 3:
            for i in range(len(self._asks) - 1):
                gap = self._asks[i + 1][0] - self._asks[i][0]
                mid_price = self._asks[0][0]
                if mid_price > 0 and gap / mid_price > 0.002:  # >0.2% gap
                    state.has_air_pocket_up = True
                    break

        if len(self._bids) >= 3:
            for i in range(len(self._bids) - 1):
                gap = self._bids[i][0] - self._bids[i + 1][0]
                mid_price = self._bids[0][0]
                if mid_price > 0 and gap / mid_price > 0.002:
                    state.has_air_pocket_down = True
                    break

        # Calculate support score (0=bearish OB, 1=bullish OB)
        ratio_score = min(1.0, state.bid_depth_ratio / 2.0)
        wall_bonus = 0.2 if state.bid_wall_price else -0.2 if state.ask_wall_price else 0
        state.support_score = max(0, min(1.0, 0.5 + (ratio_score - 0.5) + wall_bonus))

        return state

    def get_support_score(self) -> float:
        """Get current order book support score (0-1)."""
        return self.last_state.support_score if self.last_state else 0.5

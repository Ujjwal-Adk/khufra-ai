"""
Khufra Trading System - Candle Builder
Manages OHLCV candle data from WebSocket feeds.
Maintains rolling DataFrame for indicator calculations.
"""

import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class CandleBuilder:
    """
    Maintains OHLCV candle DataFrames for multiple timeframes.
    Receives kline updates from WebSocket and keeps rolling history.
    """

    def __init__(self, max_candles: int = 500):
        self.max_candles = max_candles
        self.candles: dict[str, pd.DataFrame] = {}

    def initialize_empty(self, timeframe: str):
        """Initialize an empty DataFrame for a timeframe."""
        self.candles[timeframe] = pd.DataFrame(
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        ).astype({
            'timestamp': 'datetime64[ns]',
            'open': 'float64', 'high': 'float64',
            'low': 'float64', 'close': 'float64', 'volume': 'float64'
        })

    async def handle_kline(self, data: list, arg: dict):
        """
        Handle kline/candle update from WebSocket.
        Bitget kline format: [timestamp, open, high, low, close, volume, ...]
        """
        channel = arg.get('channel', '')

        # Map channel to timeframe
        if '1H' in channel:
            tf = '1h'
        elif '15m' in channel:
            tf = '15m'
        elif '5m' in channel:
            tf = '5m'
        elif '4H' in channel:
            tf = '4h'
        else:
            tf = channel

        if tf not in self.candles:
            self.initialize_empty(tf)

        for kline in data:
            try:
                ts = datetime.fromtimestamp(int(kline[0]) / 1000)
                new_row = {
                    'timestamp': ts,
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                }

                df = self.candles[tf]

                # Update existing candle or append new one
                if len(df) > 0 and df.iloc[-1]['timestamp'] == ts:
                    # Update current candle
                    idx = df.index[-1]
                    for col, val in new_row.items():
                        df.at[idx, col] = val
                else:
                    # Append new candle
                    new_df = pd.DataFrame([new_row])
                    self.candles[tf] = pd.concat([df, new_df], ignore_index=True)

                # Trim to max candles
                if len(self.candles[tf]) > self.max_candles:
                    self.candles[tf] = self.candles[tf].iloc[-self.max_candles:].reset_index(drop=True)

            except (IndexError, ValueError) as e:
                logger.warning(f"Error parsing kline data: {e}")

    def get_candles(self, timeframe: str) -> Optional[pd.DataFrame]:
        """Get candle DataFrame for a timeframe."""
        df = self.candles.get(timeframe)
        if df is None or len(df) == 0:
            return None
        return df.copy()

    def get_latest_price(self, timeframe: str = '1h') -> Optional[float]:
        """Get the most recent close price."""
        df = self.candles.get(timeframe)
        if df is not None and len(df) > 0:
            return float(df['close'].iloc[-1])
        return None

    def load_historical(self, timeframe: str, df: pd.DataFrame):
        """Load historical candle data (e.g., from REST API at startup)."""
        required = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")

        self.candles[timeframe] = df.tail(self.max_candles).reset_index(drop=True)
        logger.info(f"Loaded {len(self.candles[timeframe])} historical candles for {timeframe}")

    @property
    def has_data(self) -> bool:
        """Check if we have any candle data."""
        return any(len(df) > 0 for df in self.candles.values())

    def candle_count(self, timeframe: str) -> int:
        """Get number of candles for a timeframe."""
        df = self.candles.get(timeframe)
        return len(df) if df is not None else 0

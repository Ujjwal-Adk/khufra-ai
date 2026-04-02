"""
Khufra Trading System - Bitget WebSocket Client
Real-time data feed from Bitget exchange.
Provides klines, trades, and order book depth.
"""

import asyncio
import json
import logging
import time
import hmac
import hashlib
import base64
from datetime import datetime
from typing import Callable, Optional

import websockets
import pandas as pd

logger = logging.getLogger(__name__)

BITGET_WS_PUBLIC = "wss://ws.bitget.com/v2/ws/public"
BITGET_WS_PRIVATE = "wss://ws.bitget.com/v2/ws/private"


class BitgetWebSocket:
    """
    Bitget WebSocket client for real-time market data.
    Subscribes to klines, trades, and order book.
    """

    def __init__(self, config):
        self.config = config
        self.symbol = config.system.symbol
        self.ws = None
        self.running = False
        self._callbacks: dict[str, list[Callable]] = {}
        self._reconnect_delay = 1
        self._max_reconnect_delay = 60
        self._last_ping = 0

    async def connect(self):
        """Connect to Bitget WebSocket and subscribe to channels."""
        self.running = True
        while self.running:
            try:
                logger.info(f"Connecting to Bitget WebSocket...")
                async with websockets.connect(
                    BITGET_WS_PUBLIC,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=5,
                ) as ws:
                    self.ws = ws
                    self._reconnect_delay = 1
                    logger.info("WebSocket connected")

                    await self._subscribe(ws)
                    await self._listen(ws)

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"WebSocket connection closed: {e}")
            except Exception as e:
                logger.error(f"WebSocket error: {e}", exc_info=True)

            if self.running:
                logger.info(f"Reconnecting in {self._reconnect_delay}s...")
                await asyncio.sleep(self._reconnect_delay)
                self._reconnect_delay = min(
                    self._reconnect_delay * 2,
                    self._max_reconnect_delay
                )

    async def _subscribe(self, ws):
        """Subscribe to market data channels."""
        channels = [
            # Klines
            {"instType": "USDT-FUTURES", "channel": "candle1H", "instId": self.symbol},
            {"instType": "USDT-FUTURES", "channel": "candle15m", "instId": self.symbol},
            # Trades
            {"instType": "USDT-FUTURES", "channel": "trade", "instId": self.symbol},
            # Order book (depth 15)
            {"instType": "USDT-FUTURES", "channel": "books15", "instId": self.symbol},
            # Ticker
            {"instType": "USDT-FUTURES", "channel": "ticker", "instId": self.symbol},
        ]

        subscribe_msg = {
            "op": "subscribe",
            "args": channels
        }

        await ws.send(json.dumps(subscribe_msg))
        logger.info(f"Subscribed to {len(channels)} channels for {self.symbol}")

    async def _listen(self, ws):
        """Listen for incoming messages."""
        async for message in ws:
            try:
                data = json.loads(message)

                # Handle ping/pong
                if data.get('event') == 'pong' or message == 'pong':
                    continue

                # Handle subscription confirmation
                if data.get('event') == 'subscribe':
                    logger.debug(f"Subscription confirmed: {data.get('arg', {})}")
                    continue

                if data.get('event') == 'error':
                    logger.error(f"WebSocket error: {data}")
                    continue

                # Handle data messages
                if 'data' in data and 'arg' in data:
                    channel = data['arg'].get('channel', '')
                    await self._dispatch(channel, data['data'], data['arg'])

            except json.JSONDecodeError:
                if message == 'pong':
                    continue
                logger.warning(f"Non-JSON message: {message[:100]}")
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)

    async def _dispatch(self, channel: str, data: list, arg: dict):
        """Dispatch data to registered callbacks."""
        # Determine event type
        if channel.startswith('candle'):
            event_type = 'kline'
        elif channel == 'trade':
            event_type = 'trade'
        elif channel.startswith('books'):
            event_type = 'orderbook'
        elif channel == 'ticker':
            event_type = 'ticker'
        else:
            event_type = channel

        callbacks = self._callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                await callback(data, arg)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}", exc_info=True)

    def on(self, event_type: str, callback: Callable):
        """Register a callback for an event type."""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)

    async def disconnect(self):
        """Disconnect WebSocket."""
        self.running = False
        if self.ws:
            await self.ws.close()
            logger.info("WebSocket disconnected")

    async def send_ping(self):
        """Send keepalive ping."""
        if self.ws and self.running:
            try:
                await self.ws.send("ping")
            except Exception:
                pass

"""
Khufra Trading System - Bitget REST API Client
Handles order placement, position queries, and account info.
Uses HMAC SHA256 authentication.
"""

import asyncio
import hashlib
import hmac
import base64
import json
import logging
import time
from datetime import datetime
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

BITGET_API_URL = "https://api.bitget.com"


class BitgetClient:
    """
    Bitget REST API client for USDT-M perpetual futures.
    Handles authentication, order management, and account queries.
    """

    def __init__(self, config):
        self.config = config
        self.api_key = config.secrets.bitget_api_key
        self.api_secret = config.secrets.bitget_api_secret
        self.passphrase = config.secrets.bitget_passphrase
        self.session: Optional[aiohttp.ClientSession] = None
        self.symbol = config.system.symbol

    async def connect(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession()
        logger.info("Bitget REST client initialized")

    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("Bitget REST client closed")

    def _sign(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate HMAC SHA256 signature for Bitget API."""
        message = timestamp + method.upper() + path + body
        mac = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode('utf-8')

    def _headers(self, method: str, path: str, body: str = "") -> dict:
        """Build authenticated request headers."""
        timestamp = str(int(time.time() * 1000))
        sign = self._sign(timestamp, method, path, body)
        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": sign,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "locale": "en-US",
        }

    async def _request(self, method: str, path: str, params: dict = None, body: dict = None) -> dict:
        """Make authenticated API request."""
        if not self.session:
            raise RuntimeError("Client not connected")

        url = BITGET_API_URL + path
        body_str = json.dumps(body) if body else ""

        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            path_with_query = f"{path}?{query}"
            headers = self._headers(method, path_with_query, body_str)
            url = f"{url}?{query}"
        else:
            headers = self._headers(method, path, body_str)

        try:
            async with self.session.request(
                method, url, headers=headers,
                data=body_str if body else None,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
                if data.get('code') != '00000':
                    logger.error(f"Bitget API error: {data}")
                return data
        except Exception as e:
            logger.error(f"Bitget API request failed: {e}", exc_info=True)
            raise

    # ── Account ────────────────────────────────────────────

    async def get_account_info(self) -> dict:
        """Get futures account info (equity, available, unrealized PnL)."""
        path = "/api/v2/mix/account/account"
        params = {"symbol": self.symbol, "productType": "USDT-FUTURES", "marginCoin": "USDT"}
        return await self._request("GET", path, params=params)

    async def get_equity(self) -> float:
        """Get current account equity in USDT."""
        data = await self.get_account_info()
        try:
            return float(data['data']['accountEquity'])
        except (KeyError, TypeError):
            logger.error(f"Failed to parse equity: {data}")
            return 0.0

    # ── Market Data ────────────────────────────────────────

    async def get_ticker(self) -> dict:
        """Get current ticker (price, volume, etc)."""
        path = "/api/v2/mix/market/ticker"
        params = {"symbol": self.symbol, "productType": "USDT-FUTURES"}
        return await self._request("GET", path, params=params)

    async def get_candles(self, granularity: str = "1H", limit: int = 200) -> list:
        """Get historical kline/candle data."""
        path = "/api/v2/mix/market/candles"
        params = {
            "symbol": self.symbol,
            "productType": "USDT-FUTURES",
            "granularity": granularity,
            "limit": str(limit),
        }
        data = await self._request("GET", path, params=params)
        return data.get('data', [])

    async def get_funding_rate(self) -> Optional[float]:
        """Get current funding rate."""
        path = "/api/v2/mix/market/current-fund-rate"
        params = {"symbol": self.symbol, "productType": "USDT-FUTURES"}
        data = await self._request("GET", path, params=params)
        try:
            return float(data['data']['fundingRate'])
        except (KeyError, TypeError):
            return None

    async def get_open_interest(self) -> Optional[float]:
        """Get current open interest."""
        path = "/api/v2/mix/market/open-interest"
        params = {"symbol": self.symbol, "productType": "USDT-FUTURES"}
        data = await self._request("GET", path, params=params)
        try:
            return float(data['data']['amount'])
        except (KeyError, TypeError):
            return None

    # ── Order Management ───────────────────────────────────

    async def place_order(
        self,
        side: str,          # 'buy' or 'sell'
        trade_side: str,    # 'open' or 'close'
        size: float,
        order_type: str = "market",
        price: float = None,
        stop_loss: float = None,
        take_profit: float = None,
    ) -> dict:
        """Place a futures order."""
        path = "/api/v2/mix/order/place-order"
        body = {
            "symbol": self.symbol,
            "productType": "USDT-FUTURES",
            "marginMode": "crossed",
            "marginCoin": "USDT",
            "side": side,
            "tradeSide": trade_side,
            "orderType": order_type,
            "size": str(size),
        }
        if price and order_type == "limit":
            body["price"] = str(price)
        if stop_loss:
            body["presetStopLossPrice"] = str(stop_loss)
        if take_profit:
            body["presetStopSurplusPrice"] = str(take_profit)

        return await self._request("POST", path, body=body)

    async def cancel_order(self, order_id: str) -> dict:
        """Cancel an open order."""
        path = "/api/v2/mix/order/cancel-order"
        body = {
            "symbol": self.symbol,
            "productType": "USDT-FUTURES",
            "orderId": order_id,
        }
        return await self._request("POST", path, body=body)

    async def get_positions(self) -> list:
        """Get all open positions."""
        path = "/api/v2/mix/position/all-position"
        params = {"productType": "USDT-FUTURES", "marginCoin": "USDT"}
        data = await self._request("GET", path, params=params)
        return data.get('data', [])

    async def close_all_positions(self) -> dict:
        """Emergency: close all positions."""
        path = "/api/v2/mix/order/close-positions"
        body = {
            "symbol": self.symbol,
            "productType": "USDT-FUTURES",
        }
        return await self._request("POST", path, body=body)

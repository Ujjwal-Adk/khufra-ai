"""
Khufra Trading System - Main Engine Orchestrator
Ties all modules together: data → brain → execution → monitoring.
V2 Architecture: WebSocket → Regime → Strategy → Confidence → Risk → Execute.
"""

import asyncio
import logging
from datetime import datetime, timezone

from core.config import KhufraConfig
from core.logger import setup_logger, TradeLogger
from database.connection import DatabaseManager
from data.websocket_client import BitgetWebSocket
from data.candle_builder import CandleBuilder
from data.order_book import OrderBookAnalyzer
from data.indicators import calculate_all_regime_indicators
from brain.regime_detector import RegimeDetector, Regime
from brain.strategy_selector import StrategySelector
from brain.behavioral import BehavioralDetector
from brain.confidence import ConfidenceEngine
from brain.market_memory import MarketMemory
from brain.ai_advisor import AIAdvisor
from execution.risk_manager import RiskManager
from execution.paper_trader import PaperTrader
from execution.bitget_client import BitgetClient
from monitoring.telegram_bot import TelegramNotifier
from monitoring.journal import TradeJournalManager

logger = logging.getLogger(__name__)
trade_logger = TradeLogger()


class KhufraEngine:
    """
    Main orchestrator. The heartbeat of the system.
    Pipeline: Data → Regime → Strategy → Behavioral → Confidence → Risk → Execute
    """

    def __init__(self, config: KhufraConfig = None):
        if config is None:
            from core.config import config as default_config
            config = default_config

        self.config = config
        self.running = False

        # Core components
        self.db = DatabaseManager(config.database_url)
        self.ws = BitgetWebSocket(config)
        self.candles = CandleBuilder()
        self.order_book = OrderBookAnalyzer(config)

        # Brain
        self.regime_detector = RegimeDetector(config)
        self.strategy_selector = StrategySelector(config)
        self.behavioral = BehavioralDetector(config)
        self.confidence = ConfidenceEngine(config)
        self.market_memory = MarketMemory(config)
        self.ai_advisor = AIAdvisor(config)

        # Execution
        self.risk_manager = RiskManager(config)
        self.paper_trader = PaperTrader(config)
        self.bitget_client = BitgetClient(config)

        # Monitoring
        self.telegram = TelegramNotifier(config)
        self.journal = None  # Initialized after DB connect

        # State
        self._last_regime = None
        self._current_funding_rate = None
        self._ticker_price = None

        # API state cache (readable by FastAPI endpoints)
        self.last_signal = None
        self.last_behavioral_signals = []
        self.last_confidence_result = None
        self.last_indicators = None
        self._start_time = None
        self._event_callbacks = {}

    async def start(self):
        """Start the engine and all subsystems."""
        logger.info("=" * 60)
        logger.info("KHUFRA TRADING SYSTEM v2.0")
        logger.info(f"Mode: {self.config.system.mode.upper()}")
        logger.info(f"Symbol: {self.config.system.symbol}")
        logger.info(f"Exchange: {self.config.system.exchange}")
        logger.info("=" * 60)

        # Validate config
        missing = self.config.validate()
        if missing:
            logger.warning(f"Missing settings: {', '.join(missing)}")

        # Initialize components
        await self._initialize()

        self._start_time = datetime.now(timezone.utc)
        self.running = True

        # Start concurrent tasks
        tasks = [
            asyncio.create_task(self.ws.connect()),
            asyncio.create_task(self._main_loop()),
            asyncio.create_task(self._health_monitor()),
        ]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Tasks cancelled")
        except Exception as e:
            logger.error(f"Engine error: {e}", exc_info=True)
        finally:
            await self.stop()

    async def _initialize(self):
        """Initialize all components."""
        # Database
        await self.db.connect()
        self.journal = TradeJournalManager(self.db)
        logger.info("Database connected")

        # Register WebSocket callbacks
        self.ws.on('kline', self.candles.handle_kline)
        self.ws.on('orderbook', self.order_book.handle_orderbook)
        self.ws.on('ticker', self._handle_ticker)

        # Load historical candles via REST API
        await self._load_historical_candles()

        # Initialize equity tracking
        if self.config.is_paper_trading():
            self.risk_manager.set_day_start_equity(self.paper_trader.equity)
        else:
            await self.bitget_client.connect()
            equity = await self.bitget_client.get_equity()
            self.risk_manager.set_day_start_equity(equity)

        # Start optional services
        await self.telegram.start()
        await self.ai_advisor.start()

        logger.info("All components initialized")

    async def _load_historical_candles(self):
        """Load historical candle data from REST API at startup."""
        try:
            await self.bitget_client.connect()

            for tf, granularity in [('1h', '1H'), ('15m', '15m')]:
                raw = await self.bitget_client.get_candles(granularity=granularity, limit=200)
                if raw:
                    import pandas as pd
                    rows = []
                    for c in raw:
                        rows.append({
                            'timestamp': pd.Timestamp(int(c[0]), unit='ms'),
                            'open': float(c[1]),
                            'high': float(c[2]),
                            'low': float(c[3]),
                            'close': float(c[4]),
                            'volume': float(c[5]),
                        })
                    if rows:
                        df = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)
                        self.candles.load_historical(tf, df)

            # Get initial funding rate
            self._current_funding_rate = await self.bitget_client.get_funding_rate()

            if not self.config.is_live_trading():
                await self.bitget_client.disconnect()

        except Exception as e:
            logger.warning(f"Failed to load historical data: {e}")
            logger.info("Will build candles from WebSocket stream instead")

    async def _handle_ticker(self, data: list, arg: dict):
        """Handle ticker updates for current price."""
        if data:
            try:
                ticker = data[0] if isinstance(data, list) else data
                self._ticker_price = float(ticker.get('lastPr', ticker.get('last', 0)))
                self.risk_manager.record_data_received()
            except (ValueError, KeyError, IndexError):
                pass

    async def _main_loop(self):
        """
        Main trading loop. Runs every cycle.
        Pipeline: Regime → Kill Zone → Strategy → Behavioral → Confidence → Risk → Execute
        """
        logger.info("Main loop started")

        while self.running:
            try:
                await self._trading_cycle()
            except Exception as e:
                logger.error(f"Trading cycle error: {e}", exc_info=True)

            await asyncio.sleep(5)  # 5-second cycle

    async def _trading_cycle(self):
        """Single trading cycle."""
        # Get candle data
        df_1h = self.candles.get_candles('1h')
        if df_1h is None or len(df_1h) < 50:
            return  # Not enough data yet

        current_price = self._ticker_price or self.candles.get_latest_price('1h')
        if not current_price:
            return

        # Step 1: Detect regime
        regime_state = self.regime_detector.classify(df_1h)

        # Log regime change
        if self._last_regime and self._last_regime != regime_state.regime:
            trade_logger.log_regime_change(
                self._last_regime, regime_state.regime, regime_state.factors
            )
            await self.telegram.send_regime_change(
                self._last_regime, regime_state.regime, regime_state.factors
            )
        self._last_regime = regime_state.regime

        # Step 2: Check kill zone
        is_active_zone, is_watch_zone, zone_name = self._check_kill_zone()

        if not is_active_zone and not is_watch_zone:
            return  # Dead zone — no trading

        # Step 3: Check if we can trade (risk limits)
        can_trade, reason = self.risk_manager.can_trade()
        if not can_trade:
            logger.debug(f"Cannot trade: {reason}")
            return

        # Step 4: Don't trade in DEAD regime
        if regime_state.regime == Regime.DEAD:
            return

        # Step 5: Select strategy for current regime
        strategy = self.strategy_selector.select(regime_state.regime)

        # Step 6: Calculate indicators
        indicators = calculate_all_regime_indicators(df_1h, self.config)
        self.last_indicators = indicators

        # Step 7: Generate signal from strategy
        signal = strategy.generate_signal(df_1h, indicators, current_price)
        self.last_signal = signal
        if signal is None:
            return  # No trade setup

        # Step 8: Detect behavioral patterns
        support_levels = self.market_memory.get_support_levels(current_price)
        resistance_levels = self.market_memory.get_resistance_levels(current_price)

        behavioral_signals = self.behavioral.detect_all(
            df_1h,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            funding_rate=self._current_funding_rate,
        )
        self.last_behavioral_signals = behavioral_signals

        # Find matching behavioral signal
        best_behavioral = None
        for bs in behavioral_signals:
            if bs.direction == signal.direction:
                if best_behavioral is None or bs.strength > best_behavioral.strength:
                    best_behavioral = bs

        # Step 9: Calculate confidence score
        ob_support = self.order_book.get_support_score()
        funding_favorable = 0.5  # neutral default
        if self._current_funding_rate is not None:
            if signal.direction == "long" and self._current_funding_rate < 0:
                funding_favorable = min(1.0, abs(self._current_funding_rate) / 0.001)
            elif signal.direction == "short" and self._current_funding_rate > 0:
                funding_favorable = min(1.0, abs(self._current_funding_rate) / 0.001)

        vol_confirmed = False
        if 'volume_spike' in indicators:
            vol_confirmed = float(indicators['volume_spike'].iloc[-1]) > 1.0

        confidence_result = self.confidence.score(
            regime_aligned=True,
            regime_clear=regime_state.regime != Regime.TRANSITION,
            behavioral_pattern=best_behavioral.pattern if best_behavioral else None,
            behavioral_strength=best_behavioral.strength if best_behavioral else 0,
            whale_confirmed=None,  # Phase 3
            order_book_support=ob_support if signal.direction == "long" else (1 - ob_support),
            funding_favorable=funding_favorable,
            volume_confirmed=vol_confirmed,
            is_watch_zone=is_watch_zone,
            regime=regime_state.regime,
        )
        self.last_confidence_result = confidence_result

        trade_logger.log_confidence_score(
            confidence_result.total_score,
            confidence_result.breakdown,
            confidence_result.action,
        )

        if not confidence_result.should_trade:
            return

        # Step 10: AI Advisor review (optional)
        if self.ai_advisor.enabled:
            review = await self.ai_advisor.review_trade(
                direction=signal.direction,
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                regime=regime_state.regime,
                confidence_score=confidence_result.total_score,
                score_breakdown=confidence_result.breakdown,
                behavioral_pattern=best_behavioral.pattern if best_behavioral else "",
            )
            if not review['approved']:
                logger.info(f"AI Advisor rejected trade: {review['reasoning']}")
                return

        # Step 11: Calculate position size
        equity = self.paper_trader.equity if self.config.is_paper_trading() else 3650
        position = self.risk_manager.calculate_position_size(
            equity=equity,
            risk_pct=confidence_result.position_risk_pct,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            regime=regime_state.regime,
        )

        if position.position_usd <= 0:
            return

        # Step 12: Execute trade
        if self.config.is_paper_trading():
            self.paper_trader.open_position(
                symbol=self.config.system.symbol,
                direction=signal.direction,
                entry_price=signal.entry_price,
                position_size_usd=position.position_usd,
                leverage=position.leverage,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                regime=regime_state.regime,
                strategy=signal.strategy_name,
                confidence_score=confidence_result.total_score,
                score_breakdown=confidence_result.breakdown,
                behavioral_pattern=best_behavioral.pattern if best_behavioral else "",
                kill_zone=zone_name,
            )
            self.risk_manager.record_position_opened()

        # Step 13: Journal entry
        if self.journal:
            self.journal.record_entry(
                symbol=self.config.system.symbol,
                direction=signal.direction,
                entry_price=signal.entry_price,
                position_size=position.position_usd,
                leverage=position.leverage,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                regime=regime_state.regime,
                strategy=signal.strategy_name,
                confidence_score=confidence_result.total_score,
                score_breakdown=confidence_result.breakdown,
                behavioral_pattern=best_behavioral.pattern if best_behavioral else "",
                kill_zone=zone_name,
                is_paper=self.config.is_paper_trading(),
            )

        # Step 14: Telegram alert
        await self.telegram.send_trade_alert({
            'trade_id': 'latest',
            'direction': signal.direction,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'confidence_score': confidence_result.total_score,
            'regime': regime_state.regime,
        }, action="OPEN")

        # Step 15: Update market memory
        self.market_memory.update_from_candles(df_1h, regime_state.regime)

        # Step 16: Check paper positions against current price
        if self.config.is_paper_trading() and self._ticker_price:
            closed = self.paper_trader.check_positions(self._ticker_price)
            for trade_result in closed:
                self.risk_manager.record_trade_result(trade_result['net_pnl'])
                await self.telegram.send_trade_alert(trade_result, action="CLOSE")

    def _check_kill_zone(self) -> tuple[bool, bool, str]:
        """
        Check if current UTC time is in an active or watch-only kill zone.
        Returns (is_active, is_watch_only, zone_name).
        """
        now = datetime.now(timezone.utc)
        current_time = now.strftime("%H:%M")

        for zone in self.config.kill_zones.active:
            if zone.start <= current_time < zone.end:
                return True, False, zone.name

        for zone in self.config.kill_zones.watch_only:
            if zone.start <= current_time < zone.end:
                return False, True, zone.name

        # Check for liquidation cascade exception — trade in any zone
        # (This would be triggered by behavioral detector)

        return False, False, "dead_zone"

    async def _health_monitor(self):
        """Periodic health checks and maintenance tasks."""
        while self.running:
            try:
                # Check data freshness
                data_age = self.risk_manager.get_status()['data_age_seconds']
                if data_age > self.config.risk.stale_data_timeout_seconds:
                    logger.warning(f"Stale data: {data_age:.0f}s")

                # Periodic funding rate update
                if self.bitget_client.session:
                    self._current_funding_rate = await self.bitget_client.get_funding_rate()

                # Check for new day (reset daily counters)
                now = datetime.now(timezone.utc)
                if now.hour == 0 and now.minute < 2:
                    equity = self.paper_trader.equity if self.config.is_paper_trading() else 3650
                    self.risk_manager.new_day_reset(equity)

                    # Send daily summary
                    stats = self.paper_trader.get_stats()
                    await self.telegram.send_daily_summary(stats)

            except Exception as e:
                logger.error(f"Health monitor error: {e}", exc_info=True)

            await asyncio.sleep(60)  # Check every minute

    async def stop(self):
        """Gracefully stop all components."""
        logger.info("Stopping Khufra Engine...")
        self.running = False

        # Close all paper positions
        if self.config.is_paper_trading() and self._ticker_price:
            self.paper_trader.force_close_all(self._ticker_price, "shutdown")

        # Disconnect
        await self.ws.disconnect()
        if self.bitget_client.session:
            await self.bitget_client.disconnect()
        await self.telegram.stop()
        await self.db.disconnect()

        # Final stats
        stats = self.paper_trader.get_stats()
        logger.info(f"Final stats: {stats}")
        logger.info("Khufra Engine stopped")

    async def kill_switch(self):
        """Emergency: close all positions and halt."""
        logger.critical("KILL SWITCH ACTIVATED")
        if self.config.is_paper_trading():
            if self._ticker_price:
                self.paper_trader.force_close_all(self._ticker_price, "kill_switch")
        else:
            await self.bitget_client.close_all_positions()

        self.risk_manager.halt_trading("Kill switch activated")
        await self.telegram.send_emergency("Kill switch activated — all positions closed")

"""
Project Khufra AI - Main Entry Point
Automated Crypto Trading Bot

Authors: Ujjwal Adhikari (Technical Lead) & Anjing Khadka (Strategy Lead)
Version: 0.1.0
Date: January 16, 2026
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.utils.logger import setup_logger, get_logger
from src.database.connection import DatabaseManager


# Initialize logger
logger = get_logger(__name__)


class KhufraAI:
    """
    Main orchestrator for the Khufra AI trading bot.
    Coordinates all modules: news monitoring, TradingView signals, AI decisions, and trade execution.
    """

    def __init__(self):
        """Initialize the Khufra AI bot."""
        self.running = False
        self.db_manager = None

        # Module placeholders (to be implemented in future phases)
        self.news_monitor = None
        self.tradingview_handler = None
        self.exchange_client = None
        self.ai_engine = None
        self.risk_manager = None
        self.notifier = None

        logger.info("=" * 60)
        logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}")
        logger.info("=" * 60)

    async def initialize(self):
        """Initialize all components and connections."""
        try:
            logger.info("Phase 1: Initializing bot components...")

            # Validate critical settings
            missing_settings = settings.validate_critical_settings()
            if missing_settings:
                logger.warning(f"Missing settings: {', '.join(missing_settings)}")
                logger.warning("Some features may not work. Check your .env file.")

            # Initialize database
            logger.info("Connecting to database...")
            self.db_manager = DatabaseManager(settings.DATABASE_URL)
            await self.db_manager.connect()
            logger.info("✓ Database connected successfully")

            # Display current configuration
            self._display_configuration()

            # TODO: Phase 2 - Initialize news monitor
            # TODO: Phase 3 - Initialize TradingView handler
            # TODO: Phase 4 - Initialize exchange client
            # TODO: Phase 5 - Initialize AI engine
            # TODO: Phase 6 - Initialize risk manager
            # TODO: Initialize notification system

            logger.info("✓ All components initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}", exc_info=True)
            return False

    def _display_configuration(self):
        """Display current bot configuration."""
        logger.info("-" * 60)
        logger.info("CURRENT CONFIGURATION:")
        logger.info(f"  Environment: {settings.ENVIRONMENT}")
        logger.info(f"  Trading Mode: {settings.TRADING_MODE.upper()}")
        logger.info(f"  Paper Trading: {settings.is_paper_trading()}")
        logger.info(f"  AI Decisions: {'Enabled' if settings.ENABLE_AI_DECISIONS else 'Disabled'}")
        logger.info(f"  News Monitoring: {'Enabled' if settings.ENABLE_NEWS_MONITORING else 'Disabled'}")
        logger.info(f"  TradingView Signals: {'Enabled' if settings.ENABLE_TRADINGVIEW_SIGNALS else 'Disabled'}")
        logger.info(f"  Max Risk/Trade: {settings.MAX_RISK_PER_TRADE * 100}%")
        logger.info(f"  Max Concurrent Positions: {settings.MAX_CONCURRENT_POSITIONS}")
        logger.info(f"  Daily Loss Limit: {settings.DAILY_LOSS_LIMIT * 100}%")
        logger.info("-" * 60)

        # Safety warnings
        if not settings.is_paper_trading():
            logger.warning("⚠️  LIVE TRADING MODE IS ACTIVE!")
            logger.warning("⚠️  Real money will be at risk!")

    async def start(self):
        """Start the bot and begin monitoring/trading."""
        if not await self.initialize():
            logger.error("Failed to initialize. Exiting.")
            return

        self.running = True
        logger.info("=" * 60)
        logger.info(f"{settings.PROJECT_NAME} is now running!")
        logger.info(f"Trading Mode: {settings.TRADING_MODE.upper()}")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        try:
            # Main event loop
            while self.running:
                await self._main_loop()
                await asyncio.sleep(1)  # Prevent busy waiting

        except KeyboardInterrupt:
            logger.info("\nReceived shutdown signal...")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        finally:
            await self.shutdown()

    async def _main_loop(self):
        """
        Main event loop - executes continuously while bot is running.
        This is where the magic happens!
        """
        # TODO: Phase 2 - Check for news updates
        # TODO: Phase 3 - Check for TradingView signals
        # TODO: Phase 4 - Check open positions
        # TODO: Phase 5 - Run AI analysis
        # TODO: Phase 6 - Apply risk management checks
        # TODO: Execute trades if conditions are met

        # For now, just a placeholder
        await asyncio.sleep(10)

    async def shutdown(self):
        """Gracefully shutdown the bot."""
        logger.info("Shutting down Khufra AI...")
        self.running = False

        try:
            # Close all connections
            if self.db_manager:
                await self.db_manager.disconnect()
                logger.info("✓ Database disconnected")

            # TODO: Close exchange connections
            # TODO: Save final state
            # TODO: Send shutdown notification

            logger.info("=" * 60)
            logger.info("Khufra AI has been shut down successfully")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)

    def handle_signal(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        logger.info(f"\nReceived signal {signum}")
        self.running = False


def main():
    """Main entry point."""
    # Setup logging
    setup_logger(
        log_level=settings.LOG_LEVEL,
        log_dir=settings.LOG_DIR
    )

    logger.info("Starting Khufra AI...")

    # Display welcome message
    print(f"\n{'=' * 60}")
    print(f"  {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"  Developed by: Ujjwal Adhikari & Anjing Khadka")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  Trading Mode: {settings.TRADING_MODE.upper()}")
    print(f"{'=' * 60}\n")

    # Safety check for live trading
    if not settings.is_paper_trading():
        print("⚠️  WARNING: LIVE TRADING MODE DETECTED!")
        print("⚠️  Real money will be at risk!")
        confirmation = input("\nType 'YES I UNDERSTAND' to continue: ")
        if confirmation != "YES I UNDERSTAND":
            print("Live trading cancelled. Exiting for safety.")
            sys.exit(0)

    # Create and run bot
    bot = KhufraAI()

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, bot.handle_signal)
    signal.signal(signal.SIGTERM, bot.handle_signal)

    # Run the bot
    try:
        asyncio.run(bot.start())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

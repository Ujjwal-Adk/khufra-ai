"""
Khufra Trading System v2.0 - Entry Point
Adaptive Multi-Edge Cryptocurrency Trading System

Built by Ujjwal Adhikari
Capital: $5,000 CAD | Primary: BTC/USDT Perps | Exchange: Bitget
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import config
from core.logger import setup_logger, get_logger
from core.engine import KhufraEngine


def main():
    """Main entry point."""
    # Setup logging
    config.log_dir.mkdir(parents=True, exist_ok=True)
    setup_logger(
        log_level=config.system.log_level,
        log_dir=config.log_dir,
    )

    logger = get_logger(__name__)

    # Welcome banner
    print(f"\n{'='*60}")
    print(f"  KHUFRA TRADING SYSTEM v2.0")
    print(f"  Mode: {config.system.mode.upper()}")
    print(f"  Symbol: {config.system.symbol}")
    print(f"  Exchange: {config.system.exchange}")
    print(f"{'='*60}\n")

    # Safety check for live trading
    if config.is_live_trading():
        print("WARNING: LIVE TRADING MODE!")
        print("Real money will be at risk!")
        confirmation = input("\nType 'YES I UNDERSTAND' to continue: ")
        if confirmation != "YES I UNDERSTAND":
            print("Cancelled. Exiting.")
            sys.exit(0)

    # Create engine
    engine = KhufraEngine(config)

    # Signal handlers
    def handle_shutdown(signum, frame):
        logger.info(f"Received signal {signum}")
        engine.running = False

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Run
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        logger.info("Interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

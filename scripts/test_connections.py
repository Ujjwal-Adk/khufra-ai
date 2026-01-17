"""
Project Khufra AI - Connection Test Script
Tests all external connections (APIs, exchanges, database).
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.utils.logger import setup_logger, get_logger

# Setup logging
setup_logger(log_level="INFO")
logger = get_logger(__name__)


def print_header(message: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def print_test(test_name: str):
    """Print test name."""
    print(f"Testing: {test_name}... ", end="", flush=True)


def print_result(success: bool, message: str = ""):
    """Print test result."""
    if success:
        print(f"✅ PASS {message}")
    else:
        print(f"❌ FAIL {message}")


async def test_database_connection():
    """Test database connection."""
    print_test("Database Connection")

    try:
        from src.database.connection import DatabaseManager

        db_manager = DatabaseManager(settings.DATABASE_URL)
        await db_manager.connect()

        # Test health check
        if db_manager.health_check():
            await db_manager.disconnect()
            print_result(True, f"({settings.DATABASE_URL.split('://')[0]})")
            return True
        else:
            await db_manager.disconnect()
            print_result(False, "Health check failed")
            return False

    except Exception as e:
        print_result(False, f"({str(e)})")
        return False


async def test_anthropic_api():
    """Test Anthropic/Claude API connection."""
    print_test("Claude AI API")

    if not settings.ANTHROPIC_API_KEY:
        print_result(False, "(API key not configured)")
        return False

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Simple test - just check if client initializes
        # Actual API call would consume credits
        print_result(True, "(API key configured)")
        return True

    except Exception as e:
        print_result(False, f"({str(e)})")
        return False


async def test_exchange_connection():
    """Test exchange API connection."""
    print_test("Exchange API (Bitget)")

    if not settings.BITGET_API_KEY:
        print_result(False, "(API key not configured)")
        return False

    try:
        import ccxt

        exchange = ccxt.bitget({
            'apiKey': settings.BITGET_API_KEY,
            'secret': settings.BITGET_API_SECRET,
            'password': settings.BITGET_API_PASSWORD,
            'enableRateLimit': True,
        })

        # Test connection by fetching ticker (doesn't require auth)
        ticker = exchange.fetch_ticker('BTC/USDT')

        if ticker:
            print_result(True, f"(Price: ${ticker['last']:.2f})")
            return True
        else:
            print_result(False, "No ticker data")
            return False

    except Exception as e:
        print_result(False, f"({str(e)[:50]}...)")
        return False


async def test_telegram_bot():
    """Test Telegram bot connection."""
    print_test("Telegram Bot")

    if not settings.TELEGRAM_BOT_TOKEN:
        print_result(False, "(Bot token not configured)")
        return False

    try:
        from telegram import Bot

        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        # Test by getting bot info
        bot_info = await bot.get_me()

        if bot_info:
            print_result(True, f"(@{bot_info.username})")
            return True
        else:
            print_result(False, "Could not get bot info")
            return False

    except Exception as e:
        print_result(False, f"({str(e)[:50]}...)")
        return False


async def test_news_api():
    """Test News API connection."""
    print_test("News API")

    if not settings.NEWS_API_KEY:
        print_result(False, "(API key not configured)")
        return False

    try:
        import requests

        url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={settings.NEWS_API_KEY}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            article_count = len(data.get('articles', []))
            print_result(True, f"({article_count} articles fetched)")
            return True
        else:
            print_result(False, f"(HTTP {response.status_code})")
            return False

    except Exception as e:
        print_result(False, f"({str(e)[:50]}...)")
        return False


async def main():
    """Main test function."""
    print_header("PROJECT KHUFRA AI - CONNECTION TESTS")

    print("This script tests all external connections.\n")
    print("Configured features:")
    print(f"  - AI Decisions: {settings.ENABLE_AI_DECISIONS}")
    print(f"  - News Monitoring: {settings.ENABLE_NEWS_MONITORING}")
    print(f"  - TradingView Signals: {settings.ENABLE_TRADINGVIEW_SIGNALS}")
    print(f"  - Telegram Notifications: {settings.ENABLE_TELEGRAM_NOTIFICATIONS}")
    print(f"  - Trading Mode: {settings.TRADING_MODE.upper()}\n")

    # Run tests
    results = {}

    # Critical tests (always run)
    results['Database'] = await test_database_connection()

    # Optional tests (based on configuration)
    if settings.ENABLE_AI_DECISIONS:
        results['Claude AI'] = await test_anthropic_api()

    if not settings.is_paper_trading():
        results['Exchange'] = await test_exchange_connection()
    else:
        print_test("Exchange API (Paper Trading Mode)")
        print_result(True, "(Skipped - using paper trading)")
        results['Exchange'] = True

    if settings.ENABLE_TELEGRAM_NOTIFICATIONS:
        results['Telegram'] = await test_telegram_bot()

    if settings.ENABLE_NEWS_MONITORING:
        results['News API'] = await test_news_api()

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed

    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print()

    if failed == 0:
        print("🎉 All tests passed! Your bot is ready to run.\n")
        print("Next steps:")
        print("  1. Review your configuration in .env")
        print("  2. Start the bot: python main.py")
        print()
        return 0
    else:
        print("⚠️  Some tests failed. Please check your configuration.\n")
        print("Failed tests:")
        for test_name, result in results.items():
            if not result:
                print(f"  - {test_name}")
        print()
        print("Tips:")
        print("  - Check your .env file for correct API keys")
        print("  - Ensure services are accessible from your network")
        print("  - Review docs/troubleshooting.md for common issues")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

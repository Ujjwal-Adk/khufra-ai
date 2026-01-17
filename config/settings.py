"""
Project Khufra AI - Central Configuration Settings
All configuration settings are managed here.
"""

import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Central configuration class for Project Khufra AI.
    All settings are loaded from environment variables with sensible defaults.
    """

    # ============================================
    # PROJECT INFO
    # ============================================
    PROJECT_NAME: str = "Project Khufra AI"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "testing", "production"] = Field(
        default="development",
        description="Current environment"
    )

    # ============================================
    # TRADING MODE
    # ============================================
    TRADING_MODE: Literal["paper", "live"] = Field(
        default="paper",
        description="Trading mode - ALWAYS start with paper!"
    )

    # ============================================
    # DATABASE
    # ============================================
    DATABASE_URL: str = Field(
        default=f"sqlite:///{BASE_DIR}/data/trades.db",
        description="Database connection URL"
    )

    # ============================================
    # EXCHANGE API CREDENTIALS
    # ============================================
    BITGET_API_KEY: str = Field(default="", description="Bitget API Key")
    BITGET_API_SECRET: str = Field(default="", description="Bitget API Secret")
    BITGET_API_PASSWORD: str = Field(default="", description="Bitget API Password")

    BINANCE_API_KEY: str = Field(default="", description="Binance API Key (optional)")
    BINANCE_API_SECRET: str = Field(default="", description="Binance API Secret (optional)")

    # ============================================
    # AI INTEGRATION
    # ============================================
    ANTHROPIC_API_KEY: str = Field(default="", description="Claude AI API Key")
    ANTHROPIC_MODEL: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Claude model to use"
    )

    # ============================================
    # NOTIFICATIONS
    # ============================================
    TELEGRAM_BOT_TOKEN: str = Field(default="", description="Telegram Bot Token")
    TELEGRAM_CHAT_ID_UJJWAL: str = Field(default="", description="Ujjwal's Telegram Chat ID")
    TELEGRAM_CHAT_ID_ANJING: str = Field(default="", description="Anjing's Telegram Chat ID")
    DISCORD_WEBHOOK_URL: str = Field(default="", description="Discord Webhook URL (optional)")

    ENABLE_TELEGRAM_NOTIFICATIONS: bool = Field(default=True, description="Enable Telegram alerts")
    ENABLE_DISCORD_NOTIFICATIONS: bool = Field(default=False, description="Enable Discord alerts")

    # ============================================
    # NEWS APIS
    # ============================================
    NEWS_API_KEY: str = Field(default="", description="NewsAPI.org key")
    ALPHA_VANTAGE_API_KEY: str = Field(default="", description="Alpha Vantage key")
    ENABLE_NEWS_MONITORING: bool = Field(default=True, description="Enable news monitoring")

    # ============================================
    # TRADINGVIEW
    # ============================================
    TRADINGVIEW_WEBHOOK_SECRET: str = Field(default="", description="TradingView webhook secret")
    ENABLE_TRADINGVIEW_SIGNALS: bool = Field(default=True, description="Enable TradingView signals")

    # ============================================
    # RISK MANAGEMENT
    # ============================================
    MAX_RISK_PER_TRADE: float = Field(
        default=0.02,
        ge=0.001,
        le=0.05,
        description="Maximum risk per trade (1-5%)"
    )
    DAILY_LOSS_LIMIT: float = Field(
        default=0.05,
        ge=0.01,
        le=0.20,
        description="Daily loss limit (1-20%)"
    )
    MONTHLY_LOSS_LIMIT: float = Field(
        default=0.15,
        ge=0.05,
        le=0.50,
        description="Monthly loss limit (5-50%)"
    )
    MAX_CONCURRENT_POSITIONS: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum concurrent positions"
    )
    STOP_AFTER_CONSECUTIVE_LOSSES: int = Field(
        default=3,
        ge=2,
        le=10,
        description="Stop trading after N consecutive losses"
    )

    # ============================================
    # LOGGING
    # ============================================
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_DIR: Path = Field(default=BASE_DIR / "data" / "logs", description="Log directory")

    # ============================================
    # SECURITY
    # ============================================
    SECRET_KEY: str = Field(
        default="",
        description="Secret key for encryption (generate securely!)"
    )

    # ============================================
    # API RATE LIMITING
    # ============================================
    API_RATE_LIMIT: int = Field(
        default=60,
        ge=10,
        le=1000,
        description="API rate limit (requests per minute)"
    )

    # ============================================
    # TIMEZONE
    # ============================================
    TIMEZONE: str = Field(default="America/Edmonton", description="Timezone for logging")

    # ============================================
    # FEATURE FLAGS
    # ============================================
    ENABLE_AI_DECISIONS: bool = Field(default=True, description="Enable AI decision-making")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @validator("TRADING_MODE")
    def validate_trading_mode(cls, v):
        """Ensure we start with paper trading."""
        if v == "live":
            print("⚠️  WARNING: Live trading mode enabled! Make sure you know what you're doing!")
        return v

    @validator("LOG_DIR", pre=True)
    def create_log_dir(cls, v):
        """Create log directory if it doesn't exist."""
        log_path = Path(v) if isinstance(v, str) else v
        log_path.mkdir(parents=True, exist_ok=True)
        return log_path

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"

    def is_paper_trading(self) -> bool:
        """Check if in paper trading mode."""
        return self.TRADING_MODE == "paper"

    def get_exchange_credentials(self, exchange: str = "bitget") -> dict:
        """Get exchange API credentials."""
        if exchange.lower() == "bitget":
            return {
                "apiKey": self.BITGET_API_KEY,
                "secret": self.BITGET_API_SECRET,
                "password": self.BITGET_API_PASSWORD,
            }
        elif exchange.lower() == "binance":
            return {
                "apiKey": self.BINANCE_API_KEY,
                "secret": self.BINANCE_API_SECRET,
            }
        else:
            raise ValueError(f"Unknown exchange: {exchange}")

    def validate_critical_settings(self) -> list[str]:
        """
        Validate critical settings and return list of missing configurations.
        Returns empty list if all critical settings are present.
        """
        missing = []

        # Check exchange credentials (only if not paper trading)
        if not self.is_paper_trading():
            if not self.BITGET_API_KEY:
                missing.append("BITGET_API_KEY")
            if not self.BITGET_API_SECRET:
                missing.append("BITGET_API_SECRET")
            if not self.BITGET_API_PASSWORD:
                missing.append("BITGET_API_PASSWORD")

        # Check AI integration
        if self.ENABLE_AI_DECISIONS and not self.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")

        # Check notifications
        if self.ENABLE_TELEGRAM_NOTIFICATIONS:
            if not self.TELEGRAM_BOT_TOKEN:
                missing.append("TELEGRAM_BOT_TOKEN")
            if not self.TELEGRAM_CHAT_ID_UJJWAL:
                missing.append("TELEGRAM_CHAT_ID_UJJWAL")
            if not self.TELEGRAM_CHAT_ID_ANJING:
                missing.append("TELEGRAM_CHAT_ID_ANJING")

        return missing


# Global settings instance
settings = Settings()


# Validate settings on import
if __name__ != "__main__":
    missing_settings = settings.validate_critical_settings()
    if missing_settings:
        print(f"⚠️  Warning: Missing critical settings: {', '.join(missing_settings)}")
        print("Please check your .env file and ensure all required variables are set.")

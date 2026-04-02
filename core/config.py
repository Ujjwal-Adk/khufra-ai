"""
Khufra Trading System - Configuration Loader
Loads settings from YAML config + .env secrets.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Try root .env first (monorepo), then local
_root_env = BASE_DIR.parent.parent / '.env'
if _root_env.exists():
    load_dotenv(_root_env)
load_dotenv()  # local fallback


@dataclass
class SystemConfig:
    mode: str = "paper"
    symbol: str = "BTCUSDT"
    exchange: str = "bitget"
    log_level: str = "INFO"
    timezone: str = "America/Edmonton"


@dataclass
class RegimeConfig:
    adx_trending_threshold: float = 25
    adx_ranging_threshold: float = 20
    atr_volatile_multiplier: float = 1.5
    atr_dead_multiplier: float = 0.5
    bb_squeeze_percentile: float = 10
    ema_fast: int = 21
    ema_slow: int = 50
    confirmation_candles: int = 3
    primary_timeframe: str = "1h"
    confirmation_timeframe: str = "15m"


@dataclass
class ConfidenceWeights:
    regime_alignment: int = 20
    behavioral_pattern: int = 25
    whale_onchain: int = 20
    order_book: int = 15
    funding_rate: int = 10
    volume: int = 10


@dataclass
class ConfidenceConfig:
    min_score_to_trade: int = 65
    min_score_watch_zone: int = 80
    weights: ConfidenceWeights = field(default_factory=ConfidenceWeights)


@dataclass
class RiskConfig:
    base_risk_pct: float = 0.02
    max_risk_pct: float = 0.04
    max_daily_drawdown: float = 0.05
    max_leverage: int = 5
    max_concurrent_positions: int = 2
    stale_data_timeout_seconds: int = 30
    error_circuit_breaker: int = 3
    stop_after_consecutive_losses: int = 3
    confidence_multipliers: dict = field(default_factory=lambda: {
        "conservative": 0.6, "standard": 1.0, "high_conviction": 1.75
    })
    regime_multipliers: dict = field(default_factory=lambda: {
        "trending_up": 1.0, "trending_down": 1.0, "ranging": 0.8,
        "volatile": 0.5, "transition": 0.5, "dead": 0.0
    })


@dataclass
class KillZone:
    name: str
    start: str
    end: str


@dataclass
class KillZonesConfig:
    active: list = field(default_factory=list)
    watch_only: list = field(default_factory=list)


@dataclass
class StopHuntConfig:
    min_volume_spike: float = 3.0
    max_reclaim_candles: int = 3
    min_break_pct: float = 0.003


@dataclass
class LiquidationCascadeConfig:
    min_oi_drop_pct: float = 0.03
    min_liquidation_volume: float = 10_000_000


@dataclass
class FomoTrapConfig:
    no_followthrough_candles: int = 3
    volume_decline_pct: float = 0.4


@dataclass
class FundingExtremeConfig:
    bullish_crowd_threshold: float = 0.0005
    bearish_crowd_threshold: float = -0.0005


@dataclass
class BehavioralConfig:
    stop_hunt: StopHuntConfig = field(default_factory=StopHuntConfig)
    liquidation_cascade: LiquidationCascadeConfig = field(default_factory=LiquidationCascadeConfig)
    fomo_trap: FomoTrapConfig = field(default_factory=FomoTrapConfig)
    funding_extreme: FundingExtremeConfig = field(default_factory=FundingExtremeConfig)


@dataclass
class MarketMemoryConfig:
    rolling_window_days: int = 7
    decay_halflife_days: int = 7
    purge_after_days: int = 30
    min_significance: float = 0.2


@dataclass
class LearningLoopConfig:
    schedule: str = "sunday_00:00_utc"
    auto_apply: bool = False
    min_trades_for_analysis: int = 20


@dataclass
class AIAdvisorConfig:
    enabled: bool = False
    model: str = "claude-sonnet-4-6-20250514"
    max_tokens: int = 1024
    confirm_above_score: int = 75


@dataclass
class SecretsConfig:
    """Loaded from .env — never in YAML."""
    bitget_api_key: str = ""
    bitget_api_secret: str = ""
    bitget_passphrase: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    anthropic_api_key: str = ""
    whale_alert_api_key: str = ""
    glassnode_api_key: str = ""


class KhufraConfig:
    """Main configuration class. Loads YAML + .env."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = BASE_DIR / "config" / "settings.yaml"

        self.config_path = Path(config_path)
        self._raw = self._load_yaml()

        self.system = self._build_system()
        self.regime = self._build_regime()
        self.confidence = self._build_confidence()
        self.risk = self._build_risk()
        self.kill_zones = self._build_kill_zones()
        self.behavioral = self._build_behavioral()
        self.market_memory = self._build_market_memory()
        self.learning_loop = self._build_learning_loop()
        self.ai_advisor = self._build_ai_advisor()
        self.secrets = self._load_secrets()

    def _load_yaml(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _get(self, *keys, default=None):
        """Safely get nested config value."""
        data = self._raw
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, default)
            else:
                return default
        return data if data is not None else default

    def _build_system(self) -> SystemConfig:
        s = self._get('system') or {}
        return SystemConfig(**{k: s.get(k, getattr(SystemConfig, k, None))
                              for k in SystemConfig.__dataclass_fields__
                              if k in s})

    def _build_regime(self) -> RegimeConfig:
        r = self._get('regime') or {}
        return RegimeConfig(**{k: r[k] for k in RegimeConfig.__dataclass_fields__ if k in r})

    def _build_confidence(self) -> ConfidenceConfig:
        c = self._get('confidence') or {}
        weights_raw = c.get('weights', {})
        weights = ConfidenceWeights(**{k: weights_raw[k] for k in ConfidenceWeights.__dataclass_fields__
                                      if k in weights_raw})
        return ConfidenceConfig(
            min_score_to_trade=c.get('min_score_to_trade', 65),
            min_score_watch_zone=c.get('min_score_watch_zone', 80),
            weights=weights
        )

    def _build_risk(self) -> RiskConfig:
        r = self._get('risk') or {}
        return RiskConfig(
            base_risk_pct=r.get('base_risk_pct', 0.02),
            max_risk_pct=r.get('max_risk_pct', 0.04),
            max_daily_drawdown=r.get('max_daily_drawdown', 0.05),
            max_leverage=r.get('max_leverage', 5),
            max_concurrent_positions=r.get('max_concurrent_positions', 2),
            stale_data_timeout_seconds=r.get('stale_data_timeout_seconds', 30),
            error_circuit_breaker=r.get('error_circuit_breaker', 3),
            stop_after_consecutive_losses=r.get('stop_after_consecutive_losses', 3),
            confidence_multipliers=r.get('confidence_multipliers', {}),
            regime_multipliers=r.get('regime_multipliers', {}),
        )

    def _build_kill_zones(self) -> KillZonesConfig:
        kz = self._get('kill_zones') or {}
        active = [KillZone(**z) for z in kz.get('active', [])]
        watch = [KillZone(**z) for z in kz.get('watch_only', [])]
        return KillZonesConfig(active=active, watch_only=watch)

    def _build_behavioral(self) -> BehavioralConfig:
        b = self._get('behavioral') or {}
        return BehavioralConfig(
            stop_hunt=StopHuntConfig(**b.get('stop_hunt', {})),
            liquidation_cascade=LiquidationCascadeConfig(**b.get('liquidation_cascade', {})),
            fomo_trap=FomoTrapConfig(**b.get('fomo_trap', {})),
            funding_extreme=FundingExtremeConfig(**b.get('funding_extreme', {})),
        )

    def _build_market_memory(self) -> MarketMemoryConfig:
        m = self._get('market_memory') or {}
        return MarketMemoryConfig(**{k: m[k] for k in MarketMemoryConfig.__dataclass_fields__ if k in m})

    def _build_learning_loop(self) -> LearningLoopConfig:
        ll = self._get('learning_loop') or {}
        return LearningLoopConfig(**{k: ll[k] for k in LearningLoopConfig.__dataclass_fields__ if k in ll})

    def _build_ai_advisor(self) -> AIAdvisorConfig:
        ai = self._get('ai_advisor') or {}
        return AIAdvisorConfig(**{k: ai[k] for k in AIAdvisorConfig.__dataclass_fields__ if k in ai})

    def _load_secrets(self) -> SecretsConfig:
        return SecretsConfig(
            bitget_api_key=os.getenv("BITGET_API_KEY", ""),
            bitget_api_secret=os.getenv("BITGET_API_SECRET", ""),
            bitget_passphrase=os.getenv("BITGET_PASSPHRASE", ""),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            whale_alert_api_key=os.getenv("WHALE_ALERT_API_KEY", ""),
            glassnode_api_key=os.getenv("GLASSNODE_API_KEY", ""),
        )

    def is_paper_trading(self) -> bool:
        return self.system.mode == "paper"

    def is_live_trading(self) -> bool:
        return self.system.mode == "live"

    def validate(self) -> list[str]:
        """Return list of missing critical settings."""
        missing = []
        if self.is_live_trading():
            if not self.secrets.bitget_api_key:
                missing.append("BITGET_API_KEY")
            if not self.secrets.bitget_api_secret:
                missing.append("BITGET_API_SECRET")
            if not self.secrets.bitget_passphrase:
                missing.append("BITGET_PASSPHRASE")
        if self.ai_advisor.enabled and not self.secrets.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        return missing

    @property
    def database_url(self) -> str:
        return os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data_store' / 'trades.db'}")

    @property
    def log_dir(self) -> Path:
        return BASE_DIR / "data_store" / "logs"


# Global config instance
config = KhufraConfig()

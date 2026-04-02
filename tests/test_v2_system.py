"""Quick verification test for Khufra V2 system."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np

def test_all():
    # 1. Config
    from core.config import config
    print("Config loaded OK")
    print(f"  Mode: {config.system.mode}")
    print(f"  Symbol: {config.system.symbol}")
    print(f"  ADX threshold: {config.regime.adx_trending_threshold}")
    print(f"  Min score: {config.confidence.min_score_to_trade}")
    print(f"  Max risk: {config.risk.max_risk_pct}")
    print(f"  Kill zones: {len(config.kill_zones.active)} active, {len(config.kill_zones.watch_only)} watch")
    print(f"  Paper trading: {config.is_paper_trading()}")
    print()

    # 2. Indicators
    from data.indicators import calculate_adx, calculate_atr, calculate_ema, calculate_bollinger_bands

    np.random.seed(42)
    n = 100
    close = 90000 + np.cumsum(np.random.randn(n) * 100)
    high = close + np.abs(np.random.randn(n) * 50)
    low = close - np.abs(np.random.randn(n) * 50)
    volume = np.random.randint(100, 1000, n).astype(float)
    df = pd.DataFrame({
        "open": close + np.random.randn(n) * 20,
        "high": high, "low": low, "close": close, "volume": volume
    })

    adx = calculate_adx(df)
    atr = calculate_atr(df)
    ema21 = calculate_ema(df["close"], 21)
    bb = calculate_bollinger_bands(df)
    print("Indicators OK")
    print(f"  ADX: {adx.iloc[-1]:.2f}")
    print(f"  ATR: {atr.iloc[-1]:.2f}")
    print(f"  EMA21: {ema21.iloc[-1]:.2f}")
    print(f"  BB width: {bb['width'].iloc[-1]:.2f}")
    print()

    # 3. Regime Detector
    from brain.regime_detector import RegimeDetector
    detector = RegimeDetector(config)
    state = detector.classify(df)
    print("Regime detection OK")
    print(f"  Regime: {state.regime}")
    print(f"  Confidence: {state.confidence:.2f}")
    print(f"  ADX: {state.adx:.2f}")
    print()

    # 4. Confidence Engine
    from brain.confidence import ConfidenceEngine
    engine = ConfidenceEngine(config)
    result = engine.score(
        regime_aligned=True, regime_clear=True,
        behavioral_pattern="stop_hunt", behavioral_strength=0.8,
        order_book_support=0.7, funding_favorable=0.6,
        volume_confirmed=True, regime="ranging"
    )
    print("Confidence scoring OK")
    print(f"  Score: {result.total_score}")
    print(f"  Action: {result.action}")
    print(f"  Risk: {result.position_risk_pct:.2%}")
    print(f"  Breakdown: {result.breakdown}")
    print()

    # 5. Risk Manager
    from execution.risk_manager import RiskManager
    rm = RiskManager(config)
    rm.set_day_start_equity(3650)
    can, reason = rm.can_trade()
    print("Risk manager OK")
    print(f"  Can trade: {can} ({reason})")
    pos = rm.calculate_position_size(
        equity=3650, risk_pct=0.02, entry_price=90000, stop_loss=89000, regime="trending_up"
    )
    print(f"  Position: ${pos.position_usd:.0f} at {pos.leverage}x leverage")
    print()

    # 6. Market Memory
    from brain.market_memory import MarketMemory
    mm = MarketMemory(config)
    mm.update_from_candles(df, "ranging")
    supports = mm.get_support_levels(close[-1])
    resistances = mm.get_resistance_levels(close[-1])
    print("Market memory OK")
    print(f"  Support levels: {len(supports)}")
    print(f"  Resistance levels: {len(resistances)}")
    print()

    # 7. DB Models
    from database.models import Base, TradeJournal
    print("Database models OK")
    print(f"  Tables: {list(Base.metadata.tables.keys())}")
    print()

    # 8. Strategy selector
    from brain.strategy_selector import StrategySelector
    ss = StrategySelector(config)
    s = ss.select("trending_up")
    print(f"Strategy selector OK: {s.name}")
    print()

    # 9. Behavioral detector
    from brain.behavioral import BehavioralDetector
    bd = BehavioralDetector(config)
    signals = bd.detect_all(df, support_levels=[89500], resistance_levels=[91000])
    print(f"Behavioral detector OK: {len(signals)} signals detected")
    print()

    print("=" * 50)
    print("ALL SYSTEMS GO - Khufra V2 ready")
    print("=" * 50)


if __name__ == "__main__":
    test_all()

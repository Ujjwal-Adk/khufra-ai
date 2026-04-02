"""
Khufra Trading System - Technical Indicators
Pure numpy/pandas implementations of all indicators needed for regime detection.
All functions work on pandas DataFrames with OHLCV columns.
"""

import numpy as np
import pandas as pd
from typing import Optional


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return series.rolling(window=period).mean()


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range.
    df must have 'high', 'low', 'close' columns.
    """
    high = df['high']
    low = df['low']
    close = df['close']

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.ewm(span=period, adjust=False).mean()


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average Directional Index (ADX).
    Measures trend strength (not direction).
    df must have 'high', 'low', 'close' columns.
    """
    high = df['high']
    low = df['low']
    close = df['close']

    # Directional movement
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index)

    # True range
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Smoothed averages
    atr = true_range.ewm(span=period, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr)

    # ADX
    dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan))
    adx = dx.ewm(span=period, adjust=False).mean()

    return adx


def calculate_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0
) -> dict:
    """
    Calculate Bollinger Bands + width + percentile rank.
    Returns dict with 'upper', 'middle', 'lower', 'width', 'width_percentile'.
    """
    close = df['close']
    middle = close.rolling(window=period).mean()
    rolling_std = close.rolling(window=period).std()

    upper = middle + (rolling_std * std_dev)
    lower = middle - (rolling_std * std_dev)
    width = upper - lower

    # Width percentile rank over last 100 candles
    width_percentile = width.rolling(window=100, min_periods=20).apply(
        lambda x: (x.iloc[-1] <= x).sum() / len(x) * 100 if len(x) > 0 else 50,
        raw=False
    )

    return {
        'upper': upper,
        'middle': middle,
        'lower': lower,
        'width': width,
        'width_percentile': width_percentile
    }


def calculate_volume_ma(volume: pd.Series, period: int = 20) -> pd.Series:
    """Calculate volume moving average."""
    return volume.rolling(window=period).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> dict:
    """Calculate MACD, signal line, and histogram."""
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line

    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def detect_swing_highs_lows(
    df: pd.DataFrame,
    lookback: int = 5
) -> dict:
    """
    Detect recent swing highs and lows.
    Returns dict with 'swing_highs' and 'swing_lows' as lists of (index, price).
    """
    highs = []
    lows = []

    high = df['high'].values
    low = df['low'].values

    for i in range(lookback, len(df) - lookback):
        if high[i] == max(high[i - lookback:i + lookback + 1]):
            highs.append((df.index[i], high[i]))
        if low[i] == min(low[i - lookback:i + lookback + 1]):
            lows.append((df.index[i], low[i]))

    return {'swing_highs': highs, 'swing_lows': lows}


def calculate_volume_spike(volume: pd.Series, period: int = 20) -> pd.Series:
    """Calculate volume as multiple of average (for spike detection)."""
    vol_ma = calculate_volume_ma(volume, period)
    return volume / vol_ma.replace(0, np.nan)


def calculate_all_regime_indicators(df: pd.DataFrame, config=None) -> dict:
    """
    Calculate all indicators needed for regime detection in one call.
    Returns a dict with all computed indicators.
    """
    ema_fast_period = config.regime.ema_fast if config else 21
    ema_slow_period = config.regime.ema_slow if config else 50

    adx = calculate_adx(df, period=14)
    atr = calculate_atr(df, period=14)
    atr_avg = atr.rolling(window=20).mean()
    ema_fast = calculate_ema(df['close'], ema_fast_period)
    ema_slow = calculate_ema(df['close'], ema_slow_period)
    bb = calculate_bollinger_bands(df, period=20, std_dev=2.0)
    vol_ma = calculate_volume_ma(df['volume'], period=20)
    vol_spike = calculate_volume_spike(df['volume'], period=20)

    return {
        'adx': adx,
        'atr': atr,
        'atr_avg': atr_avg,
        'atr_ratio': atr / atr_avg.replace(0, np.nan),
        'ema_fast': ema_fast,
        'ema_slow': ema_slow,
        'bb_upper': bb['upper'],
        'bb_middle': bb['middle'],
        'bb_lower': bb['lower'],
        'bb_width': bb['width'],
        'bb_width_percentile': bb['width_percentile'],
        'volume_ma': vol_ma,
        'volume_spike': vol_spike,
    }

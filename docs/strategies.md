# Trading Strategies - Project Khufra AI

**Status:** Waiting for Anjing to document proven strategies
**Last Updated:** January 16, 2026

---

## Overview

This document contains all trading strategies used by Khufra AI. Each strategy includes:
- Entry rules (when to enter a trade)
- Exit rules (when to exit)
- Risk management parameters
- Expected win rate and performance

---

## Strategy Template

Use this template to document each strategy:

### Strategy Name: [e.g., Breakout Momentum]

**Market Conditions:** [trending/ranging/volatile]
**Timeframe:** [e.g., 15min, 1hour, 4hour]
**Trading Pairs:** [e.g., BTC/USDT, ETH/USDT]

#### Entry Rules
1. **Primary Indicators:**
   - RSI > 50 (14-period)
   - Price breaks above resistance
   - Volume spike (1.5x average)

2. **Confirmation Signals:**
   - MACD crossover (bullish)
   - Increasing volume
   - [Add more as needed]

3. **Entry Trigger:**
   - [Exactly when to enter]

#### Exit Rules
1. **Take Profit:**
   - Target: 5% gain OR 2x risk
   - Method: [fixed percentage / trailing stop]

2. **Stop Loss:**
   - Level: 2% below entry OR below support
   - Type: [fixed / trailing]

3. **Trailing Stop:** (if applicable)
   - Activation: When 3% in profit
   - Trail: 1.5% below high

#### Risk Management
- **Position Size:** 2% of portfolio
- **Maximum Risk:** 2% per trade
- **Risk/Reward Ratio:** Minimum 2:1

#### Why This Works
[Explain the reasoning behind this strategy]

#### Historical Performance
- **Win Rate:** ~60% (if known)
- **Average Winner:** +5.2%
- **Average Loser:** -2.1%
- **Total Trades:** 50+ (if tracked)

#### Notes
- Best in trending markets
- Avoid during major news events
- [Any other important notes]

---

## Strategy 1: [TO BE DOCUMENTED BY ANJING]

*Waiting for strategy details...*

---

## Strategy 2: [TO BE DOCUMENTED BY ANJING]

*Waiting for strategy details...*

---

## Strategy 3: [TO BE DOCUMENTED BY ANJING]

*Waiting for strategy details...*

---

## Technical Indicators Used

### RSI (Relative Strength Index)
- **Period:** 14
- **Overbought:** 70
- **Oversold:** 30
- **Usage:** Momentum confirmation

### MACD (Moving Average Convergence Divergence)
- **Fast:** 12
- **Slow:** 26
- **Signal:** 9
- **Usage:** Trend confirmation

### Moving Averages
- **SMA 20:** Short-term trend
- **SMA 50:** Medium-term trend
- **EMA 12/26:** MACD components
- **Usage:** Trend identification

### Bollinger Bands
- **Period:** 20
- **Std Dev:** 2
- **Usage:** Volatility and support/resistance

### Volume
- **Period:** 20 (for average)
- **Usage:** Confirm breakouts and trends

---

## Risk Management Rules

### Global Rules (Applied to All Strategies)
1. **Never risk more than 2% per trade**
2. **Maximum 3 concurrent positions**
3. **Daily loss limit: 5% of portfolio**
4. **Monthly loss limit: 15% of portfolio**
5. **Stop trading after 3 consecutive losses**

### Position Sizing Formula
```
Position Size = (Account Balance × Risk%) / (Entry Price - Stop Loss)
```

Example:
- Account: $10,000
- Risk: 2% = $200
- Entry: $50,000
- Stop Loss: $49,000
- Position Size = $200 / $1,000 = 0.2 BTC

---

## Strategy Selection Logic

The bot will select strategies based on:
1. **Current Market Conditions**
   - Trending: Use breakout/momentum strategies
   - Ranging: Use mean reversion strategies
   - Volatile: Reduce position sizes

2. **Signal Strength**
   - Multiple confirmations = higher confidence
   - Single signal = lower position size

3. **Recent Performance**
   - If strategy underperforming, reduce allocation
   - Track win rate per strategy

4. **Risk Limits**
   - Don't exceed max concurrent positions
   - Respect daily/monthly limits

---

## News-Based Overrides

Certain news events will override strategies:

### Positive News (May increase position size)
- Major adoption announcements
- Favorable regulations
- Institutional investments

### Negative News (May skip trades or close positions)
- Exchange hacks
- Government bans
- Major technical issues

### Neutral (Proceed normally)
- Minor price movements
- Typical market news

---

## Performance Tracking

For each strategy, we track:
- Total trades executed
- Win rate (%)
- Average profit per winner
- Average loss per loser
- Maximum drawdown
- Sharpe ratio
- Risk/reward ratio

### Monthly Review
- Analyze each strategy's performance
- Adjust parameters if needed
- Disable underperforming strategies
- Optimize position sizing

---

## Notes for Anjing

Please document your strategies using the template above. Include:
1. **Clear entry rules** - What indicators/conditions trigger entry?
2. **Clear exit rules** - When do we take profit? Where's the stop loss?
3. **Risk parameters** - How much to risk? Position size?
4. **Historical performance** - Win rate from your manual trading?
5. **Market conditions** - When does this strategy work best?
6. **Why it works** - What's the logic/psychology behind it?

You can either:
- Edit this file directly
- Share in Discord #strategy-discussion channel
- Create separate documents for each strategy

---

**Status:** Awaiting strategy documentation from Anjing
**Next Steps:** Document 3-5 core strategies with historical performance data

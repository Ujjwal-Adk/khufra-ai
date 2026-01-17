# Project Khufra AI 🤖

> **An AI-powered automated crypto trading bot that combines technical analysis, sentiment monitoring, and Claude AI decision-making.**

**Version:** 0.1.0 (Phase 1)
**Status:** In Development - Foundation Complete
**Trading Mode:** Paper Trading Only (for now)

---

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Project Status](#project-status)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Development Timeline](#development-timeline)
- [Team](#team)
- [Safety & Risk Management](#safety--risk-management)

---

## 🎯 About

**Project Khufra AI** combines Anjing's trading expertise from Tokyo with Ujjwal's technical skills from Canada to create an automated crypto trading system.

**Philosophy:** "We can't predict the future, but we can move forward with mathematical certainty."

### Goals
- 🎯 Target Win Rate: 55-60%
- 📊 Monthly Return: 5-15% (conservative)
- 🛡️ Max Drawdown: <10%
- ⚡ Risk/Reward: Minimum 1:2

---

## ✨ Features

### Current (Phase 1 ✅)
- ✅ Complete project structure
- ✅ Database models for trades and performance tracking
- ✅ Configuration management
- ✅ Comprehensive logging system
- ✅ Risk management framework
- ✅ Setup scripts

### Coming Soon
- 🔄 **Phase 2:** News monitoring and sentiment analysis
- 🔄 **Phase 3:** TradingView integration
- 🔄 **Phase 4:** Exchange integration (Bitget)
- 🔄 **Phase 5:** Claude AI decision engine
- 🔄 **Phase 6:** Full risk management
- 🔄 **Phase 7:** Testing and optimization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Virtual environment

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd khufra-ai

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Run automated setup
python scripts/setup.py

# 4. Configure environment
# Edit .env file with your API keys

# 5. Test connections
python scripts/test_connections.py

# 6. Run the bot (paper trading)
python main.py
```

---

## ⚙️ Configuration

Edit `.env` file with your settings:

```env
# Trading Mode
TRADING_MODE=paper  # Always start with paper!

# Exchange API
BITGET_API_KEY=your_key_here
BITGET_API_SECRET=your_secret_here

# Claude AI
ANTHROPIC_API_KEY=your_key_here

# Risk Management
MAX_RISK_PER_TRADE=0.02
DAILY_LOSS_LIMIT=0.05
MAX_CONCURRENT_POSITIONS=3
```

---

## 👥 Team

**Ujjwal Adhikari** - Technical Lead
📍 Edmonton, Canada | 💻 Coding & AI Integration
📧 ujjwal.official010@gmail.com

**Anjing Khadka** - Strategy Lead
📍 Tokyo, Japan | 📊 Trading Strategies & Analysis
📧 anzo.anjing31@gmail.com

---

## 🛡️ Safety & Risk Management

### Non-Negotiable Rules
1. Start with paper trading (minimum 2 weeks)
2. Never risk more than 1-2% per trade
3. Maximum 3 concurrent positions
4. Daily loss limit: 5% of portfolio
5. Stop trading after 3 consecutive losses

### Security
- API keys never committed to GitHub
- Private repository only
- Regular backups
- Both team members monitor daily

---

## ⚠️ Disclaimer

Cryptocurrency trading involves substantial risk. This bot is for educational purposes. Never trade with money you cannot afford to lose. Not financial advice.

---

**Last Updated:** January 16, 2026
**Version:** 0.1.0
**Phase:** 1 - Foundation Complete ✅

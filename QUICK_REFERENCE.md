# Quick Reference - Project Khufra AI

Quick commands and information for daily development.

---

## 🚀 Quick Start Commands

```bash
# Activate virtual environment
venv\Scripts\activate

# Run automated setup
python scripts\setup.py

# Test all connections
python scripts\test_connections.py

# Start the bot
python main.py

# Stop the bot
Ctrl + C
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `main.py` | Main entry point - start here |
| `.env` | Your API keys (NEVER commit!) |
| `config/settings.py` | Bot configuration |
| `config/strategies.json` | Trading strategies |
| `requirements.txt` | Dependencies list |

---

## 🔧 Configuration

### Trading Mode
```env
TRADING_MODE=paper    # Safe mode (recommended)
TRADING_MODE=live     # Real money (dangerous!)
```

### Risk Limits
```env
MAX_RISK_PER_TRADE=0.02        # 2% max
DAILY_LOSS_LIMIT=0.05          # 5% daily
MAX_CONCURRENT_POSITIONS=3      # Max positions
```

---

## 📊 Key Modules

| Module | Purpose | Phase |
|--------|---------|-------|
| `news_monitor.py` | News scraping | Phase 2 |
| `tradingview.py` | TradingView signals | Phase 3 |
| `exchange.py` | Trade execution | Phase 4 |
| `ai_engine.py` | AI decisions | Phase 5 |
| `risk_manager.py` | Risk management | Phase 6 |
| `notifications.py` | Alerts | All phases |

---

## 🗄️ Database Models

- **Trade** - All trade information
- **Signal** - Trading signals from various sources
- **NewsEvent** - Market news and sentiment
- **PerformanceMetrics** - Daily/monthly stats
- **SystemLog** - System events and errors

---

## 📝 Logging

### Log Files Location
```
data/logs/khufra_ai.log      # General log
data/logs/errors.log         # Errors only
data/logs/daily_*.log        # Daily logs
```

### Log Levels
```env
LOG_LEVEL=DEBUG     # Everything
LOG_LEVEL=INFO      # Normal (recommended)
LOG_LEVEL=WARNING   # Warnings only
LOG_LEVEL=ERROR     # Errors only
```

---

## 🔑 Required API Keys

1. **Bitget Exchange**
   - API Key
   - API Secret
   - API Password

2. **Claude AI (Anthropic)**
   - API Key (starts with sk-ant-)

3. **Telegram Bot**
   - Bot Token
   - Your Chat ID
   - Anjing's Chat ID

4. **News APIs (Optional)**
   - NewsAPI.org key
   - Alpha Vantage key

---

## 🛡️ Safety Checklist

- [ ] Virtual environment activated
- [ ] Trading mode set to PAPER
- [ ] API keys in .env (not in code)
- [ ] Risk limits configured
- [ ] Both team members can monitor
- [ ] Emergency stop understood
- [ ] Paper trading tested for 2+ weeks

---

## 🐛 Troubleshooting

### Problem: Module not found
```bash
pip install -r requirements.txt
```

### Problem: Can't activate venv
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: Database locked
```bash
# Stop bot, delete database
del data\trades.db
# Restart bot (will recreate)
```

### Problem: API connection failed
- Check .env file for correct keys
- Verify internet connection
- See docs/troubleshooting.md

---

## 📞 Quick Contact

**Technical Issues:** ujjwal.official010@gmail.com
**Strategy Questions:** anzo.anjing31@gmail.com
**Discord:** #general channel

---

## 🔗 Useful Links

- [CCXT Docs](https://ccxt.readthedocs.io)
- [Claude API](https://docs.anthropic.com)
- [Bitget API](https://bitgetlimited.github.io/apidoc/en/spot)
- [Project GitHub](your-repo-url)

---

## 📅 Development Phases

- ✅ **Phase 1 (Week 1-2):** Foundation - COMPLETE
- 🔄 **Phase 2 (Week 3-4):** News Monitoring
- 🔄 **Phase 3 (Week 5-6):** TradingView Integration
- 🔄 **Phase 4 (Week 7-8):** Exchange Integration
- 🔄 **Phase 5 (Week 9-10):** AI Decision Engine
- 🔄 **Phase 6 (Week 11-12):** Risk Management
- 🔄 **Phase 7 (Week 13-14):** Testing
- 🔄 **Phase 8 (Week 15+):** Live Trading

---

## 💡 Daily Workflow

1. Activate virtual environment
2. Check Discord for updates
3. Pull latest code from GitHub
4. Review overnight logs
5. Test any changes
6. Commit and push code
7. Update team on progress

---

**Keep this file handy for quick reference!**

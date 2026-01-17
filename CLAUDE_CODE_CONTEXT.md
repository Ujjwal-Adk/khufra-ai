# PROJECT KHUFRA AI - CONTEXT FOR CLAUDE CODE
**Date Created:** January 16, 2026  
**Developer:** Ujjwal Adhikari  
**Partner:** Anjing Khadka (Japan)

---

## PROJECT OVERVIEW

### What We're Building
An AI-powered automated trading bot called "Khufra AI" that:
- Monitors geopolitical news and market sentiment 24/7
- Executes crypto trades based on proven trading strategies
- Operates without emotional bias using Claude AI for decision-making
- Combines Ujjwal's technical/AI skills with Anjing's trading expertise
- Target: 55-60% win rate for consistent profitability

### Partnership Structure
- **Ujjwal (Canada):** Technical lead - handles all coding, AI integration, infrastructure
- **Anjing (Japan):** Strategy lead - provides trading strategies, market analysis, signals
- **Time Commitment:** Ujjwal 15-20 hrs/week, Anjing 10-15 hrs/week
- **Communication:** Discord for calls/channels, Telegram for quick messages

### Philosophy
"We can't predict the future, but we can move forward with mathematical certainty. We don't need to be right every time - we need to be systematic, disciplined, and mathematically sound."

---

## CURRENT STATUS (Phase 1 - Week 1)

### ✅ COMPLETED
1. Discord server created: "Project Khufra AI"
2. GitHub repository created: project-khufra-ai (private)
3. VS Code installed on Ujjwal's machine
4. Master plan document created (14-week timeline)
5. Email sent to Anjing with project plan PDF
6. Communication platforms decided: Discord (primary) + Telegram (backup)

### 🔄 IN PROGRESS
1. Discord channels need to be added (see below)
2. Waiting for Anjing to document his trading strategies
3. Need to clone GitHub repo to local machine
4. Ready to start coding with Claude Code

### ⏳ NOT STARTED YET
- Python environment setup
- Bot code structure
- Database setup
- Library installations
- Google Cloud setup (planned for later)

---

## COMPLETE TECH STACK

### Programming Language
- **Python 3.11+** (primary language)

### Development Tools
- **VS Code** - Code editor (already installed)
- **Git & GitHub** - Version control (repo already created)
- **Claude Code** - CLI tool for agentic coding (using this now!)

### Python Libraries Needed
```
ccxt                    # Universal crypto exchange connector
pandas                  # Data analysis and manipulation
numpy                   # Mathematical calculations
requests                # API calls
python-telegram-bot     # Telegram notifications
pandas-ta               # Technical analysis indicators (or ta-lib)
anthropic               # Claude AI API integration
beautifulsoup4          # Web scraping for news
selenium                # TradingView automation
schedule                # Task scheduling
sqlalchemy              # Database ORM
python-dotenv           # Environment variables
asyncio                 # Async operations
```

### Cloud Infrastructure
- **Google Cloud Platform** - Ujjwal has this already
  - FREE tier: $300 credit for 90 days
  - After credits: ~$5-10/month for basic VM
- **Alternative:** Replit or Railway.app (FREE tiers available)

### AI/Analysis Tools
- **Claude API** - Ujjwal has access via subscription
- **TradingView** - FREE tier for charts and signals
- **News APIs:**
  - NewsAPI.org (100 requests/day free)
  - Alpha Vantage (500 requests/day free)
  - CryptoPanic (crypto-specific news)

### Trading Platforms
- **Bitget** - Primary exchange (Anjing uses this)
- **Binance/Bybit** - Backup options
- **Paper Trading Accounts** - For testing (FREE)

### Database
- **SQLite** - For local development and testing
- **PostgreSQL** - For production (if needed later)

---

## PROJECT FILE STRUCTURE

```
project-khufra-ai/
│
├── .env                         # Environment variables (API keys, secrets)
├── .gitignore                   # Files to exclude from Git
├── README.md                    # Project overview and setup instructions
├── requirements.txt             # Python dependencies
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # All configuration settings
│   ├── api_keys.py              # API credentials (never commit!)
│   └── strategies.json          # Trading strategy parameters from Anjing
│
├── src/                         # Main source code
│   ├── __init__.py
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── news_monitor.py      # News scraping & sentiment analysis
│   │   ├── tradingview.py       # TradingView signal handler
│   │   ├── exchange.py          # Exchange API integration (Bitget)
│   │   ├── ai_engine.py         # Claude AI decision-making
│   │   ├── risk_manager.py      # Risk management logic
│   │   └── notifications.py     # Telegram/Discord alerts
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py            # Database models
│   │   ├── connection.py        # Database connection
│   │   └── queries.py           # Database queries
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Logging configuration
│       ├── helpers.py           # Helper functions
│       └── validators.py        # Input validation
│
├── data/
│   ├── trades.db                # SQLite database
│   └── logs/                    # Daily log files
│       └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   ├── test_news_monitor.py
│   ├── test_exchange.py
│   ├── test_ai_engine.py
│   └── test_risk_manager.py
│
├── docs/
│   ├── strategies.md            # Anjing's strategies documented
│   ├── api_reference.md         # API documentation
│   ├── setup_guide.md           # Setup instructions
│   └── troubleshooting.md       # Common issues & fixes
│
├── scripts/
│   ├── setup.py                 # Initial setup script
│   ├── install_deps.py          # Install dependencies
│   └── test_connections.py      # Test API connections
│
└── main.py                      # Main entry point - starts the bot
```

---

## PHASE 1 TASKS (Week 1-2)

### WEEK 1: Ujjwal's Tasks
- [x] Set up Discord server
- [x] Create private GitHub repository
- [ ] Clone repo to local machine
- [ ] Set up Python virtual environment
- [ ] Install all required Python libraries
- [ ] Create complete folder structure
- [ ] Build basic bot framework (skeleton code)
- [ ] Set up database schema
- [ ] Create configuration files
- [ ] Write README and setup documentation

### WEEK 1: Anjing's Tasks
- [ ] Document 3-5 core trading strategies with entry/exit rules
- [ ] Share 2-3 examples of past successful trades
- [ ] List favorite technical indicators and settings
- [ ] Define preferred trading pairs and timeframes
- [ ] Share risk management rules (stop loss, position sizing)

### WEEK 2: Together
- [ ] Daily 30-min Discord calls to review progress
- [ ] Review and finalize strategy documentation
- [ ] Test basic bot structure
- [ ] Set success metrics for Phase 1
- [ ] Prepare for Phase 2 (News Monitoring System)

---

## DISCORD CHANNEL STRUCTURE

**Text Channels:**
1. 📢 #general - Daily updates and casual chat
2. 📊 #strategy-discussion - Trading strategies and market analysis
3. 💻 #code-sharing - Code snippets and technical stuff
4. 🧪 #bot-testing - Testing results and logs
5. 📈 #daily-results - Performance tracking
6. 📚 #resources - Links, docs, tutorials

**Voice Channels:**
1. 🎙️ Strategy Call - For video meetings
2. 🔧 Quick Debug - For quick technical discussions

---

## WHAT ANJING NEEDS TO PROVIDE

### Trading Strategy Documentation Format
For each strategy, Anjing should provide:

```
Strategy Name: [e.g., Breakout Momentum]
Market Conditions: [trending/ranging/volatile]
Entry Rules:
  - Specific indicators: [e.g., RSI > 50, price breaks resistance]
  - Volume conditions: [e.g., volume spike above average]
  - Confirmation signals: [e.g., MACD crossover]
Exit Rules:
  - Take Profit: [e.g., 2x risk or 5% gain]
  - Stop Loss: [e.g., below support or -2%]
  - Trailing Stop: [if applicable]
Why It Works:
  [Reasoning behind the strategy]
Timeframe:
  [5min, 15min, 1hour, 4hour, daily]
Win Rate Estimate:
  [Historical performance if known]
```

### Technical Indicators Anjing Uses
Waiting for Anjing to specify his preferences. Common ones include:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Moving Averages (SMA/EMA)
- Bollinger Bands
- Volume indicators
- Support/Resistance levels

### Risk Management Rules
Waiting for Anjing to define:
- Position sizing method
- Maximum risk per trade (likely 1-2%)
- Daily loss limits
- When to stop trading
- Portfolio allocation rules

---

## CRITICAL REQUIREMENTS & CONSTRAINTS

### Non-Negotiable Rules
1. **Start Small:** Begin with smallest position sizes possible
2. **Paper Trade First:** Minimum 2 weeks paper trading before real money
3. **Risk Limits:**
   - Never risk more than 1-2% per trade
   - Maximum 3 concurrent positions
   - Daily loss limit: 5% of portfolio
   - Monthly loss limit: 15% of portfolio
   - Stop trading if 3 losses in a row

4. **Security:**
   - API keys NEVER committed to GitHub
   - Use .env files for secrets
   - Private repository only
   - Secure credential storage

5. **Code Quality:**
   - Extensive logging for all operations
   - Error handling everywhere
   - Unit tests for critical modules
   - Daily Git commits
   - Clear documentation

### Success Metrics (Development)
- ✅ All systems functional and integrated
- ✅ Paper trading shows 55%+ win rate
- ✅ All risk controls working properly
- ✅ Zero critical bugs or crashes
- ✅ Consistent performance over 2 weeks

### Success Metrics (Live Trading)
- 🎯 Win rate: 55-60% minimum
- 🎯 Maximum drawdown: <10%
- 🎯 Risk/reward ratio: Minimum 1:2
- 🎯 Monthly return: 5-15% (conservative)
- 🎯 System uptime: 99%+

---

## COST BREAKDOWN

### Current Costs: $0/month
- Discord: FREE
- Python & All Libraries: FREE
- VS Code: FREE
- GitHub: FREE (private repos included)
- Claude AI: FREE (Ujjwal's subscription)
- TradingView Free: FREE
- News APIs (free tiers): FREE
- Google Cloud (first 90 days): FREE

### Future Costs (Optional, Split 50/50)
- Google Cloud after 90 days: $5-10/month
- TradingView Pro: $15/month (if needed)
- VPS backup hosting: $5/month (if needed)

**Total: $0-15/month maximum**

---

## IMMEDIATE NEXT STEPS FOR CLAUDE CODE

### 1. Project Initialization
```bash
# Clone the repository
git clone [repo-url]
cd project-khufra-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
# (List all libraries from tech stack section)

# Install dependencies
pip install -r requirements.txt
```

### 2. Create Complete Folder Structure
Create all folders and __init__.py files as shown in the file structure above.

### 3. Set Up Configuration Files
Create:
- `.env.example` (template for environment variables)
- `.gitignore` (Python template + secrets)
- `config/settings.py` (central configuration)
- `config/strategies.json` (placeholder for Anjing's strategies)

### 4. Build Basic Bot Framework
Create skeleton code for:
- `main.py` - Entry point with basic event loop
- `src/modules/exchange.py` - Basic Bitget API connection
- `src/database/models.py` - Trade data model
- `src/database/connection.py` - Database initialization
- `src/utils/logger.py` - Logging setup

### 5. Create Setup Scripts
- `scripts/setup.py` - Automated setup process
- `scripts/test_connections.py` - Test all API connections
- `scripts/install_deps.py` - Install all dependencies

### 6. Documentation
Create:
- Comprehensive README.md with setup instructions
- docs/setup_guide.md with detailed walkthrough
- docs/strategies.md (template for Anjing to fill)

---

## IMPORTANT CONTEXT FOR AI CODING

### What Ujjwal Knows
- Python programming and automation
- AI/ML concepts and Claude AI integration
- Has built trading bots before (TradingView + Claude AI)
- Familiar with APIs, databases, cloud deployment
- Strong with system design and architecture

### What Ujjwal Needs Help With
- Writing clean, production-ready code
- Best practices for trading bot architecture
- Error handling and edge cases
- Database design for trade data
- Testing strategies

### What Anjing Provides
- Trading strategies and market expertise
- Entry/exit rules and indicators
- Risk management parameters
- Real-world trading experience
- Signal validation

### Development Approach
1. **Start Simple:** Build basic version first, add complexity later
2. **Test Everything:** Especially with money involved
3. **Fail Safe:** If anything breaks, bot stops trading
4. **Log Everything:** Detailed logs for debugging
5. **Iterative:** Build one module at a time, test, then integrate

---

## COMMUNICATION PROTOCOL

### Daily
- Quick Discord text updates on progress
- Both respond to alerts and notifications

### 3x Per Week
- 30-minute Discord video call
- Review recent progress
- Discuss any blockers or strategy adjustments

### Weekly
- 1-hour detailed review session
- Analyze all completed work
- Update documentation
- Plan next week's focus

---

## KEY REMINDERS

⚠️ **SECURITY:** Never commit API keys, passwords, or secrets to GitHub
⚠️ **START SMALL:** Begin with tiny position sizes in paper trading
⚠️ **PAPER TRADE FIRST:** Minimum 2 weeks before real money
⚠️ **RISK MANAGEMENT:** Protect capital first, profit second
⚠️ **LOG EVERYTHING:** Every decision, every trade, every error
⚠️ **BACKUP:** Daily backups of code and data
⚠️ **STAY LEGAL:** Ensure compliance with regulations

---

## USEFUL RESOURCES

### APIs & Documentation
- CCXT Docs: https://ccxt.readthedocs.io
- Claude AI API: https://docs.anthropic.com
- TradingView: https://www.tradingview.com/pine-script-docs
- Bitget API: https://bitgetlimited.github.io/apidoc/en/spot

### Learning Resources
- Python for Finance: https://realpython.com/python-finance
- Algorithmic Trading: r/algotrading on Reddit
- Trading Bot Examples: GitHub search "crypto trading bot python"

### Trading Education
- Babypips: https://babypips.com (free trading course)
- TradingView Education: Technical analysis basics

---

## QUESTIONS TO ANSWER DURING DEVELOPMENT

1. **Database Schema:** What trade data do we need to store?
   - Trade ID, timestamp, pair, entry/exit prices, size, PnL, strategy used, etc.

2. **News Sources:** Which news APIs should we prioritize?
   - Start with CryptoPanic and NewsAPI for crypto news

3. **Signal Validation:** How do we validate TradingView signals?
   - Waiting for Anjing's strategy documentation

4. **Error Handling:** What happens when exchange API fails?
   - Bot should stop trading, send alert to both via Telegram

5. **Position Sizing:** How to calculate position size dynamically?
   - Based on portfolio %, risk %, and stop loss distance

---

## PROJECT TIMELINE (14 Weeks Total)

**Phase 1 (Weeks 1-2):** Foundation & Setup [CURRENT]
**Phase 2 (Weeks 3-4):** News Monitoring System
**Phase 3 (Weeks 5-6):** TradingView Integration
**Phase 4 (Weeks 7-8):** Exchange Integration
**Phase 5 (Weeks 9-10):** AI Decision Engine
**Phase 6 (Weeks 11-12):** Risk Management
**Phase 7 (Weeks 13-14):** Testing & Optimization
**Phase 8 (Week 15+):** Live Deployment

---

## CONTACT INFORMATION

**Ujjwal Adhikari**
- Email: ujjwal.official010@gmail.com
- Location: Edmonton, Canada (NAIT student)
- Discord: [username to be added]
- GitHub: [username - repo owner]

**Anjing Khadka**
- Email: anzo.anjing31@gmail.com
- Location: Tokyo, Japan
- Discord: [waiting for him to join]
- GitHub: [waiting for username]

---

## NOTES FOR CLAUDE CODE

- Ujjwal is a capable programmer but wants clean, production-ready code
- This is a real project with real money eventually involved - take security seriously
- Anjing is not a programmer - keep strategy integration simple for him to understand
- Focus on modularity - each piece should work independently
- Prioritize error handling and logging - debugging will be critical
- Use type hints and docstrings - make code self-documenting
- Write tests for critical functions - especially risk management
- Keep it simple initially - we can always add complexity later

---

**END OF CONTEXT DOCUMENT**

Last Updated: January 16, 2026
Ready for Phase 1 Development with Claude Code!

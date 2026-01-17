# Project Khufra AI - Setup Guide

Complete step-by-step setup instructions for getting Project Khufra AI running on your machine.

---

## Prerequisites

### System Requirements
- **Operating System:** Windows 10/11, macOS 10.15+, or Linux
- **Python:** Version 3.11 or higher
- **RAM:** Minimum 4GB (8GB recommended)
- **Storage:** At least 1GB free space
- **Internet:** Stable connection required

### Software Requirements
- Python 3.11+ ([Download](https://www.python.org/downloads/))
- Git ([Download](https://git-scm.com/downloads))
- Text editor (VS Code recommended)

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd khufra-ai

# Verify you're in the right directory
ls  # Should see main.py, requirements.txt, etc.
```

---

## Step 2: Create Virtual Environment

**Why?** Keeps project dependencies isolated from your system Python.

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify:** Your prompt should now show `(venv)` at the beginning.

---

## Step 3: Run Automated Setup

The easiest way to get started:

```bash
python scripts/setup.py
```

This script will:
1. Check Python version
2. Install all dependencies
3. Create `.env` file from template
4. Initialize database
5. Run basic tests

**If this succeeds,** skip to Step 7 (Configuration).

---

## Step 4: Manual Setup (If Automated Fails)

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required Python packages (may take 5-10 minutes).

### Create Environment File

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### Create Directories

```bash
# Windows
mkdir data\logs

# Linux/Mac
mkdir -p data/logs
```

---

## Step 5: Initialize Database

The database will be created automatically on first run. To verify:

```bash
python -c "from src.database.connection import DatabaseManager; import asyncio; asyncio.run(DatabaseManager('sqlite:///data/trades.db').connect())"
```

---

## Step 6: Obtain API Keys

### Required API Keys

#### 1. Bitget Exchange (for live trading)
- Go to: https://www.bitget.com
- Sign up and verify account
- Navigate to: API Management
- Create API key with trading permissions
- Save: API Key, Secret, and Password

#### 2. Anthropic Claude AI
- Go to: https://console.anthropic.com/
- Sign up for account
- Navigate to: API Keys
- Create new API key
- Save the key (starts with `sk-ant-`)

#### 3. Telegram Bot (for notifications)
- Open Telegram
- Search for `@BotFather`
- Send `/newbot` and follow instructions
- Save the bot token
- Get your chat ID:
  - Send message to your bot
  - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
  - Find `chat.id` in the response

#### 4. News API (optional)
- Go to: https://newsapi.org/
- Sign up for free account
- Get API key from dashboard

---

## Step 7: Configure Environment

Open `.env` file in your text editor and fill in your API keys:

```env
# Trading Mode - ALWAYS START WITH PAPER!
TRADING_MODE=paper

# Exchange API
BITGET_API_KEY=your_actual_api_key_here
BITGET_API_SECRET=your_actual_secret_here
BITGET_API_PASSWORD=your_actual_password_here

# Claude AI
ANTHROPIC_API_KEY=sk-ant-your_key_here

# Telegram Notifications
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID_UJJWAL=your_chat_id
TELEGRAM_CHAT_ID_ANJING=anjing_chat_id

# Risk Management
MAX_RISK_PER_TRADE=0.02
DAILY_LOSS_LIMIT=0.05
MAX_CONCURRENT_POSITIONS=3
```

**Important:** Never commit `.env` file to Git!

---

## Step 8: Test Connections

Verify all services are accessible:

```bash
python scripts/test_connections.py
```

Expected output:
```
Testing: Database Connection... ✅ PASS
Testing: Claude AI API... ✅ PASS
Testing: Exchange API... ✅ PASS
Testing: Telegram Bot... ✅ PASS
```

If any tests fail, check:
- API keys are correct
- Internet connection is stable
- Services are not blocked by firewall

---

## Step 9: Configure Trading Strategies

Edit `config/strategies.json` with your trading strategies.

**Note:** This file contains template strategies. Replace with actual strategies from Anjing.

---

## Step 10: Run the Bot

### First Run (Paper Trading)

```bash
python main.py
```

You should see:
```
==============================================================
  Project Khufra AI v0.1.0
  Trading Mode: PAPER
==============================================================

✓ Database connected successfully
✓ All components initialized successfully

Khufra AI is now running!
```

### Stop the Bot

Press `Ctrl+C` to stop gracefully.

---

## Troubleshooting

### "Python version too old"
- Install Python 3.11+ from python.org
- Verify: `python --version`

### "Module not found"
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### "Database error"
- Delete `data/trades.db` and let it recreate
- Check file permissions

### "API connection failed"
- Verify API keys in `.env` are correct
- Check internet connection
- Ensure services are accessible from your location

### "Telegram bot not responding"
- Verify bot token is correct
- Ensure you've sent at least one message to the bot
- Check chat ID is correct

---

## Next Steps

1. ✅ Setup complete
2. 📝 Document trading strategies
3. 🧪 Test with paper trading
4. 📊 Monitor performance
5. 🚀 When ready, consider small live trades (with caution!)

---

## Getting Help

- **Documentation:** Check other docs in `docs/` folder
- **Troubleshooting:** See `docs/troubleshooting.md`
- **Discord:** Contact team on Discord server
- **Email:** ujjwal.official010@gmail.com

---

**Last Updated:** January 16, 2026

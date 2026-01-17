# Installation Guide for Python 3.13

You're running **Python 3.13.1**, which is newer than most packages expect. Here's how to install successfully:

---

## Option 1: Install Minimal Dependencies (Recommended)

This will get you started with just the core functionality:

```bash
# Make sure you're in the project folder and venv is activated
cd C:\Users\ujjwa\OneDrive\Desktop\khufra-ai
venv\Scripts\activate

# Upgrade pip first
python -m pip install --upgrade pip

# Install minimal dependencies
pip install -r requirements-minimal.txt

# Test if core works
python -c "from config.settings import settings; print('Config loaded!')"
```

---

## Option 2: Install Full Dependencies (Step by Step)

```bash
# 1. Core packages (should work fine)
pip install python-dotenv pydantic pydantic-settings sqlalchemy requests colorlog

# 2. Async packages
pip install aiohttp anthropic

# 3. Exchange package
pip install ccxt

# 4. Try pandas and numpy (might need pre-compiled wheels)
pip install --only-binary :all: numpy pandas

# 5. If pandas fails, try without it for now
# (We'll add it later when needed in Phase 2+)

# 6. Other packages
pip install beautifulsoup4 python-telegram-bot schedule tenacity python-dateutil pytz
```

---

## Option 3: Use Python 3.11 (Easiest)

If you keep having issues, install Python 3.11 which has better package support:

1. Download Python 3.11.x from [python.org](https://www.python.org/downloads/)
2. Install it (add to PATH)
3. Create new venv with Python 3.11:
   ```bash
   py -3.11 -m venv venv311
   venv311\Scripts\activate
   pip install -r requirements.txt
   ```

---

## What You Need RIGHT NOW

For Phase 1, you only need these core packages:

✅ **Critical (Must Have):**
- `python-dotenv` - Load .env files
- `pydantic` + `pydantic-settings` - Configuration
- `sqlalchemy` - Database
- `colorlog` - Logging

✅ **Important (Should Have):**
- `anthropic` - Claude AI (for Phase 5)
- `ccxt` - Exchange connection (for Phase 4)
- `requests` - HTTP requests
- `aiohttp` - Async operations

⚠️ **Can Skip for Now:**
- `pandas` + `numpy` - Data analysis (Phase 2+)
- `beautifulsoup4` - News scraping (Phase 2)
- `selenium` - TradingView automation (Phase 3)
- `python-telegram-bot` - Notifications (can add later)

---

## Quick Install Command

Try this single command:

```bash
pip install python-dotenv pydantic pydantic-settings sqlalchemy colorlog aiohttp anthropic ccxt requests tenacity python-dateutil pytz
```

This should work on Python 3.13 without issues.

---

## After Installation

Once you have the core packages installed:

```bash
# Test the installation
python -c "from config.settings import settings; print('✅ Config loaded!')"

# Test database
python -c "from src.database.models import Trade; print('✅ Models loaded!')"

# Test logging
python -c "from src.utils.logger import get_logger; print('✅ Logger loaded!')"

# If all pass, try running main.py
python main.py
```

---

## Troubleshooting

### Error: "No module named 'pydantic_settings'"
```bash
pip install pydantic-settings
```

### Error: NumPy compilation failed
```bash
# Try pre-compiled wheel
pip install --only-binary :all: numpy

# Or skip for now (not needed in Phase 1)
```

### Error: Pandas installation failed
```bash
# Skip pandas for now, we'll add it in Phase 2
# The bot will work without it for Phase 1
```

---

## What to Do Now

1. **Install core packages:**
   ```bash
   pip install python-dotenv pydantic pydantic-settings sqlalchemy colorlog aiohttp anthropic ccxt requests
   ```

2. **Create .env file:**
   ```bash
   copy .env.example .env
   notepad .env
   ```

3. **Test the bot:**
   ```bash
   python main.py
   ```

4. **If it works, add remaining packages as needed**

---

## Success Criteria

You'll know it's working when:
- ✅ No import errors when running `python main.py`
- ✅ Bot starts and shows "Khufra AI is now running!"
- ✅ Database file created at `data/trades.db`
- ✅ Logs appear in `data/logs/`

---

**You don't need ALL packages to start!**

Install core packages now, add others as you progress through phases.

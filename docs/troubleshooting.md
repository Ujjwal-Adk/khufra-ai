# Troubleshooting Guide - Project Khufra AI

Common issues and their solutions.

---

## Installation Issues

### Python Version Error

**Problem:** "Python 3.11+ required"

**Solution:**
1. Install Python 3.11+ from [python.org](https://python.org)
2. Verify installation: `python --version`
3. On some systems, use `python3` instead of `python`

---

### Module Not Found Error

**Problem:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Permission Denied

**Problem:** "Permission denied" when installing packages

**Solution:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or run with elevated permissions (not recommended in venv)
```

---

## Configuration Issues

### Missing .env File

**Problem:** Bot can't find configuration

**Solution:**
```bash
# Create from template
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

---

### Invalid API Keys

**Problem:** "API authentication failed"

**Solution:**
1. Verify keys in `.env` have no extra spaces
2. Check keys are not expired
3. Ensure API permissions are correct
4. For Bitget: Verify IP whitelist (if enabled)

---

### Environment Variables Not Loading

**Problem:** Settings show default values

**Solution:**
1. Ensure `.env` file is in project root (same folder as main.py)
2. Check file has no syntax errors
3. Restart the bot after editing `.env`

---

## Database Issues

### Database Locked

**Problem:** "Database is locked"

**Solution:**
```bash
# Stop all running instances of the bot
# Delete and recreate database
rm data/trades.db  # Linux/Mac
del data\trades.db  # Windows

# Restart bot to recreate tables
python main.py
```

---

### Table Doesn't Exist

**Problem:** "No such table: trades"

**Solution:**
```bash
# Delete existing database
rm data/trades.db

# Let bot recreate on startup
python main.py
```

---

### Database Corruption

**Problem:** "Database disk image is malformed"

**Solution:**
```bash
# Backup existing database
cp data/trades.db data/trades_backup.db

# Delete corrupted database
rm data/trades.db

# Restore from backup or start fresh
python main.py
```

---

## Connection Issues

### Exchange Connection Failed

**Problem:** Can't connect to Bitget/Binance

**Possible Causes:**
1. **Wrong API Keys**
   - Verify keys in `.env`
   - Check key permissions on exchange

2. **Network Issues**
   - Check internet connection
   - Try: `ping api.bitget.com`

3. **IP Restrictions**
   - Disable IP whitelist on exchange
   - Or add your IP to whitelist

4. **Firewall**
   - Check firewall isn't blocking connections
   - Try temporarily disabling firewall

---

### Telegram Bot Not Responding

**Problem:** Bot doesn't send notifications

**Solutions:**
1. **Verify Token**
   ```bash
   # Test token manually
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```

2. **Get Chat ID**
   - Send `/start` to your bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Find `"chat":{"id":123456}`

3. **Check Bot Privacy**
   - Ensure bot can receive messages
   - Add bot to group if needed

---

### Claude AI API Error

**Problem:** "Anthropic API authentication failed"

**Solutions:**
1. Verify API key starts with `sk-ant-`
2. Check key hasn't expired
3. Verify billing is set up on Anthropic console
4. Test key:
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01"
   ```

---

### News API Issues

**Problem:** Can't fetch news

**Solutions:**
1. Verify API key from newsapi.org
2. Check rate limits (100 requests/day on free tier)
3. Ensure `ENABLE_NEWS_MONITORING=true` in `.env`

---

## Runtime Issues

### Bot Crashes on Startup

**Problem:** Bot exits immediately with error

**Debugging Steps:**
1. Check logs: `cat data/logs/khufra_ai.log`
2. Run with debug logging:
   ```bash
   # Edit .env
   LOG_LEVEL=DEBUG

   # Run bot
   python main.py
   ```
3. Check error messages carefully

---

### High CPU Usage

**Problem:** Bot using too much CPU

**Solutions:**
1. Check for infinite loops in logs
2. Reduce API polling frequency
3. Optimize database queries
4. Check if stuck in error retry loop

---

### Memory Leak

**Problem:** Memory usage keeps increasing

**Solutions:**
1. Restart bot daily
2. Check for unclosed database connections
3. Review recent code changes
4. Monitor with: `top` or Task Manager

---

### Bot Stops Responding

**Problem:** Bot appears frozen

**Solutions:**
1. Check if waiting for API response
2. Review logs for errors
3. Restart the bot
4. Check internet connection

---

## Trading Issues

### Orders Not Executing

**Problem:** Bot detects signals but doesn't trade

**Possible Causes:**
1. **Paper Trading Mode**
   - Check: `TRADING_MODE=paper` in `.env`
   - This is intentional for safety!

2. **Risk Limits Hit**
   - Check daily loss limit
   - Check max concurrent positions
   - Review consecutive losses

3. **Position Size Too Small**
   - Check minimum order size on exchange
   - Increase position size if needed

4. **Insufficient Balance**
   - Verify account has funds
   - Check if funds are available (not in orders)

---

### Incorrect Trade Calculations

**Problem:** Position sizes or P&L seem wrong

**Solutions:**
1. Check exchange fees in configuration
2. Verify position size calculation
3. Review price precision settings
4. Check for floating-point rounding errors

---

### Stop Loss Not Triggering

**Problem:** Stop loss didn't execute

**Possible Causes:**
1. **Slippage:** Market moved too fast
2. **Exchange Issue:** API delays
3. **Bug in Code:** Check implementation

**Solutions:**
- Use market orders for stop loss
- Implement backup monitoring
- Consider lower position sizes

---

## Logging Issues

### No Log Files Generated

**Problem:** `data/logs/` is empty

**Solutions:**
```bash
# Ensure directory exists
mkdir -p data/logs

# Check write permissions
ls -la data/

# Verify LOG_LEVEL in .env
LOG_LEVEL=INFO
```

---

### Log Files Too Large

**Problem:** Logs filling up disk space

**Solutions:**
1. Logs rotate automatically (10MB max per file)
2. Manually clean old logs:
   ```bash
   rm data/logs/*.log.1
   rm data/logs/*.log.2
   ```
3. Reduce LOG_LEVEL to WARNING or ERROR

---

## Performance Issues

### Slow API Responses

**Problem:** Bot laggy, slow to react

**Solutions:**
1. Check internet speed
2. Reduce API rate limit in config
3. Use VPN if ISP throttling
4. Consider upgrading hosting

---

### Database Slow

**Problem:** Database queries taking long

**Solutions:**
1. Regularly vacuum SQLite:
   ```bash
   sqlite3 data/trades.db "VACUUM;"
   ```
2. Add indexes if needed
3. Consider PostgreSQL for production
4. Archive old data

---

## Git / Repository Issues

### Can't Push to GitHub

**Problem:** "Authentication failed"

**Solutions:**
1. Use Personal Access Token (not password)
2. Configure SSH keys
3. Check repository permissions

---

### Accidentally Committed Secrets

**Problem:** `.env` file pushed to GitHub

**URGENT ACTIONS:**
1. **Immediately rotate all API keys!**
2. Remove from Git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   git push origin --force --all
   ```
3. Update `.gitignore` to prevent future issues

---

## Testing Issues

### Tests Failing

**Problem:** `python scripts/test_connections.py` shows failures

**Solutions:**
1. Check each failed test individually
2. Verify API keys are correct
3. Ensure services are accessible
4. Check internet connection
5. Review firewall settings

---

## Getting Help

If you can't resolve your issue:

1. **Check Logs:**
   ```bash
   cat data/logs/khufra_ai.log
   cat data/logs/errors.log
   ```

2. **Enable Debug Logging:**
   ```env
   LOG_LEVEL=DEBUG
   ```

3. **Contact Team:**
   - Discord: #troubleshooting channel
   - Email: ujjwal.official010@gmail.com
   - Include: Error message, logs, what you tried

4. **Provide Details:**
   - Operating system
   - Python version
   - What you were doing when error occurred
   - Complete error message
   - Relevant log entries

---

## Common Error Messages

### "Event loop is closed"
- **Cause:** Asyncio event loop issue
- **Fix:** Restart the bot

### "Connection reset by peer"
- **Cause:** Network interruption
- **Fix:** Check internet, retry operation

### "Rate limit exceeded"
- **Cause:** Too many API requests
- **Fix:** Wait, reduce request frequency

### "Insufficient funds"
- **Cause:** Not enough balance
- **Fix:** Add funds or reduce position size

---

**Last Updated:** January 16, 2026

For additional help, check the README.md or contact the development team.

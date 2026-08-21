# AVA OS Troubleshooting

## Installation Issues

### "Command not found: python"

Python isn't installed or not in PATH.

**Fix:**
1. Download Python 3.9+ from https://www.python.org
2. During install, check "Add Python to PATH"
3. Restart terminal and verify: `python --version`

### "ModuleNotFoundError" when installing

Dependencies didn't install correctly.

**Fix:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### "Permission denied" on shell scripts

Scripts aren't executable (macOS/Linux).

**Fix:**
```bash
chmod +x scripts/run_chat.sh
chmod +x scripts/run_dashboard.sh
./scripts/run_chat.sh
```

## API & Configuration Issues

### "ANTHROPIC_API_KEY not found"

API key isn't set.

**Fix:**
```bash
# macOS/Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Verify
echo $ANTHROPIC_API_KEY
```

To make permanent, add to shell profile (`~/.bashrc`, `~/.zshrc`, etc.)

### "Invalid API key"

Key is expired or malformed.

**Fix:**
1. Visit https://console.anthropic.com/account/keys
2. Create new key if needed
3. Copy full key (starts with `sk-ant-`)
4. Set environment variable again

### "Rate limit exceeded"

Hit 100 requests/hour or 100 turns/session limit.

**Fix:**
- Wait 1 hour for hourly limit reset
- Start new session for turn limit
- Check `/api/safety` for remaining quota

## Chat & Voice Issues

### "Voice input failed" or microphone not working

Microphone permission issue.

**Fix:**

**macOS:**
1. System Preferences → Security & Privacy → Microphone
2. Allow access for your terminal/browser

**Windows:**
1. Settings → Privacy & Security → Microphone
2. Allow app to use microphone

**Linux:**
```bash
sudo apt-get install pulseaudio
sudo usermod -a -G audio $USER
```

### "Hanging on voice input"

Microphone is busy or unresponsive.

**Fix:**
1. Try text mode: `python -m avaos.chat`
2. Close other apps using microphone
3. Restart terminal

### "Garbled or incorrect speech recognition"

Background noise or audio quality issue.

**Fix:**
1. Reduce background noise
2. Speak clearly and closer to microphone
3. Try slower speech rate
4. Use text mode if persistent

## Dashboard Issues

### "Connection refused" when opening dashboard

Server not running or wrong port.

**Fix:**
```bash
# Make sure server is running
python scripts/dashboard.py

# If port 5000 in use, try different port
python scripts/dashboard.py --port 8080

# Then visit correct address
# http://localhost:5000 (default)
# http://localhost:8080 (if using --port 8080)
```

### "Page won't load" or blank screen

Browser cache issue or CSS loading problem.

**Fix:**
1. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
2. Clear browser cache
3. Try different browser
4. Check console for errors: F12 → Console tab

### "API endpoints returning 500 error"

Server-side error, usually from bad data or missing KB.

**Fix:**
```bash
# Re-initialize knowledge base
python scripts/manage_knowledge.py --init

# Restart dashboard
python scripts/dashboard.py
```

## Data & Export Issues

### "Export file won't download"

Browser security or network issue.

**Fix:**
1. Check browser's download folder
2. Allow downloads for localhost
3. Try different browser
4. Check firewall settings

### "Knowledge base empty" after initialization

Facts didn't load properly.

**Fix:**
```bash
# Re-initialize
python scripts/manage_knowledge.py --init

# Verify facts loaded
python scripts/manage_knowledge.py --view-age 10
```

### "Conversation history missing"

Corrupted JSONL file or wrong directory.

**Fix:**
```bash
# Check if file exists
ls ~/.ava_os/memory/conversation_history.jsonl

# Backup corrupted file
mv ~/.ava_os/memory/conversation_history.jsonl \
   ~/.ava_os/memory/conversation_history.jsonl.bak

# Start fresh
python -m avaos.chat
```

## Performance Issues

### "Chat is slow" or responses taking >30s

API latency or network issue.

**Check:**
1. Internet connection speed
2. Anthropic API status: https://status.anthropic.com
3. Local system resources (RAM, CPU)

**Fix:**
- Reduce max_tokens in chat.py (currently 500)
- Check if other heavy processes running
- Try again later if API is slow

### "Dashboard is slow" or laggy

Too much data or browser issue.

**Fix:**
1. Limit conversation history loaded: edit dashboard.py limit parameter
2. Close other browser tabs
3. Clear browser cache: Ctrl+Shift+Delete
4. Use simpler browser (Chrome faster than Firefox usually)

## Test Failures

### "Some tests fail" after changes

Code issue or environment problem.

**Fix:**
```bash
# Run full test suite
python -m unittest discover -s tests

# Run specific test
python -m unittest tests.test_chat

# Verbose output
python -m unittest discover -s tests -v
```

## Docker Issues

### "Docker container won't start"

Port or permission issue.

**Fix:**
```bash
# Check if port in use
docker ps

# Use different port
docker run -p 8080:5000 ...

# Check logs
docker logs <container_id>
```

### "Volume mount not working"

Path or permissions issue.

**Fix:**
```bash
# Ensure directory exists
mkdir -p ~/ava_data

# Use absolute path
docker run -v ~/ava_data:/root/.ava_os ...
```

## Still stuck?

1. Check full logs: `tail -n 100 ~/.ava_os/memory/notifications.log`
2. Enable debug mode (if available)
3. Search GitHub issues for similar problems
4. Create new issue with:
   - Error message (full text)
   - Command you ran
   - Python version (`python --version`)
   - OS and browser
   - Steps to reproduce

## Getting Help

- **Setup issues?** Read SETUP_GUIDE.md
- **API questions?** Check API.md
- **Feature details?** See README.md

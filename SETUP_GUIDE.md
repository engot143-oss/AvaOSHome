# AVA OS Setup Guide

Complete walkthrough for installing and configuring AVA OS.

## Prerequisites

- Python 3.9 or higher
- ~100MB disk space for dependencies
- Microphone (optional, for voice mode)
- Anthropic API key (get from https://console.anthropic.com/account/keys)

## Quick Start (5 minutes)

### 1. Install

```bash
python scripts/install.py
```

This will:
- Verify Python version
- Install all dependencies
- Set up your API key (interactive)
- Create necessary directories
- Initialize the knowledge base

### 2. Start Chatting

**Text mode:**
```bash
python -m avaos.chat
```

**Voice mode:**
```bash
python -m avaos.chat --voice
```

### 3. Open Dashboard

In another terminal:
```bash
python scripts/dashboard.py
```

Then open http://localhost:5000 in your browser.

## Docker Setup

**Build:**
```bash
docker build -t ava-os .
```

**Run:**
```bash
docker run -p 5000:5000 \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -v ava_data:/root/.ava_os \
  ava-os
```

**Or use docker-compose:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
docker-compose up
```

## Configuration

### Knowledge Base Customization

Add custom facts for your family's values:

```bash
python scripts/manage_knowledge.py --add
```

Then fill in:
- Fact ID (e.g., "family-01")
- Topic
- Title and explanation
- Age range (min/max)
- Complexity level (BEGINNER/INTERMEDIATE/ADVANCED)

### API Key Setup

If the installer didn't ask for your key:

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

**macOS/Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

To make permanent, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc
```

### Running Tests

Verify everything works:

```bash
python -m unittest discover -s tests
```

Expected: 170 tests pass.

## File Structure

```
~/.ava_os/
├── memory/
│   ├── profile.json              # User profile
│   ├── conversation_history.jsonl # Chat logs
│   ├── notifications.log          # Parent alerts
│   ├── analytics.json             # Learning data
│   ├── insights.json              # Sentiment/stress
│   └── security_log.jsonl         # Safety events
└── knowledge/
    ├── facts.jsonl                # Age-tagged facts
    └── learned.jsonl              # Mastered topics
```

## Troubleshooting

### "Python is not installed"

Download from https://www.python.org (3.9+)

Verify:
```bash
python --version
```

### "ModuleNotFoundError: No module named 'anthropic'"

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not found"

Set your key (see Configuration section above).

Test it:
```bash
echo $ANTHROPIC_API_KEY  # macOS/Linux
$env:ANTHROPIC_API_KEY  # Windows PowerShell
```

### "Microphone not working" (voice mode)

1. Check permissions: System Preferences → Security & Privacy → Microphone
2. Try text mode first: `python -m avaos.chat`
3. Test audio: `python -c "import speech_recognition; print('OK')"`

### Port 5000 already in use

Use a different port:
```bash
python scripts/dashboard.py --port 8080
```

Then visit http://localhost:8080

### "Rate limit exceeded"

AVA limits to 100 requests/hour. Wait a minute and try again.

## Next Steps

1. **First conversation:** Start with `python -m avaos.chat` to test
2. **Set birthdate:** Add her birthdate so knowledge matures with her
3. **Customize KB:** Add family values via `manage_knowledge.py --add`
4. **Monitor progress:** Open dashboard to see analytics
5. **Export data:** Regularly backup via `/api/export/full-backup`

## Support

- **Errors?** Check TROUBLESHOOTING.md
- **Features?** See README.md
- **Architecture?** See ARCHITECTURE.md
- **API endpoints?** See API.md

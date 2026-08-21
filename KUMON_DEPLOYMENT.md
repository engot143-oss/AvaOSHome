# AVA OS Kumon - Deployment Guide

Complete guide to deploying the Kumon-structured learning system for your daughter.

## Overview

**What's included:**
- Kumon-structured curriculum (26 concepts across 5 subjects)
- Interactive PWA (Progressive Web App)
- Daily topic selection and tracking
- Mastery-based progression
- Parent monitoring dashboard
- Offline-capable design

**Architecture:**
- Frontend: Static HTML/CSS/JavaScript PWA (deploy to Netlify)
- Backend: Flask server (run on your machine or cloud server)
- Data: Local storage on daughter's device + server sync

---

## Quick Deployment (5 minutes)

### Option 1: Netlify (Easiest)

1. **Fork/clone this repo to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "AVA OS Kumon initial commit"
   git remote add origin https://github.com/yourusername/ava-os-kumon.git
   git push -u origin main
   ```

2. **Connect to Netlify:**
   - Visit https://app.netlify.com
   - Click "New site from Git"
   - Select your GitHub repo
   - Deploy (uses netlify.toml automatically)

3. **Send to your daughter:**
   ```
   Your app is live at: https://your-site-name.netlify.app
   She can install it as an app on her phone!
   ```

### Option 2: Run Locally

1. **Start the Kumon server:**
   ```bash
   python scripts/kumon_server.py
   ```

2. **Open in browser:**
   ```
   http://localhost:5001
   ```

3. **Send her a link:**
   ```bash
   # If on same network:
   http://<your-computer-ip>:5001
   
   # If remote (across country):
   # Use ngrok to tunnel: https://ngrok.com
   ngrok http 5001
   ```

---

## First-Time Setup

### 1. Initialize Everything

```bash
# Install dependencies
pip install -r requirements.txt

# Curriculum is already in ~/.ava_os/curriculum/

# Verify it's there
python scripts/manage_knowledge.py --view-age 10
```

### 2. Configure Your Daughter's Profile

```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, 'src')

from avaos.memory import Memory

memory = Memory(Path.home() / '.ava_os' / 'memory')
profile = memory.load_or_create_profile(
    name='[Daughter Name]',
    age=10,
    date_of_birth='2016-08-19'  # Update this
)
print(f'Profile created: {profile.name}, age {profile.age}')
"
```

### 3. Start the Server

```bash
# Local development
python scripts/kumon_server.py

# Production (with gunicorn)
pip install gunicorn
gunicorn --bind 0.0.0.0:5001 --workers 4 scripts.kumon_server:app
```

### 4. Share the Link

Send her one of these:

**Scenario A: Same home network**
```
http://192.168.1.100:5001
(Replace IP with your computer's IP)
```

**Scenario B: Across the country (ngrok tunnel)**
```bash
# On your machine (requires free ngrok account)
ngrok http 5001

# Then send her the link like: https://abc123.ngrok.io
```

**Scenario C: Netlify (recommended for simplicity)**
```
https://your-ava-kumon.netlify.app
(Automatically hosted, no server management needed)
```

---

## Daily Topics & Progression

### How It Works

1. **Every day**, a new concept is selected from the Kumon curriculum
2. **Subject rotation**: Math → Science → English → History → Computer Science
3. **Mastery requirement**: She must reach 80% accuracy before unlocking the next concept
4. **Prerequisite chains**: Some concepts have prerequisites (e.g., "Multiplication" requires "Addition mastery")

### Example Progression

```
Day 1: Math - Addition (2-digit)
  ↓ Needs 80% mastery, ~5-7 attempts
Day 2: Math - Addition (2-digit with regrouping)
  ↓ Same subject, builds on previous
Day 3: Math - Subtraction (2-digit)
  ↓ New subject
Day 4: Science - Living vs Non-living
  ↓ Rotates through subjects daily
Day 5: English - Phonics & word families
```

---

## Parent Monitoring

### Check Her Progress Anytime

**View the dashboard:**
```
http://localhost:5001/parent-dashboard.html
```

**Key metrics to watch:**
- **Mastery %** - Overall progress across all concepts
- **Current Streak** - Consecutive days of practice (goal: 7+ days)
- **Subject Breakdown** - Which subjects she's strongest in
- **Concepts at Risk** - Where she's struggling (< 70%)

### Export Data

```bash
# Get progress report
curl http://localhost:5001/api/progress/all | jq

# Get mastery details
curl http://localhost:5001/api/mastery/report | jq

# Get today's topic
curl http://localhost:5001/api/topic/today | jq
```

---

## Customization

### Add Your Family's Values

```bash
python scripts/manage_knowledge.py --add
```

Then add custom facts like:
- Family financial values
- College/career aspirations
- Cultural/family traditions
- Specific interests (e.g., coding projects)

### Adjust Difficulty

All concepts have mastery thresholds (70-85%). To change:

Edit `~/.ava_os/curriculum/kumon_curriculum.json` and update the `mastery_threshold` field.

### Modify Daily Schedule

Change which subject comes which day by editing the subject order in `kumon_server.py`.

---

## Troubleshooting

### "Page won't load"

1. Verify server is running: `curl http://localhost:5001/api/health`
2. Check firewall is open (port 5001)
3. If using ngrok, verify tunnel is active

### "Data not syncing"

1. Check both devices are on same network (local) or using same ngrok link
2. Refresh the page
3. Check browser console for errors (F12)

### "She can't install as app"

1. Desktop browsers: Click install icon in address bar (after visiting once)
2. Mobile: Use "Add to Home Screen" from browser menu
3. iOS Safari: Requires iOS 15+

### "Progress not saving"

1. Check ~/. ava_os/memory/ has write permissions
2. Verify localStorage is enabled in browser (F12 → Application → LocalStorage)
3. Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)

---

## Long-Term Management

### Weekly Routine

- **Monday**: Check her mastery % (aim for 5% improvement/week)
- **Thursday**: Review which subjects she's engaging with most
- **Friday**: Send encouragement for weekend learning

### Monthly Routine

- **Month-end**: Export progress report and save it
- **Month-end**: Add 1-2 new custom family facts based on her interests
- **Month-end**: Adjust recommendations if needed

### Yearly Routine

- **Birthday**: New age-appropriate facts automatically unlock
- **Summer**: Track her progress across the whole summer
- **School year**: Align with her school curriculum (math, science, reading)

---

## API Reference

All endpoints available at `http://localhost:5001/api/`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/topic/today` | GET | Today's learning topic |
| `/progress/all` | GET | Overall progress |
| `/progress/subject/{name}` | GET | Subject-specific progress |
| `/mastery/report` | GET | Detailed mastery breakdown |
| `/attempt` | POST | Record practice attempt |
| `/chat` | POST | Chat with AVA |
| `/sync` | POST | Sync client data |
| `/health` | GET | Server health check |

### Example API Call

```bash
# Get today's topic
curl -X GET http://localhost:5001/api/topic/today

# Record a correct answer
curl -X POST http://localhost:5001/api/attempt \
  -H "Content-Type: application/json" \
  -d '{
    "concept_id": "math-001",
    "correct": true,
    "score": 0.85
  }'
```

---

## Security & Privacy

**Data stays local:**
- Conversation history: `~/.ava_os/memory/conversation_history.jsonl`
- Progress data: `~/.ava_os/memory/kumon_progress.json`
- Knowledge base: `~/.ava_os/knowledge/`

**No cloud sync (unless you add it):**
- Everything is local by default
- Export backups regularly for safety

**For Netlify deployment:**
- Only frontend runs on Netlify (no data stored there)
- Backend stays on your machine
- All data remains under your control

---

## Support

If something breaks:

1. **Check the logs:**
   ```bash
   tail -f ~/.ava_os/memory/notifications.log
   ```

2. **Restart the server:**
   ```bash
   pkill -f kumon_server.py
   python scripts/kumon_server.py
   ```

3. **Reset progress (if needed):**
   ```bash
   rm ~/.ava_os/memory/kumon_progress.json
   # Progress will reinitialize on next start
   ```

4. **Full backup before changes:**
   ```bash
   cp -r ~/.ava_os ~/.ava_os.backup-$(date +%Y%m%d)
   ```

---

## Next Steps

1. **Deploy**: Choose Netlify, Local, or Hybrid approach
2. **Customize**: Add family-specific facts via `manage_knowledge.py`
3. **Share**: Send her the link
4. **Monitor**: Check dashboard weekly
5. **Iterate**: Adjust based on her engagement and mastery

Happy learning! 🚀

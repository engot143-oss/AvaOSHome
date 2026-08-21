# AVA OS Kumon - Quick Start Guide

Get your daughter started in 10 minutes.

## Step 1: Start the Server (1 minute)

```bash
cd /e/EricBegone/AvaOSHome
python scripts/kumon_server.py
```

You should see:
```
[AVA OS - Kumon Server]
Starting server on http://localhost:5001
```

## Step 2: Send Her the Link (2 minutes)

### Option A: Same Home Network
```
http://<your-computer-ip>:5001
```

Get your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

### Option B: Across the Country (need ngrok)

```bash
# Install ngrok (free, one-time)
https://ngrok.com

# Start tunnel
ngrok http 5001

# Send her the link (looks like https://abc123.ngrok.io)
```

### Option C: Deploy to Netlify (Recommended)

See `KUMON_DEPLOYMENT.md` for one-click deployment

## Step 3: She Installs as App (2 minutes)

**On Mobile:**
- Open the link in Safari or Chrome
- Tap the menu (three dots)
- Select "Add to Home Screen"
- She can now tap the app icon anytime!

**On Desktop:**
- Click the install icon (usually in address bar)
- App appears on desktop

## Step 4: She Starts Learning (5 minutes)

1. She opens the app
2. Sees today's topic (e.g., "Math - Addition")
3. Chats with AVA about it
4. Practices the concept
5. Streak counter increases!

---

## What You Can Do Right Now

### Check Her Progress
```
http://localhost:5001/parent-dashboard.html
```

Look for:
- **Today's Topic** - What she's learning
- **Mastery %** - How well she's doing
- **Streak** - Days in a row

### View Her Conversation
```
curl http://localhost:5001/api/progress/all | jq
```

### Export Her Data
```bash
# Get mastery report
curl http://localhost:5001/api/mastery/report > progress.json

# Email it to yourself for backup
```

---

## Customization (Optional)

### Add Family Values/Facts

```bash
python scripts/manage_knowledge.py --add
```

Then tell her about:
- Your family's financial values
- Career paths you want her to know about
- Cultural traditions

### Adjust Daily Practice Time

Default: 20 min/day

Edit `scripts/kumon_server.py` and change:
```python
estimated_time_min=20  # Change to 30, 45, etc.
```

---

## Troubleshooting

### "Can't connect"
1. Is the server running? Check you ran the python command
2. Is she on same network? (if using local IP)
3. Try refreshing the page

### "Data not saving"
1. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. Check browser console (F12) for errors

### "App won't install"
- iOS needs iOS 15+
- Desktop needs Chrome/Edge
- After visiting once, try installing again

---

## Next Steps

1. **Let her practice for a few days** to see how she engages
2. **Check the dashboard weekly** to track progress
3. **Read KUMON_DEPLOYMENT.md** for advanced setup (better hosting, backup, etc.)
4. **Contact support** if you need help

---

Happy learning! 🚀

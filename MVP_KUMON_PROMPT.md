# AVA OS - Core MVP Prompt (Kumon Only)

**Use this prompt in a new Claude Code project to build just the learning system.**

---

## Your Prompt:

```
I'm building AVA OS - an AI tutor for my 10-year-old daughter. 

CORE FEATURES (MVP only):

1. **Kumon Curriculum System**
   - 5 subjects: Math, Reading, Writing, Science, Social Studies
   - Each subject has 50 concepts with difficulty levels (Beginner → Intermediate → Advanced)
   - Daily topic rotation (one topic per day)
   - Track mastery: needs 3 correct attempts to master (80% accuracy threshold)
   - Prerequisites: can't unlock next level until previous is 80% mastered
   - Show progress: % mastered per subject, total streak, concepts left

2. **Chat Interface**
   - Simple web page with chat box
   - Student types questions
   - AVA responds with guidance (not just answers)
   - Log conversation history

3. **Hallucination Prevention** (CRITICAL)
   - Extract factual claims from AVA's responses
   - Check against 20+ verified facts database
   - Flag uncertain claims with confidence levels: CERTAIN / PROBABLY / MAYBE / UNSURE / DON'T_KNOW
   - Never give wrong information to my daughter

4. **Backend API**
   - GET /api/topic/today - get today's topic
   - GET /api/progress/all - overall progress
   - GET /api/mastery/report - detailed progress
   - POST /api/attempt - record practice attempt
   - POST /api/chat - send message to AVA
   - GET /api/health - health check

5. **Simple Dashboard** (Parent View)
   - Password-protected
   - Show: today's topic, progress %, streak, subjects mastered
   - No fancy analytics - just the essentials

6. **Data Storage**
   - Save curriculum to JSON
   - Save progress to JSON (can restart fresh each day)
   - Save conversations to file

**CONSTRAINTS:**
- Keep it simple - no complexity
- No faith curriculum
- No autonomous improvements
- No encryption/security hardening yet
- No budget tracker or financial literacy
- Focus: Does the learning system work?

**SUCCESS CRITERIA:**
- Daughter can access it
- Can see today's topic
- Can chat with AVA
- AVA doesn't hallucinate
- Progress is tracked correctly
- Parents can see dashboard
```

---

## What to Build First:

1. ✅ **Kumon curriculum structure** (5 subjects, 50 concepts each)
2. ✅ **Daily topic selection** (picks one, tracks it)
3. ✅ **Progress tracking** (attempts, mastery %, streak)
4. ✅ **Simple chat** (student → AVA → response)
5. ✅ **Hallucination check** (basic: check against 20 facts)
6. ✅ **Web interface** (just text chat + progress bar)
7. ✅ **Flask backend** (serve API + static files)
8. ✅ **Deploy** (Netlify frontend + Heroku backend)

---

## File Structure (Simple):

```
avaos-core/
├── src/
│   └── avaos/
│       ├── kumon.py (curriculum + progress)
│       ├── hallucination.py (fact checking)
│       ├── memory.py (save conversations)
│       └── chat.py (simple responses)
├── web/
│   ├── index.html (chat interface)
│   └── dashboard.html (parent view)
├── scripts/
│   └── server.py (Flask backend)
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## What You've Already Built:

- ✅ Kumon tracking system (use it!)
- ✅ Hallucination prevention framework (use it!)
- ✅ Chat interface (simplify it!)
- ✅ Memory system (use it!)
- ✅ Flask server (use it!)

**Just remove:**
- ❌ Autonomous improvement system
- ❌ Faith curriculum
- ❌ Financial literacy
- ❌ Budget tracker
- ❌ Encryption
- ❌ Security monitoring
- ❌ Complex dashboards

---

## Why This Matters:

With the MVP, you can:
- Get it live quickly (1-2 days)
- Test with your daughter
- See what actually works
- Add features one by one
- Not get overwhelmed

---

## Next Steps:

1. Create new folder: `E:\EricBegone\avaos-core`
2. Copy ONLY the core files (kumon.py, hallucination.py, memory.py, chat.py)
3. Create simple web/index.html (basic chat)
4. Create simple scripts/server.py (Flask)
5. Deploy
6. Get feedback from your daughter
7. Build from there

---

**Start fresh. Keep it simple. Focus on: Does learning work?**
```

---

## Here's What I Recommend:

1. **Pause the complicated project** (keep it saved)
2. **Create new folder:** `E:\EricBegone\avaos-core`
3. **Copy just these files** from the existing project:
   - `src/avaos/kumon.py`
   - `src/avaos/hallucination.py`
   - `src/avaos/memory.py`
   - `src/avaos/chat.py`
4. **Use the MVP prompt above** with fresh Claude Code
5. **Build simple, test with daughter, add features as needed**

Would you like me to help you:
- ✅ Copy the core files to a new folder?
- ✅ Create a fresh README for the MVP?
- ✅ Start a new Claude Code session with this prompt?

What feels right to you? 👇
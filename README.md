# AVA OS — A Truthful AI Guide for Your Daughter

AVA is a personal AI system designed to guide your 10-year-old daughter through life, school, and financial literacy — with a built-in guarantee that it will **never give her wrong advice**.

**Now with Kumon-structured learning:** Daily topics, mastery-based progression, and streak tracking for consistent learning.

Every piece of guidance is checked for hallucinations before she hears it. If AVA isn't sure, she says so.

## Quick Start

### Easiest Way: Automated Setup
```bash
python scripts/install.py
```

This handles Python check, dependency install, API key setup, and knowledge base init.

### Manual Setup

**Windows:**
1. Double-click `scripts/run_chat.bat` to start chatting
2. Double-click `scripts/run_dashboard.bat` to open the dashboard

**macOS/Linux:**
```bash
./scripts/run_chat.sh          # Start chatting (text)
./scripts/run_chat.sh --voice  # Start chatting (with voice)
./scripts/run_dashboard.sh     # Open dashboard
```

**Or use Python directly:**
```bash
python -m avaos.chat          # Text mode
python -m avaos.chat --voice  # Voice mode
python scripts/dashboard.py    # Dashboard
```

**Docker:**
```bash
docker-compose up
# Open http://localhost:5000
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed installation and deployment options.

## What AVA Does

### ✅ She Will:
- Answer questions about school, nursing careers, and life
- Explain financial concepts in age-appropriate ways
- Remember what your daughter has told her (conversation history)
- Tell you when she doesn't know something
- Verify facts with live web search if she's unsure

### ❌ She Won't:
- Give medical, financial, or legal advice without verifying the facts
- Make up information or guess
- Take actions on your behalf (send messages, buy things, etc.)
- Access the internet except to verify uncertain advice

## Safety & Guardrails

AVA OS includes multiple layers of protection:

**Input Validation:**
- Length limits (prevents token spam)
- Character validation (blocks special characters)
- Prompt injection detection (prevents jailbreaks like "ignore your instructions")
- SQL injection detection (blocks database attacks)

**Content Filtering:**
- Detects harmful topics (self-harm, suicide, abuse, illegal activities)
- Identifies harmful keywords and phrases
- Escalates sensitive content to parent notification
- Blocks inappropriate requests with clear messages

**Rate Limiting:**
- Max 100 requests per hour (prevents abuse)
- Conversation session limits (100 turns per session)
- Automatic throttling with user feedback

**Safety Logging:**
- Records all security violations
- Tracks violation types and patterns
- Available on dashboard for parent review
- Helps identify concerning trends

**Hallucination Checking:**
Every time AVA responds:
1. **Claim Extraction** — Break her response into individual factual claims
2. **Grounding Check** — Do these claims come from sources she already knows about?
3. **Stakes Assessment** — How risky is it if this claim is wrong?
4. **Fallback Check** — For high-stakes claims, search the web to verify

If a claim can't be verified, AVA either hedges it ("I'm not completely sure about this") or asks you to check with a trusted adult.

## Knowledge Base Management

AVA grows with your daughter. You can customize what she learns and track her progress.

### Initialize the Knowledge Base
On first run, AVA will automatically create a knowledge base with 9 core facts covering:
- **Nursing** — What nurses do, career paths, how to become a nurse
- **Finance** — Money basics, earning, saving, banking
- **Life Skills** — Managing emotions, friendships, time management

### View Available Knowledge
See what's appropriate for your daughter's current age:
```bash
python scripts/manage_knowledge.py --view-age 10
```

### Add Custom Facts
Teach her topics beyond the defaults:
```bash
python scripts/manage_knowledge.py --add
```

You'll be prompted to enter:
- Fact ID (e.g., "nursing-04")
- Topic (nursing, finance, life_skills, or custom)
- Title and explanation
- Age range and complexity level (BEGINNER / INTERMEDIATE / ADVANCED)
- Source and any parent notes

### Track What She's Learned
See which topics she's already mastered:
```bash
python scripts/manage_knowledge.py --learned
```

## Parent Notifications

High-stakes advice gets logged to a file so you can review conversations:

```
~/.ava_os/memory/notifications.log
```

Topics that trigger notifications:
- **MEDICAL** — Health, medication, symptoms
- **FINANCIAL** — Money, investing, saving
- **CRITICAL** — Identity, safety, major life decisions

## Cost

AVA runs almost entirely on your computer, except:
- **Anthropic API** (~$2-10/month for active daily use) — only used when verifying uncertain advice
- **Voice I/O** (free) — uses local, open-source speech recognition and synthesis

## Files

- `src/avaos/` — Core logic (hallucination pipeline, memory, chat)
- `tests/` — 63 unit tests verifying the system works correctly
- `scripts/` — Demos and utilities
- `docs/` — Design specification (framework_design.md)

## How the Knowledge Base Works

When you start a conversation, AVA automatically:

1. **Loads age-appropriate facts** — Only content tagged for your daughter's current age
2. **Sorts by complexity** — Starts with simple concepts, adds detail as she matures
3. **Includes facts in her context** — Claude sees these facts and uses them to guide her responses
4. **Respects boundaries** — Won't teach concepts beyond her age range

This means AVA's knowledge naturally grows as your daughter does. At 10, she learns "how to earn an allowance." At 14, she can learn about interest and compound growth. At 18, she understands investment strategy.

You control what goes into the knowledge base, so you can:
- **Add family-specific facts** (e.g., your family's financial values)
- **Update existing facts** (e.g., when she graduates a complexity level)
- **Track learning progress** (see which topics stick)

## Birthday Progression

AVA matures automatically with your daughter. Set her date of birth once, and:

- **On each birthday**, new age-appropriate facts automatically unlock
- **Explanations get more sophisticated** as she ages (simple → intermediate → advanced)
- **Parent gets notified** of the milestone
- **Daughter sees a birthday greeting** when she logs in

Example progression for nursing:
- **Age 10** — "Nurses help people who are sick or hurt"
- **Age 12** — "There are different types: emergency, pediatric, surgical"
- **Age 16+** — "To become a nurse: science classes → nursing program → NCLEX exam"

Set her date of birth in the dashboard or via:
```bash
python scripts/manage_knowledge.py --add-birthdate 2014-03-15
```

## File Structure

The knowledge base is stored in `~/.ava_os/knowledge/` with two files:

- `facts.jsonl` — All facts tagged by age, topic, and complexity
- `learned.jsonl` — Topics your daughter has mastered

Conversation history is in `~/.ava_os/memory/`:

- `conversation_history.jsonl` — Every turn tagged with timestamp and topic
- `notifications.log` — High-stakes advice flagged for parent review

## Parental Dashboard

A mobile-optimized web interface for managing and monitoring AVA's conversations, knowledge base, and learning progress.

**Start the dashboard:**
```bash
python scripts/dashboard.py
```

Then open your browser to `http://localhost:5000`

**Mobile & PWA Support:**
- Fully responsive design (mobile, tablet, desktop)
- Progressive Web App (PWA) support — install as app on phone
- Offline caching for basic functionality
- Touch-friendly interface with 44px minimum tap targets
- Works on iOS, Android, and web browsers

**Dashboard Tabs:**
- **Conversations** — Browse all chat history, filter by topic, see timestamps
- **Notifications** — Review high-stakes advice (medical, financial, critical)
- **Analytics** — Track learning progress:
  - Topic engagement (how often discussed)
  - Mastery levels (1-5 proficiency rating)
  - Learning streaks (consistency tracking)
  - Knowledge gaps (topics to focus on)
  - Learning recommendations (personalized suggestions)
- **Knowledge Base** — View age-appropriate facts for any age (8-18)
- **Learning Progress** — Track mastered topics by age

## Export & Backup

Export your daughter's data anytime for backup or external analysis:

**Available exports from dashboard:**
- **Conversations** — Full chat history (JSON or CSV format)
- **Analytics** — Learning metrics and progress data
- **Knowledge Base** — All age-appropriate facts and curriculum
- **Profile** — User information and preferences
- **Full Backup** — Complete system snapshot with timestamp

**API Endpoints:**
- `/api/export/conversations?format=json` — Export conversations
- `/api/export/analytics` — Export learning analytics
- `/api/export/knowledge-base` — Export knowledge base
- `/api/export/full-backup` — Export everything
- `/api/export/summary` — Get backup summary (what will be exported)

All exports are JSON-formatted and include timestamps for audit trails.

## Advanced Insights

Track deeper patterns in learning and emotional well-being:

**Sentiment Analysis:**
- Detect positive, negative, neutral sentiment in conversations
- Stress level indicators (0.0-1.0 scale)
- Emotional checkpoint tracking over time

**Learning Velocity:**
- Conversations per day (learning pace)
- Trend detection: accelerating, stable, or decelerating
- Days active tracking

**Engagement Patterns:**
- Primary and secondary interests
- Focus level (concentrated vs. broad topics)
- Interest evolution over time

**Stress Indicators:**
- High stress detection
- Declining engagement patterns
- Sentiment trend analysis
- Automatic recommendations

**API Endpoints:**
- `/api/insights` — Comprehensive insights summary
- `/api/insights/emotional-trend?days=7` — Emotional patterns
- `/api/insights/velocity` — Learning pace metrics
- `/api/insights/patterns` — Topic engagement patterns
- `/api/insights/stress` — Stress and engagement alerts

## Learning Analytics

AVA automatically tracks your daughter's learning:

**Engagement Metrics:**
- How often each topic is discussed
- Average message count per discussion
- First and last discussion dates

**Mastery Levels:**
- Rate her proficiency in each topic (1-5)
- Track progression over time
- Identify areas for deeper study

**Learning Streaks:**
- Monitor daily learning consistency
- Celebrate consecutive days of engagement
- Identify periods of reduced interaction

**Knowledge Gaps:**
- See which topics haven't been discussed yet
- Get recommendations on what to focus on next
- Personalized learning path suggestions

**Export & Analysis:**
- Export analytics as JSON for external review
- Track long-term learning patterns
- Identify emerging interests and strengths

## Documentation

📖 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** — Complete installation walkthrough
🔧 **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Common issues and fixes  
🌐 **[API.md](API.md)** — Dashboard and export API reference
📐 **[DEPLOYMENT.md](DEPLOYMENT.md)** — Docker, cloud, and deployment options
🏗️ **[docs/framework_design.md](docs/framework_design.md)** — Architecture deep-dive

## Next Steps

1. **Setup:** `python scripts/install.py`
2. **Chat:** `python -m avaos.chat --voice`
3. **Dashboard:** `python scripts/dashboard.py` (http://localhost:5000)
4. **Customize:** `python scripts/manage_knowledge.py --add`
5. **Backup:** Export via dashboard or `/api/export/full-backup`

## At a Glance

| Feature | Status |
|---------|--------|
| Hallucination checking | ✅ Multi-stage verification |
| Age progression | ✅ Birthday-triggered unlocking |
| Learning analytics | ✅ Engagement, mastery, velocity |
| Safety guardrails | ✅ Rate limiting, content filter |
| Mobile/PWA | ✅ Offline caching, app install |
| Export/backup | ✅ Full data portability |
| Advanced insights | ✅ Sentiment, stress, patterns |
| Voice I/O | ✅ Optional speech recognition |
| Dashboard | ✅ Multi-tab monitoring UI |
| Docker support | ✅ One-command deployment |
| Test coverage | ✅ 170 tests passing |

---

Built with a hallucination-checking pipeline that verifies every claim before your daughter hears it.
**All code is open-source and runs locally on your machine.**

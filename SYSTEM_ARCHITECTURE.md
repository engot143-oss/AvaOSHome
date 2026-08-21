# AVA OS - Complete System Architecture

## All Frameworks & Systems

### 1. **HALLUCINATION PREVENTION PIPELINE** 
**File:** `src/avaos/hallucination_prevention.py`

Multi-stage analysis:
- Claim extraction (identifies factual/definition/process/opinion statements)
- Fact verification (checks against verified database)
- Confidence scoring (0.0-1.0 scale)
- Parent audit reports
- Statistics tracking

**How it works:**
1. Extract claims from AVA's response
2. Verify each claim against database
3. Flag unverified or low-confidence claims
4. Calculate overall response confidence
5. Add uncertainty markers if needed
6. Generate parent report

---

### 2. **KUMON CURRICULUM SYSTEM**
**File:** `src/avaos/kumon.py`

Daily learning structure:
- Daily topic rotation (5 subjects: Math, English, Science, Faith, Finance)
- Concept tracking (progress per concept)
- Mastery calculation (% based on correct answers)
- Prerequisite unlocking (prerequisites must be mastered first)
- Streak tracking (consecutive days of practice)
- Subject progress (per-subject mastery)

**How it works:**
1. Rotates through 5 subjects daily
2. Selects one concept for the day
3. Records attempts (correct/incorrect)
4. Calculates mastery %
5. Unlocks prerequisite concepts when ready
6. Tracks learning streaks

---

### 3. **ADAPTIVE DIFFICULTY SYSTEM**
**File:** `src/avaos/adaptive_difficulty.py`

Performance-based progression:
- Tracks accuracy per concept
- Adjusts difficulty based on performance
- 3 levels: Easy, Medium, Hard
- Rules:
  - <60% accuracy: Stay same level
  - 60-80% accuracy: Maintain level
  - >80% accuracy: Advance to harder
  - Drop below 50%: Regress to easier

**How it works:**
1. Track last 10 attempts
2. Calculate accuracy %
3. Compare to thresholds
4. Auto-adjust difficulty
5. Record performance history

---

### 4. **SPACED REPETITION SYSTEM**
**File:** `src/avaos/spaced_repetition.py`

Scientifically-proven review schedule:
- 5-stage review schedule (Day 1, 3, 7, 14, 30)
- Performance-based interval adjustment:
  - Poor performance: 0.5x multiplier (shorter interval)
  - Fair: 0.8x multiplier
  - Good: 1.0x multiplier (normal)
  - Excellent: 1.5x multiplier (longer interval)
- Auto-marks as "mastered" after final review
- Tracks which concepts are due today

**How it works:**
1. Schedule review at intervals
2. Adjust based on performance
3. Show due reviews first
4. Auto-graduate to mastered
5. Prevent forgetting

---

### 5. **LEARNING RECOMMENDATIONS ENGINE**
**File:** `src/avaos/learning_recommendations.py`

Smart "what to study next":
- 6 recommendation types:
  1. Spaced repetition due (highest priority)
  2. Prerequisite fixes (unlock new concepts)
  3. Low mastery improvement (weak areas)
  4. Subject balance (don't over-focus)
  5. Optimal progression (ready for next)
  6. Faith development (character growth)
- Priority scoring system
- Subject engagement tracking
- Top 5 recommendations per day

**How it works:**
1. Check spaced rep due dates
2. Find weak areas
3. Check prerequisites
4. Balance across subjects
5. Rank by priority score
6. Return top 5

---

### 6. **FINANCIAL LITERACY CURRICULUM**
**File:** `src/avaos/financial_literacy.py`

Age-progressive money education (ages 10-18):
- Age 10: Money basics, earning, saving
- Age 12: 50/30/20 rule, living within means
- Age 14: Banking, interest, compound growth
- Age 16: Credit/debt, taxes, investing
- Age 18: College costs, loans, wealth building

**Family values embedded:**
- "Don't live above your means"
- "Always save for rainy days"
- "Hard work = money"

**How it works:**
1. Unlock content by age
2. Progress through levels
3. Embed family values
4. Track financial goals
5. Build money mindset

---

### 7. **FAITH & CHARACTER CURRICULUM**
**File:** `src/avaos/faith_curriculum.py`

Age-progressive spiritual development (ages 10-18):
- Age 10-11: FOUNDATION (God, prayer, kindness)
- Age 12-14: CHARACTER (integrity, courage, temptation resistance)
- Age 14-17: PURPOSE (calling, addiction resistance, decisions)
- Age 16+: DISCIPLESHIP (deep faith, influencing others)

**Protective factors tracked:**
- Prayer practice
- Values demonstrated
- Faith foundation
- Church community involvement
- Self-reflection

**Daily reflection prompts (10 rotating):**
- "Who did I help today?"
- "Did I face temptation?"
- "How did I see God's love?"
- "Did I act with integrity?"
- And 6 more...

**How it works:**
1. Age-appropriate lessons
2. Track protective factors
3. Record prayers
4. Log value demonstrations
5. Provide daily reflection
6. Generate parent reports

---

### 8. **BUDGET TRACKER SYSTEM**
**File:** `src/avaos/budget_tracker.py`

Money management for kids:
- Income/expense logging
- 50/30/20 rule enforcement:
  - 50% = Needs
  - 30% = Wants
  - 20% = Savings
- Rainy day fund tracking (minimum 10%)
- Monthly spending summaries
- Budget health assessment
- Spending trend analysis (3-month)

**How it works:**
1. Log transactions
2. Categorize (needs/wants/savings)
3. Calculate percentages
4. Check vs 50/30/20
5. Alert if out of balance
6. Provide advice

---

### 9. **CLAIM EXTRACTOR**
**File:** `src/avaos/claim_extractor.py`

Identifies statements needing verification:
- Claim types:
  - Factual claims
  - Definitions
  - Process descriptions
  - Opinions
  - Instructions
- Verification levels: CRITICAL, HIGH, MEDIUM, LOW
- Vague claim detection
- Confidence threshold requirements:
  - CRITICAL: 95%
  - HIGH: 85%
  - MEDIUM: 75%
  - LOW: 60%

**How it works:**
1. Parse response text
2. Identify claim patterns
3. Classify by type
4. Assign verification level
5. Set confidence threshold
6. Flag for verification

---

### 10. **FACT VERIFICATION DATABASE**
**File:** `src/avaos/fact_verification.py`

Verified facts with sources:
- 20+ pre-verified facts across topics
- Science, history, math, finance, health
- Known false claims detection:
  - Flat earth
  - Vaccine myths
  - Moon landing denial
  - Evolution denial
- Confidence scoring (0.0-1.0)
- Multi-source attribution
- Family financial values (99% confidence)

**How it works:**
1. Load verified fact database
2. Check incoming claims
3. Match against database
4. Score confidence
5. Return verification result
6. Flag known false claims

---

### 11. **UNCERTAINTY COMMUNICATION**
**File:** `src/avaos/uncertainty_communication.py`

Honest confidence expression:
- 5 confidence levels:
  - CERTAIN (90-100%): "I'm very sure"
  - PROBABLY (75-89%): "I'm pretty sure"
  - MAYBE (50-74%): "I think but not 100% sure"
  - UNSURE (20-49%): "I'm not very sure"
  - DONT_KNOW (0-19%): "I don't know"
- Age-appropriate phrasing
- Refusal triggers (medical, dangerous, legal, self-harm)
- AVA's honesty guideline

**How it works:**
1. Get confidence score
2. Map to level
3. Select age-appropriate phrase
4. Add to response
5. Suggest verification if uncertain
6. Refuse if dangerous/illegal

---

### 12. **ENHANCED SAFETY SYSTEM**
**File:** `src/avaos/enhanced_safety.py`

Content filtering for child safety:
- 8 harmful categories:
  - Self-harm
  - Abuse
  - Drugs
  - Alcohol
  - Sexual content
  - Violence
  - Illegal activity
  - Phishing/scams
- URL whitelist (only safe domains):
  - github.com
  - wikipedia.org
  - khan academy
  - code.org
  - scratch.mit.edu
  - And 15+ others
- Phishing/scam pattern detection
- Content sanitization (redact keywords)
- Security logging

**How it works:**
1. Scan for harmful content
2. Check URLs against whitelist
3. Detect phishing patterns
4. Sanitize/redact if needed
5. Log security event
6. Block if critical

---

### 13. **SECURITY MONITORING**
**File:** `src/avaos/security_monitor.py`

Centralized security event logging:
- Event types:
  - Rate limit violations
  - Content blocked
  - Injection attempts
  - Failed auth
  - Errors
- Severity levels: info, warning, critical
- Critical event alerting
- Security reports for parent
- Threat analysis & frequency tracking

**How it works:**
1. Log all security events
2. Assign severity
3. Alert on critical events
4. Generate weekly reports
5. Track threat patterns
6. Provide recommendations

---

### 14. **ENCRYPTION SYSTEM**
**File:** `src/avaos/encryption.py`

Data protection at rest:
- AES encryption via Fernet
- Automatic key generation/management
- Key stored at ~/.ava_os/.encryption_key
- Encrypted file storage
- Encrypted JSON handling
- Conversation history encryption

**How it works:**
1. Generate encryption key
2. Encrypt sensitive data
3. Store encrypted data
4. Decrypt on retrieval
5. Key management
6. Automatic key rotation option

---

### 15. **MEMORY SYSTEM**
**File:** `src/avaos/memory.py`

Conversation history & context:
- Immutable conversation history (JSONL format)
- ConversationTurn dataclass (timestamp, role, text, topic)
- Append-only log (can't delete/modify)
- Session management
- Context window management
- Long-term memory for learning patterns

**How it works:**
1. Record each turn (user/AVA)
2. Timestamp each message
3. Append to JSONL log
4. Retrieve for context
5. Analyze patterns over time
6. Inform recommendations

---

### 16. **PWA (PROGRESSIVE WEB APP)**
**File:** `web/index.html`, `web/sw.js`, `web/manifest.json`

Mobile app experience:
- Installable (add to home screen)
- Offline capable (service worker)
- Network-first caching strategy
- Push notifications support
- Responsive design (mobile/tablet/desktop)
- Dark mode support
- App icon & theme colors

**How it works:**
1. Service worker caches assets
2. Network requests first
3. Fallback to cache if offline
4. User installs as app
5. Works like native app
6. Syncs when online

---

### 17. **PARENT DASHBOARD**
**File:** `web/parent-dashboard-secure.html`

Monitoring & analytics interface:
- Password-protected login (default: ava2024)
- Session-based auth (1-hour auto-logout)
- Today's activity view
- Overall progress tracking
- Learning streak display
- Subject mastery charts
- Personalized recommendations
- **Spiritual development tracking**
- Protective factors assessment
- Data export capability
- Settings management

**How it works:**
1. Parent logs in with password
2. Views dashboard stats
3. Sees learning progress
4. Monitors spiritual development
5. Reviews recommendations
6. Exports data
7. Auto-logouts after 1 hour

---

### 18. **DIARY SYSTEM**
**File:** `web/diary.html`

Private journaling (completely local):
- Password protected (default: diary123)
- Browser localStorage (no cloud)
- Mood tracking (8 emojis)
- Date-stamped entries
- Filter by mood
- Statistics dashboard
- Delete individual entries
- Session logout
- Change password anytime

**How it works:**
1. Lock screen with password
2. Unlock to write/read
3. Save entries locally
4. Filter & review
5. Logout to lock again
6. Zero token cost

---

### 19. **CURRICULUM GENERATOR**
**File:** `src/avaos/curriculum_generator.py`

Dynamic curriculum creation:
- Generates kumon_curriculum.json
- 5 subjects with prerequisites
- Unlocking system
- Difficulty progression
- Estimated days per concept
- Sample questions
- Age recommendations

**How it works:**
1. Define curriculum structure
2. Generate JSON file
3. Save to ~/.ava_os/curriculum/
4. Kumon tracker loads it
5. Used for daily topics
6. Enables prerequisites/unlocking

---

### 20. **API SERVER**
**File:** `scripts/kumon_server.py`

Flask backend (Heroku):
- 10+ endpoints:
  - `/api/topic/today` - Daily learning topic
  - `/api/progress/all` - All progress
  - `/api/progress/subject/<subject>` - Subject progress
  - `/api/mastery/report` - Mastery details
  - `/api/attempt` - Record attempt
  - `/api/chat` - Chat with AVA
  - `/api/sync` - Data synchronization
  - `/api/faith/lessons/<age>` - Faith curriculum
  - `/api/faith/summary/<age>` - Faith progress
  - `/api/security/status` - Security info
  - `/api/health` - Health check
- Rate limiting (100 req/hour)
- API key authentication
- Security headers (CSP, HSTS, etc.)
- CORS enabled

**How it works:**
1. PWA makes API calls
2. Server processes requests
3. Returns JSON responses
4. Manages Kumon data
5. Handles Claude API calls
6. Returns structured data

---

## **How They Work Together**

```
┌─────────────────────────────────────────────────────────────┐
│                     DAUGHTER'S EXPERIENCE                    │
│  Chats with AVA → See Progress → Write in Private Diary     │
└────────┬────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING LOOP (Daily)                     │
│                                                               │
│  1. Kumon selects daily topic (rotates through 5 subjects)  │
│  2. Adaptive difficulty picks easy/medium/hard               │
│  3. She practices & answers questions                        │
│  4. Spaced repetition schedules reviews                      │
│  5. Learning recommendations suggest what's next             │
│  6. Hallucination prevention checks AVA's responses          │
│  7. Safety system filters harmful content                    │
│  8. Conversation stored in memory                            │
│  9. Diary stores private thoughts (no tokens!)               │
│  10. Progress saved to local storage & server                │
└────────┬────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────┐
│                  PARENT'S VIEW (Dashboard)                   │
│                                                               │
│  • Today's activity (topic, time, accuracy)                  │
│  • Overall mastery progress                                  │
│  • Learning streak counter                                   │
│  • Subject-by-subject progress                               │
│  • Personalized recommendations                              │
│  • Spiritual development progress                            │
│  • Protective factors against addiction                      │
│  • Security events & monitoring                              │
│  • Data export for backup                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## **Data Flow Diagram**

```
DAUGHTER'S DEVICE (Phone/Tablet)
├── PWA (index.html)
│   ├── Kumon UI (shows today's topic)
│   ├── Chat UI (talks with AVA)
│   ├── Progress Dashboard
│   └── Links to Diary
│
├── Service Worker (sw.js)
│   ├── Caches assets
│   └── Works offline
│
└── Local Storage
    ├── Progress data
    ├── Diary entries (password protected)
    └── Session info

         ↕ (API calls)

SERVER (Heroku Backend)
├── Flask API Server
│   ├── /api/topic/today
│   ├── /api/attempt (records learning)
│   ├── /api/progress/* (gets stats)
│   ├── /api/faith/* (faith curriculum)
│   └── /api/chat (Claude integration)
│
├── Kumon Tracker
│   ├── Daily topic selection
│   ├── Progress tracking
│   ├── Mastery calculation
│   └── Prerequisite unlocking
│
├── Adaptive Difficulty
│   ├── Tracks accuracy
│   └── Adjusts difficulty
│
├── Spaced Repetition
│   ├── Schedules reviews
│   └── Adjusts intervals
│
├── Learning Recommendations
│   ├── Prioritizes next concepts
│   └── Balances subjects
│
├── Hallucination Prevention
│   ├── Extracts claims
│   ├── Verifies facts
│   └── Scores confidence
│
├── Safety System
│   ├── Filters harmful content
│   ├── Checks URLs
│   └── Logs events
│
├── Faith Curriculum
│   ├── Age-appropriate lessons
│   ├── Tracks protective factors
│   └── Records prayers
│
└── Memory System
    ├── Stores conversation history
    └── Tracks patterns

         ↕ (Claude API calls)

CLAUDE AI (anthropic.com)
├── Generates responses
├── Understands context
├── Adapts to learning level
└── Provides guidance

         ↕ (Parent access)

PARENT'S DASHBOARD
├── Login (password protected)
├── View progress
├── Monitor safety
├── Export data
└── Auto-logout (1 hour)
```

---

## **Summary: All 20 Systems**

| # | System | Purpose | Files |
|---|--------|---------|-------|
| 1 | Hallucination Prevention | Prevent false information | hallucination_prevention.py |
| 2 | Kumon Curriculum | Daily learning structure | kumon.py |
| 3 | Adaptive Difficulty | Auto-adjust challenge | adaptive_difficulty.py |
| 4 | Spaced Repetition | Scientifically-proven reviews | spaced_repetition.py |
| 5 | Learning Recommendations | Smart "what to study next" | learning_recommendations.py |
| 6 | Financial Literacy | Money education (ages 10-18) | financial_literacy.py |
| 7 | Faith & Character | Spiritual development (ages 10-18) | faith_curriculum.py |
| 8 | Budget Tracker | 50/30/20 rule tracking | budget_tracker.py |
| 9 | Claim Extractor | Identify statements to verify | claim_extractor.py |
| 10 | Fact Verification | Database of verified facts | fact_verification.py |
| 11 | Uncertainty Communication | Honest confidence expression | uncertainty_communication.py |
| 12 | Enhanced Safety | Content filtering & URL whitelist | enhanced_safety.py |
| 13 | Security Monitoring | Event logging & alerts | security_monitor.py |
| 14 | Encryption | Data protection at rest | encryption.py |
| 15 | Memory System | Conversation history | memory.py |
| 16 | PWA | Mobile app experience | index.html, sw.js, manifest.json |
| 17 | Parent Dashboard | Monitoring interface | parent-dashboard-secure.html |
| 18 | Diary System | Private journaling (local) | diary.html |
| 19 | Curriculum Generator | Generate curriculum JSON | curriculum_generator.py |
| 20 | API Server | Flask backend (Heroku) | kumon_server.py |

---

## **Technology Stack**

**Frontend:**
- HTML5, CSS3, JavaScript (vanilla)
- PWA (Progressive Web App)
- Service Worker (offline support)
- Local Storage (diary, progress)

**Backend:**
- Python 3.8+
- Flask (web server)
- Heroku (hosting)

**AI:**
- Claude API (Anthropic)
- Token counting for cost tracking

**Hosting:**
- Netlify (frontend PWA)
- Heroku (backend API)
- Both FREE tier

**Data:**
- JSON (curriculum, config)
- JSONL (conversation history)
- SQLite/JSON (local)
- Encrypted storage (Fernet)

---

This is the **complete architectural overview** of AVA OS - all 20 systems working together to create a comprehensive learning platform for your daughter.

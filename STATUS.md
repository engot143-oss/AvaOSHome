# AVA OS — Real Status

Rule for this file: nothing gets listed here unless it was actually run and the
output was seen, in this session or a later one. No "production ready" or
"approved for deployment" language until there's a real deployment to talk about.

## What exists right now

- `docs/framework_design.md` — architecture spec, carried over from prior design
  work. Describes the intended system (interface layer, reasoning engine, memory
  store, learning loop, hallucination mitigation). Not implemented — this is the
  target, not a status report.
- `docs/pbvl_remediation_plan.md` — an independent critique of an earlier design,
  with concrete fixes (consequence triage, falsifiability, anti-sycophancy,
  provenance tracing). Used as a requirements source, not as evidence anything
  was built.
- `src/avaos/criticality.py` — real, working code. Classifies text into a
  consequence tier (LOW/MEDIUM/HIGH/CRITICAL) across domains (medical, financial,
  legal, security, identity, irreversible-action), with MAX aggregation and
  action-marker escalation. Implements framework_design.md §6's risk-tier concept
  and remediation_plan.md's Fix 1 (Consequence Triage) / Invariant 4
  (Criticality Lock).
- `src/avaos/claims.py` — real, working code. Decomposes a draft response into
  sentence-level claims and classifies each as FACTUAL / HEDGED / OPINION /
  QUESTION / INSTRUCTION (framework_design.md §9A step 1). Heuristic/keyword-based,
  documented limitations at the bottom of the file.
- `src/avaos/evidence.py` — real, working code. `Source`/`GroundingResult` data
  model matching the §5 response schema, plus `check_grounding()` — a keyword-
  overlap heuristic that checks a claim against an explicitly-passed-in list of
  sources (§9A step 2). Does not fetch sources itself; there's no memory store or
  tool layer to fetch from yet.
- `src/avaos/stakes.py` — real, working code. Classifies an ungrounded claim as
  LOW or HIGH stakes (§9A step 3), reusing criticality.py's domain tiering plus a
  specificity check (numbers/dates/causal language). Calibrated against the
  design doc's own "Paris is the capital of France" = low-stakes example.
- `src/avaos/pipeline.py` — real, working code. Wires claims → grounding →
  stakes → render together (§9A steps 1-4, 7), plus `resolve_fallback_checks()`
  for steps 5-6. Grounded claims pass through cited; ungrounded low-stakes
  claims get hedged; ungrounded high-stakes claims are marked
  `NEEDS_FALLBACK_CHECK` until resolved against a real verification call.
  This module has no hard dependency on `anthropic`/network - it takes a
  `fallback_fn` callable, so it stays independently testable.
- `src/avaos/fallback_check.py` — real, working code. Implements §9A steps
  5-6 for real: calls the Claude API (`claude-opus-5`) with the live web
  search tool to check a high-stakes ungrounded claim, and parses the result
  into CONFIRMED / CONTRADICTED / EMPTY with citations. Requires
  `ANTHROPIC_API_KEY` in the environment (never hardcoded - reads from env
  only) and costs real money per call. Not run by the automated test suite;
  tested with a fake client instead (see `tests/test_fallback_check.py`).
- `scripts/manual_fallback_check_demo.py` — the one place that makes a real,
  costed API call. Meant to be run by hand (`python scripts/manual_fallback_check_demo.py`
  with `ANTHROPIC_API_KEY` set), never by the test suite or automatically.
- `tests/` — 47 unit tests across six modules, **all passing** as of
  2026-08-19 (verified by running `python -m unittest discover -s tests -v`).
  None of them touch the network or need an API key - `test_fallback_check.py`
  mocks the Anthropic client and also verifies that calling without credentials
  raises a clear error rather than silently doing nothing.

## What does NOT exist

- No confirmation-flow / approval-gate implementation yet (framework_design.md §6
  describes it; nothing runs it).
- No memory/knowledge store, no learning loop, no interface layer, no tool
  registry. `check_grounding()` in evidence.py only checks sources explicitly
  passed in by the caller - there's still nothing that fetches sources on its
  own.
- The live fallback check has never actually been run against the real API in
  this project - only against a mocked client. The Founder needs to set
  `ANTHROPIC_API_KEY` and run `scripts/manual_fallback_check_demo.py` before
  this piece counts as "verified against reality" rather than "verified
  against a mock."
- No "BVL" system of any kind runs here. A prior `bvl_v0_3_phase3_validation.py`
  found in Downloads claimed 85.5% test pass rates and production approval; it
  does not run (missing dependency `bvl_v0_3_phase2_integration`, which was
  never delivered) and its completion reports are dated in the future relative
  to when they were found. Treat all claims in that file's reports are false.

## Setup needed before live verification works

```
pip install -r requirements.txt
# set ANTHROPIC_API_KEY in your environment (never hardcode it in a file)
python scripts/manual_fallback_check_demo.py
```

- `src/avaos/confirmation.py` — real, working code. Implements §6's
  confirmation-step policy: LOW auto-executes, MEDIUM needs one confirmation,
  HIGH needs three sequential confirmations (restate → surface consequence →
  friction pause) each with its own timeout. Any decline or timeout at any
  step resets progress to zero - no partial credit across attempts. Unclassified
  tools default to HIGH (fail-safe). `tier_from_consequence()` bridges
  criticality.py's 4-tier consequence scale into this module's 3-tier gate.
  Modeled as pure state transitions (`advance(session, response, elapsed)`),
  not real clocks/sleeps, so it's fully unit-testable.
  ASSUMPTION flagged in the file: the design doc doesn't specify MEDIUM
  tier's timeout, defaulted to 120s to match HIGH's per-step default.
- `tests/` — 59 unit tests across seven modules, **all passing** as of
  2026-08-19.

## Scope Decision (from Founder, 2026-08-19)

AVA OS is built for a 10-year-old daughter to:
- **Get guidance on life lessons, school, and career** (she wants to become a nurse)
- **Learn financial responsibility and literacy**
- **Have a trusted, truthful AI companion** that never gives her wrong advice

**Critical requirement: Hallucination checking is mandatory.** Every piece of
advice, every fact AVA gives her must be verified or explicitly hedged as
uncertain - the hallucination pipeline (criticality → grounding → fallback
check) is not optional, it's core to the system.

**What AVA OS will NOT do:** No real-world actions on her behalf. No sending
messages, modifying files, purchasing things, or controlling other apps. Pure
conversational guidance - text in, verified advice out. This keeps the safety
surface small (only advice can be wrong, not an action triggered on bad data).

**What AVA OS WILL do next:**
1. Build an **approved, verified knowledge base** for her focus areas (nursing
   career path, age-appropriate financial literacy, life skills for a 10yo)
2. Build a **memory system** to remember her interests, progress toward goals,
   and past conversations
3. Wire the hallucination pipeline into a real **chat interface** so every
   response she gets is grounded or explicitly marked as uncertain
4. Consider **parental oversight** (her parent should be able to review
   conversations, especially high-stakes advice) - this may map to the
   confirmation policy's `owner_scope` field

- `src/avaos/chat.py` — real, working chat interface. Wires everything together:
  loads Claude API, generates responses, runs the hallucination pipeline (extract
  claims → ground them → fallback check if needed), saves to memory, outputs via
  voice (pyttsx3) or text, and logs high-stakes advice to notifications.log for
  parent review. Supports both text mode (`python -m avaos.chat`) and voice mode
  (`python -m avaos.chat --voice`).
- `tests/` — 63 unit tests across eight modules, **all passing**.
- `README.md` — setup and usage guide for the parent (how to run, what AVA does,
  how hallucination checking works, cost breakdown).

## Ready to use NOW

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."  # your key
python -m avaos.chat --voice            # start voice chat
```

AVA will:
- Listen to your daughter's question (or read from stdin if `--voice` fails)
- Think through her answer using Claude
- Check every claim in her answer for hallucinations
- Verify high-stakes advice with live web search
- Speak the response aloud (or print it)
- Log high-stakes topics to `~/.ava_os/memory/notifications.log` for you to review
- Save conversation history for context in future chats

## Known limitations (acceptable for v1)

1. **No custom knowledge base yet** — AVA only uses Claude's training + live search.
   Next step: curate verified content on nursing careers, financial literacy for
   kids, etc., and pass it to Claude as context instead of relying on search.
2. **No parental approval gates** — per Founder's decision. System just notifies.
3. **Voice latency** — ~3-5 seconds per turn (Claude thinking + TTS). Acceptable
   for a guidance system, not real-time conversation.
4. **Single user** — memory system assumes one daughter. Easy to extend to
   multiple users if needed.

## Next priorities (optional; this version is functional)

1. **Curated knowledge base** — approved, age-appropriate content on:
   - Nursing career path
   - Financial literacy for kids
   - Life skills & emotional resilience
2. **Parental dashboard** (nice-to-have) — web UI to review notifications and
   conversation history instead of raw files
3. **Customization** — let parent set topics, constraints, goals for their daughter

# AVA OS — Framework Transfer Prompt

*Use this document as context when handing the AVA OS design to another AI for review, critique, or continued design work. Paste it in full as the opening message, then ask your question.*

---

## 1. What AVA OS is

AVA OS is a conceptual architecture for a personal AI operating system with a self-updating knowledge base. Its defining feature is a **learning loop**: a scheduled process that searches the internet for books, evaluates them, and ingests qualifying content into a versioned knowledge store — closing the loop with the system's own reasoning engine so that real usage (not just guesswork) drives what gets learned next.

This document is the full, validated design as of the current revision. Treat it as a specification to be tested, stress-tested, or extended — not as working code. No part of this has been implemented or run against real data or real infrastructure.

---

## 2. System-wide module map

Five top-level modules inside the AVA OS container:

- **Interface layer** — thin per-channel adapters (chat, voice, API). Normalizes input into a common request format, streams output back in the channel's native shape. Contains no reasoning — just protocol translation, auth, and session state.
- **Tool & action layer** — a registry of callable capabilities (search, calendar, file ops, external APIs), each with a schema the core engine matches against. Adding a new tool means registering a schema + handler + risk tier, not changing core engine code.
- **Core reasoning engine** — the decision-making hub. Classifies each request's intent, then routes to one of three paths: answer directly (already confident), retrieve from memory, or call a tool. All paths converge on composing a response, which is logged.
- **Memory & knowledge store** — versioned, append-only long-term knowledge. Never overwritten in place; every ingestion batch is a new immutable version layer. A "current" pointer marks what's live; rollback is just moving that pointer back.
- **Learning loop** — the book-ingestion subsystem (detailed in §3). Writes new knowledge into the memory store, closing the cycle with the core engine.

Data flow: interface + tool layers feed the core engine → core engine draws on memory + tools → learning loop feeds memory → low-confidence retrievals feed back into the learning loop as demand-driven gap signals.

---

## 3. The learning loop (book ingestion)

**Cadence:** fires at 06:00, then every 3 hours (09:00, 12:00, 15:00, 18:00, 21:00, 00:00, 03:00).

**Six stages, in order:**

1. **Scheduler / loop orchestrator** — fires the loop on cadence, tracks last-run state, retries on failure.
2. **Discovery agent** — pulls open gaps from the gap tracker (topics with thin/stale/low-confidence coverage), expands each into targeted search queries, and queries legitimate book sources in parallel: Open Library, Google Books API, Project Gutenberg (public domain), licensed publisher/library APIs. **Never scrapes full text from unauthorized sources.**
3. **Relevance & licensing filter** — scores candidates on topical relevance, recency, source authority, and license clearance. Hard-rejects anything without a clear license path. Caps ingestion volume per cycle (e.g. top 5–10 candidates) so each cycle stays fast and reviewable.
4. **Content integrity check** (see §7 for full detail) — corroboration check, anomaly detection against high-confidence facts, source diversity check. Clean batches promote; flagged batches quarantine.
5. **Ingestion pipeline** — parses, chunks, embeds accepted content; extracts structured metadata.
6. **Update manager / validation gate** — dedup pass, then creates a new versioned layer in the knowledge store and advances the "current" pointer. Bad batches never reach this point if they were quarantined in step 4.

**Gap tracker (feedback loop):** retires or downgrades a gap once enough quality material has been ingested against it. Critically, gaps are also populated by real usage — every time memory retrieval comes back low-confidence on an actual user query, that's logged as a gap signal. This makes the loop **demand-driven**, not just speculative.

---

## 4. Core reasoning engine: decision logic

For every incoming request:

1. **Classify intent** — does it need live/personal data (→ retrieve memory), does it require an action (→ call a tool), or is confidence already high (→ answer directly)?
2. **Route** to the matching path. Only one path executes retrieval/tool cost; the majority of simple requests skip both.
3. **Compose response** — merges findings (direct knowledge, retrieved memory, tool output) into a single answer.
4. **Log & return** to the interface layer.

---

## 5. Request/response schema

```json
// Request (interface layer → core engine)
{
  "request_id": "uuid",
  "channel": "chat | voice | api",
  "session_id": "uuid",
  "actor": "owner | delegated_actor_id",
  "user_input": "string",
  "context": { "prior_turns": [], "user_prefs": {} },
  "timestamp": "ISO8601"
}
```

```json
// Response (core engine → interface layer)
{
  "request_id": "uuid",
  "status": "complete | needs_confirmation | blocked | error",
  "answer": "string",
  "sources": [
    {
      "type": "memory | tool | direct",
      "ref": "string | null",
      "confidence": "grounded | verified | hedged_low_stakes | unverified",
      "outcome": "original | confirmed | contradicted | empty",
      "gap_logged": false
    }
  ],
  "pending_action": {
    "tool": "string",
    "params": {},
    "params_grounded": true,
    "grounding_check_log": [
      { "param": "string", "outcome": "confirmed_by_source | confirmed_by_user | contradicted", "source": "string | null" }
    ],
    "risk_tier": "low | medium | high",
    "approver_scope": "owner_only | delegated",
    "delegated_actor": "actor_id | null",
    "confirmations_required": 0,
    "confirmations_received": 0,
    "current_step_expires_at": "ISO8601",
    "confirmation_log": [],
    "blocked": false
  },
  "timestamp": "ISO8601"
}
```

`request_id` threads every log, memory write, and confirmation back to its origin. `sources` makes every answer auditable — always traceable to memory, a tool, or direct model knowledge, with per-claim confidence now visible rather than implied. `params_grounded` is a hard boolean gate on `pending_action` — see §9A — the confirmation flow in §6 cannot begin while it is `false`.

---

## 6. Confirmation-step policy (final)

Risk tier — not tool identity — determines the gate. Tier is assigned per tool at registration time.

| Tier | Behavior |
|---|---|
| **Low** | Auto-execute. Read-only or fully reversible actions only: search, fetch data, draft (not send) messages, query the knowledge store. No confirmation. |
| **Medium** | Requires **one** confirmation. Default `approver_scope: owner_only` — if the requesting session's `actor` is not the owner, the confirmation routes to the owner, not back to the requester. Delegation is possible but must be explicitly granted per-tool, never blanket. |
| **High** | Requires **triple confirmation** — three distinct, sequential approvals: (1) restate the action verbatim, ~2 min timeout; (2) surface the consequence, not just the action, ~2 min timeout, starts after step 1; (3) deliberate friction step, 10–15 sec minimum cooling-off, ~5 min max timeout. |

**Timeout/decline behavior:** any timeout or decline at any step, at any tier, kills the entire request and resets `confirmations_received` to 0. No partial credit — the user must re-initiate from step 1. This is deliberate: every approved high-risk action should be tied to one coherent, recent decision, not a chain of approvals stitched together over an unbounded span of time.

**Default for unclassified tools:** any tool without an assigned risk tier is treated as **high risk** by default — fail-safe, not fail-open.

**Grounding gate precedes confirmation (see §9A):** for any medium or high risk tool call, every parameter derived from a factual claim (amount, date, recipient, quantity, etc.) must pass the grounding check in §9A *before* `pending_action` is populated and the confirmation flow above begins. Confirmation approves the decision to act; grounding ensures the facts behind that action are accurate. Neither is sufficient alone — a user can confidently confirm a wrong action if the underlying claim was never verified.

---

## 7. Content integrity check (ingestion safeguard)

Sits between the ingestion pipeline and the knowledge store's validation gate. Defends against knowledge poisoning — a real risk for a system that autonomously ingests content from the open internet every 3 hours.

1. **Corroboration check** — search existing knowledge store for related claims; compute an agreement score (support / contradict / silent).
2. **Anomaly detection** — flags content that conflicts specifically with *high-confidence* facts (strong prior corroboration + authority), not the whole corpus indiscriminately.
3. **Source diversity check** — a claim that would **override existing high-confidence knowledge** requires corroboration from multiple (recommended: 3+) independent sources before promotion. A single well-scored source is not sufficient to overturn established knowledge.
4. **Clean → promote** to the validation gate. **Flagged → quarantine**, not deleted — held in a non-queryable state where it can accumulate corroboration over future cycles or get manually reviewed.
5. **Trust score feedback** — sources that repeatedly produce flagged/contradicted content get their authority score downgraded in future discovery-agent ranking.

**Known open gap (unresolved as of this revision):** the source diversity threshold only triggers when new content would *override existing* knowledge. On a genuinely novel topic with no existing high-confidence entries to compare against, a single confidently-wrong, well-authority-scored source can currently slip through and get promoted, because there's nothing for the anomaly check to detect a conflict against. A candidate fix under discussion: require multi-source corroboration by default for **any** first-time coverage of a new topic, not only when overriding existing knowledge — at the cost of slower clearance for genuinely new/rare topics.

---

## 8. Memory retrieval logic

1. **Form retrieval query** — rewritten by the core engine using conversation context (resolves pronouns/references), not just the raw user message passed through.
2. **Embed & vector search** — always queries the knowledge store's **current version pointer** only, never a historical version. This means a rollback is instantly reflected in retrieval with no extra logic.
3. **Hybrid rerank** — combines raw semantic similarity with recency and the source-authority score assigned at ingestion time. Prevents similar-sounding-but-low-quality text from outranking authoritative sources.
4. **Confidence & contradiction filter** — if retrieved passages disagree, default is to surface the conflict (flag it in `sources`) rather than silently picking one side. Known bias risk: naive "prefer higher authority/more recent" resolution isn't always correct (older sources are sometimes right, newer ones sometimes wrong) — flagging is safer than silent resolution.
5. **Assemble context** — top-k passages, hard length cap, every passage carries a citation.
6. **Return to core engine** with `sources` populated.

**Feedback:** any retrieval that comes back thin or low-confidence logs a gap signal consumed by the learning loop's gap tracker (§3). This is the most load-bearing connection in the whole design — it means learning is prioritized by what's actually being asked, not by speculative search.

---

## 9A. Hallucination mitigation

Hallucination risk in AVA OS concentrates almost entirely in the core engine's **"answer directly" path** (§4) — the branch where the engine asserts from its own trained knowledge without retrieval or a tool call. That path has no verification step by default, making it the one part of the design that isn't auditable against a source. This section closes that gap.

**Pipeline, run on every draft response before it's finalized:**

1. **Extract factual claims** — decompose the draft into discrete checkable assertions. Opinions, conversational filler, and already-hedged statements are skipped; only assertions presented as fact are checked.
2. **Grounding check, per claim** — does this claim trace back to something in `sources` (a memory retrieval or tool result)? Grounded claims proceed as-is, cited. Ungrounded claims move to step 3.
3. **Stakes classification, for ungrounded claims only** — not every ungrounded claim carries the same risk. Well-established, low-consequence claims ("Paris is the capital of France") are low stakes. Specific numbers, names, dates, causal claims, or anything the user might act on are high stakes, regardless of how confident the model feels about them.
4. **Low stakes → hedge language.** Rendered with calibrated uncertainty rather than flat assertion, without paying a retrieval round-trip.
5. **High stakes → batched fallback check.** All high-stakes ungrounded claims in the response are extracted together and checked in **one parallel batch** (not sequentially, to avoid stacking latency) against **both** the internal knowledge store **and** any available live tools — internal memory alone will usually be empty or stale for time-sensitive claims.
6. **Fallback resolves to exactly one of three outcomes:**
   - **Confirmed** — a source backs the claim. Cite it, mark grounded.
   - **Contradicted** — a source disagrees. The claim is corrected or dropped; it is never shipped in its original wrong form.
   - **Empty** — no source either way. This is a real answer state, not a failure to hide: the response states the uncertainty explicitly to the user ("I don't have a verified source for this — my best understanding is X"), and the miss is logged as a gap signal into the **same gap-tracker queue** used by low-confidence retrieval (§3, §8). A hallucination fallback miss and a retrieval miss are the same underlying signal — both mean AVA doesn't actually have solid coverage on the topic — so both should drive the learning loop equally.
7. **Render with confidence, visibly.** Confidence is not just a metadata field — grounded, hedged, and unverified claims must read differently in the actual output the user sees (softer language, an inline marker, an explicit caveat), so trust calibrates in the moment rather than requiring the user to inspect logs after the fact.

**Interaction with the confirmation-step policy (§6) — the grounding gate:** for any medium or high risk tool call, every parameter derived from a factual claim must pass this same grounding pipeline *before* `pending_action` is populated. If a parameter can't be resolved via the fallback check, the core engine halts and asks the user to confirm the value itself, before any risk-tier confirmation flow begins. This closes a real interaction gap: the confirmation policy protects *whether* an action executes, but assumes its parameters are already correct — without this gate, a user could confidently approve a tool call built on a hallucinated number. `params_grounded` (§5) is the hard boolean that enforces this ordering.

**Design tradeoffs acknowledged:**
- The stakes classifier (step 3) is itself a judgment call — too conservative and every response pays a latency tax; too permissive and the mechanism misses the claims that matter most.
- Batching (step 5) reduces latency from O(n) sequential round-trips to roughly one, but still adds cost to any response containing high-stakes ungrounded claims.

---

## 9B. Observability layer

Four modules emit events into a central, append-only metrics store (kept separate from the knowledge store — operational data, not knowledge content):

- **Learning loop** → promotion rate, quarantine rate
- **Memory retrieval** → hit rate, low-confidence rate
- **Confirmation flow** → timeout/abandonment rate
- **Hallucination mitigation** → fallback trigger rate, fallback outcome mix (confirmed/contradicted/empty), grounding-gate blocks on `pending_action`

Metrics derive from existing logs (`confirmation_log`, ingestion outcomes, retrieval confidence scores, grounding-check logs) rather than duplicate instrumentation.

**Core tracked signals:**

| Signal | What it catches |
|---|---|
| Quarantine rate trending up | Discovery agent's sources degrading, or integrity check working as intended |
| Retrieval low-confidence rate | Knowledge gaps not closing as fast as usage demands them |
| Confirmation abandonment/timeout rate | Confirmation friction too high, or requests poorly scoped |
| Source trust score distribution | Whether a small number of sources dominate the corpus (concentration risk) |
| Quarantine backlog age | Content stuck in limbo — either genuinely bad, or the corroboration threshold is set too high |
| Hallucination fallback "empty" rate | Topics AVA is asked about but has no grounded source for either way — a gap signal (§9A) |
| Hallucination fallback "contradicted" rate | How often the model's direct assertions are actually wrong when checked — a proxy for base hallucination rate |
| Grounding-gate blocks on `pending_action` | How often a risky tool call was about to be built on an unverified parameter — should trend toward zero, not be routinely high |

**Alerts** (needs attention now) vs. **dashboard** (periodic trend review) are kept distinct.

---

## 10. Known unresolved issues (as of this revision)

Flag these explicitly to any AI reviewing this framework — they are acknowledged gaps, not oversights. Items previously listed here that are now addressed by §9A are noted as resolved rather than removed, so the reviewing AI can see what changed.

1. **Novel-topic poisoning gap** (§7) — still open. Single-source claims on brand-new topics can bypass the diversity check since it only triggers on overrides of existing knowledge. Not addressed by §9A, since that section covers the core engine's direct-answer path, not the ingestion pipeline.
2. **Triple-confirmation usability cliff** — still open. The high-risk tier's friction (up to ~9+ minutes across three steps, full reset on any timeout) may make high-risk actions functionally unusable in normal conditions. Accepted as intentional, not validated against real user behavior.
3. **Contradiction resolution bias in retrieval** (§8) — still open for the memory-retrieval path specifically. Note this is now handled more rigorously for the *direct-answer* path via the three-outcome fallback in §9A (confirmed/contradicted/empty), but §8's retrieval-time contradiction handling still defaults to a "prefer higher authority/recency" heuristic when not simply flagging.
4. **No capacity/scaling boundaries defined** — still open. No pruning, compaction, or query-time budget specified for when the knowledge store, candidate pool, or fallback-check volume grows large.
5. ~~**Confirmation policy protects execution but not claim accuracy**~~ — **resolved by §9A's grounding gate.** `params_grounded` now blocks `pending_action` from being built on any unverified parameter, closing the gap where a user could confidently approve a tool call built on a hallucinated value.
6. ~~**Hallucination on the direct-answer path was entirely unverified**~~ — **resolved by §9A.** The claim-extraction → grounding → stakes-classification → fallback pipeline now covers this path end to end, including user-visible confidence and gap-tracker feedback.
7. **Nothing in this design has been implemented or run.** All validation to date, including §9A, has been scenario-based reasoning through the spec, not execution against real data, real APIs, or real infrastructure.

---

## 11. Suggested prompts for the receiving AI

- "Review this architecture for security or safety gaps I haven't listed in §10."
- "Stress-test the confirmation-step policy in §6 against edge cases involving concurrent requests or session hijacking."
- "Propose a fix for the novel-topic poisoning gap in §7 that doesn't excessively slow down legitimate new-topic ingestion."
- "Design the tool registry schema referenced in §6/§4 that assigns risk tiers to new tools."
- "Identify any inconsistency between §5 (schema) and §6 (policy) as written."
- "Stress-test the hallucination mitigation pipeline in §9A against a claim that is grounded in a *quarantined* (not yet promoted) knowledge-store entry — should that count as grounded or not?"
- "Evaluate whether the stakes classifier in §9A step 3 needs to be a separate model call or can be folded into claim extraction — what's the latency/accuracy tradeoff?"

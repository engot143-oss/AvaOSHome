# AVA OS 4.2 — Selective Routing & Persistent State Architecture Patch

Status: APPROVED architecture policy
Date: 2026-11-02
Scope: AVA OS 4.x forward architecture; does not downgrade or overwrite existing 4.2 artifacts.

## Purpose
Apply the current AVA OS research findings without adding a new major subsystem. The goal is to improve efficiency, persistence, and governed coordination while preserving existing authority, Agent7 safeguards, Dot scope, Context Bridge integrity, and current working components.

## Governing decision
AVA OS uses the smallest capable authorized worker set for each task. Worker selection is dynamic at task/batch boundaries. Persistent task state remains external to workers. Governance remains external to the worker/model being governed.

## Core flow
Task -> Glow/Agent7 analysis -> policy gate -> choose smallest capable authorized worker -> execute -> verify -> checkpoint -> choose next worker or stop.

This replaces fixed "run every available agent" behavior as the default policy. Parallel fan-out is opt-in and must have a measurable reason.

## Policy 1 — Dynamic worker selection
Before dispatch, Glow evaluates:
- task type and required capability
- authorized scope and action risk
- unresolved work / evidence gaps
- expected cost or credit use
- local/cloud availability
- whether a worker is necessary at all

Selection rule: choose zero or the smallest number of workers that can satisfy the task and verification requirement.

No worker may expand its own authority. Selection does not bypass AVA OS approvals, host gates, STOP behavior, or Agent7 scope checks.

## Policy 2 — Persistent state outside workers
Authoritative task state must not depend on one model session or worker process.

Minimum checkpoint record:
- task/incident ID
- current state/status
- authorized scope
- selected worker(s)
- evidence references
- decision/approval references when applicable
- attempt/cycle number
- last verified outcome
- unresolved items/uncertainty
- next permitted transition
- timestamp and integrity reference

Workers consume state and return results. They do not own authoritative state.

## Policy 3 — Bounded coordination
Default: sequential execution or one selected worker.

Limited parallel execution is allowed only when at least one is true:
- independent subtasks can be evaluated concurrently
- diversity is explicitly required for comparison/red-team work
- latency benefit is material and resource use is acceptable

Parallel work must still converge through one governed verification/checkpoint step.

## Policy 4 — External governance
Governance stays outside workers and includes:
- authority and scope
- approval requirements
- budgets/caps
- fail-stop / STOP state
- evidence requirements
- recovery/fencing rules
- irreversible-action gates
- audit/checkpoint records

A worker result is a proposal/effect result, not a grant of additional permission.

## Policy 5 — No new major subsystem yet
Do not install or adopt external persistent-agent frameworks or Graph-of-Agents-style stacks into AVA OS 4.2 merely because they informed this design.

Use them as testable patterns. Promote only after isolated evidence shows a concrete benefit over the current architecture.

## Implementation priority
P1. Dynamic worker-selection experiment.
P2. Persistent checkpoint/state schema validation.
P3. Small-team vs all-agent routing comparison.
P4. Parallel coordination overhead measurement.
P5. Governance coverage cross-check.

## Acceptance criteria for runtime promotion
The policy may be promoted from architecture/spec to runtime default only when:
1. Dynamic selection never exceeds authorized worker/action scope.
2. A task can resume from a checkpoint after worker interruption without inventing state.
3. The selective route uses fewer/equal worker calls than broadcast routing on the test set without reducing acceptance success.
4. Parallel execution remains bounded and its reason is logged.
5. Existing Agent7 verification, fencing/recovery, and Glow satisfaction boundaries remain intact.
6. Existing AVA OS integrity/approval tests still pass after integration.

## Deferred
- automatic learned routing thresholds
- unrestricted all-agent mode
- adoption of third-party agent runtimes
- broad refactor of Agent7
- new orchestration service

These require evidence from P1-P4 first.

## Version note
This is a forward AVA OS 4.2 architecture patch. It does not relabel the Agent7 V4.1.3 candidate as runtime-enforced, and it does not modify the existing AVA OS 4.2 package hash or claim a rebuilt 4.2 binary/package.

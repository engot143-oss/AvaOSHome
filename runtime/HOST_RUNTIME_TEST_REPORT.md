# AVA OS 4.2 Host Runtime Candidate — Test Report

Date: 2026-11-02
Status: CANDIDATE PASSED FOCUSED ISOLATED TESTS

## Scope
This candidate implements the host-side responsibilities left outside Agent7 and required by the AVA OS 4.2 selective-routing patch:

- smallest-capable authorized worker selection
- external persistent checkpoints
- stable host incident identity
- idempotent effect replay protection keyed by incident/cycle/fencing/action/scope
- append-only hash-chained host ledger with a separate head anchor
- selective-vs-broadcast call-count evidence

It does not modify Agent7, the existing AVA OS 4.2 package, or the existing 4.2 package hash.

## Test command
`python3 -m unittest -v test_host_runtime.py`

## Result
9 tests run, 9 passed.

Covered:
1. Dynamic routing picks the lowest-cost authorized worker that satisfies all required capabilities.
2. A verifier is added only when the primary worker lacks the required verification capability.
3. Unauthorized scope fails closed.
4. No-op tasks can select zero workers.
5. Checkpoints survive host-object restart and reload with integrity verification.
6. Replayed effects return the first recorded outcome instead of executing a second effect record.
7. Stable host incident keys cannot be rebound to a different incident.
8. Ledger truncation is detected when the independent anchor survives.
9. Selective routing matched broadcast task-success count while using 4 calls vs 9 calls on the synthetic comparison set.

## Open limitations
- The router uses explicit static capability/scope metadata. Automatic learned thresholds are intentionally deferred.
- The ledger anchor must live on a trust boundary that cannot be rolled back together with the ledger for strong rollback detection. The isolated test only proves detection when the anchor survives.
- This is not yet wired into the live AVA OS host/Context Bridge. Runtime integration requires a separate integration pass and existing AVA OS/Agent7 regression checks.
- Synthetic call-count evidence supports the routing hypothesis but does not prove real model/credit savings until measured on actual routed workloads.

## Promotion recommendation
Promote from candidate to integration-test stage, not directly to production/runtime default.

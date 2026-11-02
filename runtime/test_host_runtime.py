import tempfile
import unittest
from pathlib import Path

from avaos_host_runtime import HostState, RoutingError, TaskSpec, WorkerSpec, select_workers


class HostRuntimeTests(unittest.TestCase):
    def workers(self):
        return [
            WorkerSpec("local-coder", frozenset({"code", "analyze"}), frozenset({"build"}), 1),
            WorkerSpec("agent7", frozenset({"analyze", "verify"}), frozenset({"build", "research"}), 2),
            WorkerSpec("researcher", frozenset({"research", "analyze"}), frozenset({"research"}), 1),
            WorkerSpec("expensive-generalist", frozenset({"code", "analyze", "verify", "research"}), frozenset({"build", "research"}), 9),
        ]

    def mkstate(self, td):
        root = Path(td)
        return HostState(root / "state.db", root / "ledger.jsonl", root / "anchor.txt")

    def test_dynamic_selection_prefers_smallest_authorized_set(self):
        task = TaskSpec("t1", frozenset({"code"}), "build")
        selected = select_workers(task, self.workers())
        self.assertEqual([w.name for w in selected], ["local-coder"])

    def test_verifier_added_only_when_required(self):
        task = TaskSpec("t2", frozenset({"code"}), "build", "verify")
        selected = select_workers(task, self.workers())
        self.assertEqual([w.name for w in selected], ["local-coder", "agent7"])

    def test_scope_is_fail_closed(self):
        task = TaskSpec("t3", frozenset({"code"}), "admin")
        with self.assertRaises(RoutingError):
            select_workers(task, self.workers())

    def test_zero_worker_for_noop_task(self):
        task = TaskSpec("t4", frozenset(), "build")
        self.assertEqual(select_workers(task, self.workers()), [])

    def test_checkpoint_survives_new_host_instance(self):
        with tempfile.TemporaryDirectory() as td:
            s1 = self.mkstate(td)
            payload = {
                "task_id": "resume-1", "status": "running", "authorized_scope": "build",
                "selected_workers": ["local-coder"], "evidence_refs": ["e1"], "attempt": 1,
                "last_verified_outcome": None, "unresolved": ["verify"],
                "next_permitted_transition": "verify", "timestamp": "2026-11-02T20:00:00Z"
            }
            s1.save_checkpoint(payload)
            del s1
            s2 = self.mkstate(td)
            self.assertEqual(s2.load_checkpoint("resume-1"), payload)
            self.assertTrue(s2.verify_ledger())

    def test_effect_replay_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            s = self.mkstate(td)
            first, _ = s.record_effect_once("i1", 1, "epoch", "a1", "build", {"ok": True})
            second, out2 = s.record_effect_once("i1", 1, "epoch", "a1", "build", {"ok": False})
            self.assertTrue(first)
            self.assertFalse(second)
            self.assertEqual(out2, {"ok": True})

    def test_stable_host_identity_rejects_rebinding(self):
        with tempfile.TemporaryDirectory() as td:
            s = self.mkstate(td)
            self.assertEqual(s.bind_identity("host-key", "incident-1"), "incident-1")
            self.assertEqual(s.bind_identity("host-key", "incident-1"), "incident-1")
            with self.assertRaises(ValueError):
                s.bind_identity("host-key", "incident-2")

    def test_ledger_truncation_detected_when_anchor_survives(self):
        with tempfile.TemporaryDirectory() as td:
            s = self.mkstate(td)
            s.append_event({"type": "one"})
            s.append_event({"type": "two"})
            lines = s.ledger_path.read_text().splitlines()
            s.ledger_path.write_text(lines[0] + "\n")
            self.assertFalse(s.verify_ledger())

    def test_selective_vs_broadcast_efficiency_same_success(self):
        workers = self.workers()
        tasks = [
            TaskSpec("a", frozenset({"code"}), "build"),
            TaskSpec("b", frozenset({"research"}), "research"),
            TaskSpec("c", frozenset({"code"}), "build", "verify"),
        ]
        selective_calls = 0
        broadcast_calls = 0
        selective_success = 0
        broadcast_success = 0
        for task in tasks:
            chosen = select_workers(task, workers)
            selective_calls += len(chosen)
            selective_success += int(bool(chosen) or not task.required_capabilities)

            eligible = [w for w in workers if w.available and task.authorized_scope in w.scopes]
            broadcast_calls += len(eligible)
            can_do = any(task.required_capabilities.issubset(w.capabilities) for w in eligible)
            can_verify = (not task.verification_capability) or any(task.verification_capability in w.capabilities for w in eligible)
            broadcast_success += int(can_do and can_verify)

        self.assertEqual(selective_success, broadcast_success)
        self.assertLess(selective_calls, broadcast_calls)
        self.assertEqual(selective_calls, 4)
        self.assertEqual(broadcast_calls, 9)


if __name__ == "__main__":
    unittest.main()

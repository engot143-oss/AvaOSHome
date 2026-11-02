from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class WorkerSpec:
    name: str
    capabilities: frozenset[str]
    scopes: frozenset[str]
    cost_rank: int = 100
    available: bool = True


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    required_capabilities: frozenset[str]
    authorized_scope: str
    verification_capability: str | None = None


class RoutingError(RuntimeError):
    pass


def select_workers(task: TaskSpec, workers: Sequence[WorkerSpec]) -> list[WorkerSpec]:
    """Choose the smallest capable authorized worker set.

    Current bounded rule: one primary worker when one can satisfy all required
    capabilities; optionally one verifier only when verification requires a
    capability the primary does not have. No broadcast fan-out.
    """
    eligible = [
        w for w in workers
        if w.available
        and task.authorized_scope in w.scopes
        and task.required_capabilities.issubset(w.capabilities)
    ]
    if not task.required_capabilities:
        return []
    if not eligible:
        raise RoutingError("no authorized worker satisfies required capabilities")
    eligible.sort(key=lambda w: (w.cost_rank, w.name))
    primary = eligible[0]
    selected = [primary]

    if task.verification_capability and task.verification_capability not in primary.capabilities:
        verifiers = [
            w for w in workers
            if w.available
            and task.authorized_scope in w.scopes
            and task.verification_capability in w.capabilities
            and w.name != primary.name
        ]
        if not verifiers:
            raise RoutingError("verification required but no authorized verifier available")
        verifiers.sort(key=lambda w: (w.cost_rank, w.name))
        selected.append(verifiers[0])
    return selected


class HostState:
    """External authoritative host state for checkpoints, identity and replay protection."""

    def __init__(self, db_path: str | os.PathLike[str], ledger_path: str | os.PathLike[str], anchor_path: str | os.PathLike[str]):
        self.db_path = str(db_path)
        self.ledger_path = Path(ledger_path)
        self.anchor_path = Path(anchor_path)
        self._init_db()
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.anchor_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.ledger_path.exists():
            self.ledger_path.write_text("", encoding="utf-8")
        if not self.anchor_path.exists():
            self.anchor_path.write_text(self._empty_head(), encoding="utf-8")

    @staticmethod
    def _empty_head() -> str:
        return hashlib.sha256(b"").hexdigest()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as c:
            c.executescript(
                """
                CREATE TABLE IF NOT EXISTS identities(
                    host_incident_key TEXT PRIMARY KEY,
                    incident_id TEXT NOT NULL UNIQUE
                );
                CREATE TABLE IF NOT EXISTS checkpoints(
                    task_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS effects(
                    replay_key TEXT PRIMARY KEY,
                    outcome TEXT NOT NULL
                );
                """
            )

    def bind_identity(self, host_incident_key: str, incident_id: str) -> str:
        if not host_incident_key:
            raise ValueError("stable host_incident_key required")
        with self._connect() as c:
            row = c.execute("SELECT incident_id FROM identities WHERE host_incident_key=?", (host_incident_key,)).fetchone()
            if row:
                if row[0] != incident_id:
                    raise ValueError("host incident key already bound to another incident")
                return row[0]
            c.execute("INSERT INTO identities(host_incident_key, incident_id) VALUES(?,?)", (host_incident_key, incident_id))
        return incident_id

    def save_checkpoint(self, payload: dict) -> str:
        required = {
            "task_id", "status", "authorized_scope", "selected_workers",
            "evidence_refs", "attempt", "last_verified_outcome",
            "unresolved", "next_permitted_transition", "timestamp"
        }
        missing = required - payload.keys()
        if missing:
            raise ValueError(f"checkpoint missing fields: {sorted(missing)}")
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(encoded.encode()).hexdigest()
        with self._connect() as c:
            c.execute(
                "INSERT INTO checkpoints(task_id,payload,payload_sha256) VALUES(?,?,?) "
                "ON CONFLICT(task_id) DO UPDATE SET payload=excluded.payload,payload_sha256=excluded.payload_sha256",
                (payload["task_id"], encoded, digest),
            )
        self.append_event({"type": "checkpoint", "task_id": payload["task_id"], "sha256": digest})
        return digest

    def load_checkpoint(self, task_id: str) -> dict:
        with self._connect() as c:
            row = c.execute("SELECT payload,payload_sha256 FROM checkpoints WHERE task_id=?", (task_id,)).fetchone()
        if not row:
            raise KeyError(task_id)
        payload, digest = row
        actual = hashlib.sha256(payload.encode()).hexdigest()
        if actual != digest:
            raise RuntimeError("checkpoint integrity failure")
        return json.loads(payload)

    @staticmethod
    def replay_key(incident_id: str, cycle: int, fencing_epoch: str, action_id: str, scope: str) -> str:
        material = "\x1f".join([incident_id, str(cycle), fencing_epoch, action_id, scope])
        return hashlib.sha256(material.encode()).hexdigest()

    def record_effect_once(self, incident_id: str, cycle: int, fencing_epoch: str, action_id: str, scope: str, outcome: dict) -> tuple[bool, dict]:
        key = self.replay_key(incident_id, cycle, fencing_epoch, action_id, scope)
        encoded = json.dumps(outcome, sort_keys=True, separators=(",", ":"))
        with self._connect() as c:
            row = c.execute("SELECT outcome FROM effects WHERE replay_key=?", (key,)).fetchone()
            if row:
                return False, json.loads(row[0])
            c.execute("INSERT INTO effects(replay_key,outcome) VALUES(?,?)", (key, encoded))
        self.append_event({"type": "effect", "replay_key": key, "outcome_sha256": hashlib.sha256(encoded.encode()).hexdigest()})
        return True, outcome

    def append_event(self, event: dict) -> str:
        prev = self.anchor_path.read_text(encoding="utf-8").strip() or self._empty_head()
        body = json.dumps({"prev": prev, "event": event}, sort_keys=True, separators=(",", ":"))
        head = hashlib.sha256(body.encode()).hexdigest()
        line = json.dumps({"prev": prev, "event": event, "head": head}, sort_keys=True, separators=(",", ":")) + "\n"
        with self.ledger_path.open("a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        tmp_fd, tmp_name = tempfile.mkstemp(dir=str(self.anchor_path.parent), prefix=self.anchor_path.name + ".", text=True)
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(head)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, self.anchor_path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        return head

    def verify_ledger(self) -> bool:
        prev = self._empty_head()
        for raw in self.ledger_path.read_text(encoding="utf-8").splitlines():
            rec = json.loads(raw)
            if rec["prev"] != prev:
                return False
            body = json.dumps({"prev": rec["prev"], "event": rec["event"]}, sort_keys=True, separators=(",", ":"))
            head = hashlib.sha256(body.encode()).hexdigest()
            if rec["head"] != head:
                return False
            prev = head
        anchored = self.anchor_path.read_text(encoding="utf-8").strip() or self._empty_head()
        return prev == anchored

"""
Confirmation-step policy for AVA OS - docs/framework_design.md §6.

Risk tier (not tool identity) determines how much friction a pending action
gets before it executes:
  LOW    - auto-execute, no confirmation
  MEDIUM - one confirmation
  HIGH   - three distinct, sequential confirmations, each with its own timeout

Any decline or timeout, at any step, at any tier, kills the whole request and
resets progress to zero - no partial credit, no resuming a stale approval
chain (§6: "every approved high-risk action should be tied to one coherent,
recent decision"). An unclassified tool defaults to HIGH - fail-safe, not
fail-open.

This module models the flow as pure state transitions, not real clocks or
sleeps: the caller (an actual interface layer - chat UI, voice, API - which
doesn't exist yet, see STATUS.md) is responsible for knowing when a response
arrived and how much time elapsed, and drives the flow forward by calling
advance(). That keeps this fully unit-testable without real waiting.

ASSUMPTION (documented, not specified in framework_design.md): the doc gives
explicit timeouts for HIGH tier's three steps (~2 min, ~2 min, ~5 min) but
does not state one for MEDIUM tier's single confirmation. This module defaults
MEDIUM's timeout to 120 seconds, matching HIGH's per-step default, as a
judgment call - revisit if the Founder wants a different value.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from .criticality import ConsequenceTier

MEDIUM_CONFIRMATION_TIMEOUT_SECONDS = 120.0  # see ASSUMPTION above


class ConfirmationTier(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class FlowOutcome(Enum):
    PENDING = auto()    # still waiting on the current step
    APPROVED = auto()    # every required step confirmed
    DECLINED = auto()     # user explicitly declined - reset
    TIMED_OUT = auto()     # a step's timeout elapsed - reset


@dataclass(frozen=True)
class ConfirmationStep:
    index: int
    kind: str                 # "restate_action" | "surface_consequence" | "friction_pause" | "confirm_action"
    timeout_seconds: float
    min_wait_seconds: float = 0.0  # nonzero only for the HIGH tier's friction step


def build_steps(tier: ConfirmationTier) -> tuple[ConfirmationStep, ...]:
    if tier == ConfirmationTier.LOW:
        return ()
    if tier == ConfirmationTier.MEDIUM:
        return (
            ConfirmationStep(index=0, kind="confirm_action", timeout_seconds=MEDIUM_CONFIRMATION_TIMEOUT_SECONDS),
        )
    if tier == ConfirmationTier.HIGH:
        return (
            ConfirmationStep(index=0, kind="restate_action", timeout_seconds=120.0),
            ConfirmationStep(index=1, kind="surface_consequence", timeout_seconds=120.0),
            ConfirmationStep(index=2, kind="friction_pause", timeout_seconds=300.0, min_wait_seconds=10.0),
        )
    raise ValueError(f"Unknown tier: {tier}")


def default_tier_for_unclassified_tool() -> ConfirmationTier:
    """§6: 'any tool without an assigned risk tier is treated as high risk by
    default - fail-safe, not fail-open.'"""
    return ConfirmationTier.HIGH


_CONSEQUENCE_TO_CONFIRMATION = {
    ConsequenceTier.LOW: ConfirmationTier.LOW,
    ConsequenceTier.MEDIUM: ConfirmationTier.MEDIUM,
    ConsequenceTier.HIGH: ConfirmationTier.HIGH,
    # criticality.py's CRITICAL has no separate confirmation tier in §6's
    # three-row table - it maps to the strictest available gate (HIGH's
    # triple confirmation), not a stricter one that doesn't exist. Documented
    # judgment call, same spirit as the MEDIUM-timeout assumption above.
    ConsequenceTier.CRITICAL: ConfirmationTier.HIGH,
}


def tier_from_consequence(consequence_tier: ConsequenceTier) -> ConfirmationTier:
    """Bridge criticality.py's 4-tier consequence scale to confirmation.py's
    3-tier confirmation gate, per §6: 'risk tier - not tool identity -
    determines the gate.'"""
    return _CONSEQUENCE_TO_CONFIRMATION[consequence_tier]


@dataclass(frozen=True)
class ConfirmationSession:
    tier: ConfirmationTier
    steps: tuple[ConfirmationStep, ...]
    current_step_index: int = 0
    confirmations_received: int = 0
    outcome: FlowOutcome = FlowOutcome.PENDING
    log: tuple[str, ...] = field(default_factory=tuple)


def start_session(tier: ConfirmationTier) -> ConfirmationSession:
    steps = build_steps(tier)
    if not steps:
        # LOW tier: nothing to confirm - already approved.
        return ConfirmationSession(tier=tier, steps=steps, outcome=FlowOutcome.APPROVED)
    return ConfirmationSession(tier=tier, steps=steps)


def _reset(session: ConfirmationSession, outcome: FlowOutcome, reason: str) -> ConfirmationSession:
    return ConfirmationSession(
        tier=session.tier,
        steps=session.steps,
        current_step_index=0,
        confirmations_received=0,
        outcome=outcome,
        log=session.log + (reason,),
    )


def advance(session: ConfirmationSession, response: str, elapsed_seconds: float) -> ConfirmationSession:
    """Drive the flow forward by one response.

    `response` is "confirm" or "decline". `elapsed_seconds` is time since the
    current step started (not since the whole flow started) - the caller
    measures this against a real clock; this function only compares numbers.
    """
    if session.outcome != FlowOutcome.PENDING:
        # Already resolved (approved/declined/timed out) - a resolved session
        # never mutates. Starting over means calling start_session() again,
        # which is the point: no resuming a stale approval chain.
        return session

    current_step = session.steps[session.current_step_index]

    if response == "decline":
        return _reset(session, FlowOutcome.DECLINED, f"declined at step {current_step.index} ({current_step.kind})")

    if elapsed_seconds > current_step.timeout_seconds:
        return _reset(session, FlowOutcome.TIMED_OUT, f"timed out at step {current_step.index} ({current_step.kind})")

    if response != "confirm":
        raise ValueError(f"response must be 'confirm' or 'decline', got {response!r}")

    if elapsed_seconds < current_step.min_wait_seconds:
        # Deliberate friction: a confirmation that arrives before the minimum
        # cooling-off period isn't accepted yet - still pending, not an error,
        # not progress. The caller should keep waiting and call advance()
        # again once more time has passed.
        return ConfirmationSession(
            tier=session.tier,
            steps=session.steps,
            current_step_index=session.current_step_index,
            confirmations_received=session.confirmations_received,
            outcome=FlowOutcome.PENDING,
            log=session.log + (f"confirm arrived too soon at step {current_step.index} - still cooling off",),
        )

    new_log = session.log + (f"confirmed step {current_step.index} ({current_step.kind})",)
    new_confirmations = session.confirmations_received + 1
    is_last_step = session.current_step_index == len(session.steps) - 1

    if is_last_step:
        return ConfirmationSession(
            tier=session.tier,
            steps=session.steps,
            current_step_index=session.current_step_index,
            confirmations_received=new_confirmations,
            outcome=FlowOutcome.APPROVED,
            log=new_log,
        )

    return ConfirmationSession(
        tier=session.tier,
        steps=session.steps,
        current_step_index=session.current_step_index + 1,
        confirmations_received=new_confirmations,
        outcome=FlowOutcome.PENDING,
        log=new_log,
    )

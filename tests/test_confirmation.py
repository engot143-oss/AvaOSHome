import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.confirmation import (
    ConfirmationTier,
    FlowOutcome,
    advance,
    default_tier_for_unclassified_tool,
    start_session,
    tier_from_consequence,
)
from avaos.criticality import ConsequenceTier


class TestConfirmationFlow(unittest.TestCase):
    def test_low_tier_auto_approves(self):
        session = start_session(ConfirmationTier.LOW)
        self.assertEqual(session.outcome, FlowOutcome.APPROVED)
        self.assertEqual(session.steps, ())

    def test_medium_tier_needs_one_confirmation(self):
        session = start_session(ConfirmationTier.MEDIUM)
        self.assertEqual(session.outcome, FlowOutcome.PENDING)
        session = advance(session, "confirm", elapsed_seconds=5)
        self.assertEqual(session.outcome, FlowOutcome.APPROVED)
        self.assertEqual(session.confirmations_received, 1)

    def test_medium_tier_decline_resets(self):
        session = start_session(ConfirmationTier.MEDIUM)
        session = advance(session, "decline", elapsed_seconds=5)
        self.assertEqual(session.outcome, FlowOutcome.DECLINED)
        self.assertEqual(session.confirmations_received, 0)

    def test_medium_tier_timeout_resets(self):
        session = start_session(ConfirmationTier.MEDIUM)
        session = advance(session, "confirm", elapsed_seconds=200)  # > 120s default
        self.assertEqual(session.outcome, FlowOutcome.TIMED_OUT)

    def test_high_tier_needs_three_sequential_confirmations(self):
        session = start_session(ConfirmationTier.HIGH)
        self.assertEqual(len(session.steps), 3)

        session = advance(session, "confirm", elapsed_seconds=5)  # step 0: restate
        self.assertEqual(session.outcome, FlowOutcome.PENDING)
        self.assertEqual(session.current_step_index, 1)

        session = advance(session, "confirm", elapsed_seconds=5)  # step 1: consequence
        self.assertEqual(session.outcome, FlowOutcome.PENDING)
        self.assertEqual(session.current_step_index, 2)

        session = advance(session, "confirm", elapsed_seconds=15)  # step 2: friction (min 10s)
        self.assertEqual(session.outcome, FlowOutcome.APPROVED)
        self.assertEqual(session.confirmations_received, 3)

    def test_high_tier_friction_step_rejects_too_fast_confirmation(self):
        session = start_session(ConfirmationTier.HIGH)
        session = advance(session, "confirm", elapsed_seconds=5)
        session = advance(session, "confirm", elapsed_seconds=5)
        # Friction step requires >= 10s cooling off - 3s is too fast.
        session = advance(session, "confirm", elapsed_seconds=3)
        self.assertEqual(session.outcome, FlowOutcome.PENDING)
        self.assertEqual(session.current_step_index, 2)  # still on the friction step
        self.assertEqual(session.confirmations_received, 2)  # no progress credited

        # Waiting longer and confirming again succeeds.
        session = advance(session, "confirm", elapsed_seconds=12)
        self.assertEqual(session.outcome, FlowOutcome.APPROVED)

    def test_high_tier_decline_at_any_step_resets_everything(self):
        session = start_session(ConfirmationTier.HIGH)
        session = advance(session, "confirm", elapsed_seconds=5)
        session = advance(session, "confirm", elapsed_seconds=5)
        session = advance(session, "decline", elapsed_seconds=15)  # decline on final step
        self.assertEqual(session.outcome, FlowOutcome.DECLINED)
        self.assertEqual(session.confirmations_received, 0)
        self.assertEqual(session.current_step_index, 0)

    def test_high_tier_timeout_on_step_two_resets_everything_no_partial_credit(self):
        session = start_session(ConfirmationTier.HIGH)
        session = advance(session, "confirm", elapsed_seconds=5)   # step 0 confirmed
        session = advance(session, "confirm", elapsed_seconds=200)  # step 1 times out (>120s)
        self.assertEqual(session.outcome, FlowOutcome.TIMED_OUT)
        self.assertEqual(session.confirmations_received, 0)
        self.assertEqual(session.current_step_index, 0)

    def test_resolved_session_does_not_mutate_further(self):
        session = start_session(ConfirmationTier.MEDIUM)
        session = advance(session, "confirm", elapsed_seconds=5)
        self.assertEqual(session.outcome, FlowOutcome.APPROVED)
        unchanged = advance(session, "decline", elapsed_seconds=5)
        self.assertIs(unchanged, session)

    def test_unclassified_tool_defaults_to_high_not_low(self):
        self.assertEqual(default_tier_for_unclassified_tool(), ConfirmationTier.HIGH)

    def test_consequence_tier_maps_to_matching_confirmation_tier(self):
        self.assertEqual(tier_from_consequence(ConsequenceTier.LOW), ConfirmationTier.LOW)
        self.assertEqual(tier_from_consequence(ConsequenceTier.MEDIUM), ConfirmationTier.MEDIUM)
        self.assertEqual(tier_from_consequence(ConsequenceTier.HIGH), ConfirmationTier.HIGH)

    def test_critical_consequence_maps_to_high_confirmation_not_missing_tier(self):
        # CRITICAL has no dedicated row in §6's confirmation table - it must
        # fall back to the strictest tier that exists (HIGH), not raise or
        # silently under-gate.
        self.assertEqual(tier_from_consequence(ConsequenceTier.CRITICAL), ConfirmationTier.HIGH)


if __name__ == "__main__":
    unittest.main()

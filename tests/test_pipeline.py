import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enum import Enum, auto
from dataclasses import dataclass

from avaos.evidence import Source, SourceType
from avaos.pipeline import RenderedStatus, assess_response, resolve_fallback_checks


class _FakeOutcome(Enum):
    CONFIRMED = auto()
    CONTRADICTED = auto()
    EMPTY = auto()


@dataclass(frozen=True)
class _FakeFallbackResult:
    outcome: _FakeOutcome
    explanation: str


class TestPipeline(unittest.TestCase):
    def test_grounded_claim_passes_through_unchanged(self):
        sources = [Source(type=SourceType.MEMORY, content="The Eiffel Tower is in Paris, France.")]
        results = assess_response("The Eiffel Tower is in Paris.", sources)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, RenderedStatus.GROUNDED)
        self.assertEqual(results[0].rendered_text, "The Eiffel Tower is in Paris.")

    def test_ungrounded_low_stakes_gets_hedged(self):
        results = assess_response("Cats are mammals.", sources=[])
        self.assertEqual(results[0].status, RenderedStatus.HEDGED_LOW_STAKES)
        self.assertIn("not independently verified", results[0].rendered_text)

    def test_ungrounded_high_stakes_needs_fallback_not_shipped_as_fact(self):
        results = assess_response("This medication has no side effects.", sources=[])
        self.assertEqual(results[0].status, RenderedStatus.NEEDS_FALLBACK_CHECK)

    def test_non_factual_sentences_produce_no_assessment(self):
        results = assess_response("I love this book. What time is it?", sources=[])
        self.assertEqual(results, [])

    def test_mixed_paragraph(self):
        text = (
            "The Eiffel Tower is in Paris. Cats are mammals. "
            "This medication has no side effects."
        )
        sources = [Source(type=SourceType.MEMORY, content="The Eiffel Tower is in Paris, France.")]
        results = assess_response(text, sources)
        self.assertEqual(len(results), 3)
        statuses = [r.status for r in results]
        self.assertEqual(
            statuses,
            [
                RenderedStatus.GROUNDED,
                RenderedStatus.HEDGED_LOW_STAKES,
                RenderedStatus.NEEDS_FALLBACK_CHECK,
            ],
        )


class TestResolveFallbackChecks(unittest.TestCase):
    def test_confirmed_becomes_verified_live(self):
        assessments = assess_response("This medication has no side effects.", sources=[])
        resolved = resolve_fallback_checks(
            assessments,
            fallback_fn=lambda text: _FakeFallbackResult(_FakeOutcome.CONFIRMED, "Sources agree."),
        )
        self.assertEqual(resolved[0].status, RenderedStatus.VERIFIED_LIVE)

    def test_contradicted_gets_corrected_not_shipped_as_original(self):
        assessments = assess_response("This medication has no side effects.", sources=[])
        resolved = resolve_fallback_checks(
            assessments,
            fallback_fn=lambda text: _FakeFallbackResult(
                _FakeOutcome.CONTRADICTED, "It commonly causes drowsiness."
            ),
        )
        self.assertEqual(resolved[0].status, RenderedStatus.CONTRADICTED_LIVE)
        self.assertIn("drowsiness", resolved[0].rendered_text)

    def test_empty_result_is_flagged_not_silently_shipped(self):
        assessments = assess_response("This medication has no side effects.", sources=[])
        resolved = resolve_fallback_checks(
            assessments,
            fallback_fn=lambda text: _FakeFallbackResult(_FakeOutcome.EMPTY, ""),
        )
        self.assertEqual(resolved[0].status, RenderedStatus.UNVERIFIED_AFTER_LIVE_CHECK)
        self.assertIn("trusted adult", resolved[0].rendered_text)

    def test_grounded_claims_are_untouched_no_fallback_call(self):
        sources = [Source(type=SourceType.MEMORY, content="The Eiffel Tower is in Paris, France.")]
        assessments = assess_response("The Eiffel Tower is in Paris.", sources)

        def _fail_if_called(text):
            raise AssertionError("fallback_fn should not be called for grounded claims")

        resolved = resolve_fallback_checks(assessments, fallback_fn=_fail_if_called)
        self.assertEqual(resolved[0].status, RenderedStatus.GROUNDED)


if __name__ == "__main__":
    unittest.main()

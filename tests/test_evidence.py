import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.evidence import Source, SourceType, Outcome, ConfidenceLevel, check_grounding


class TestEvidence(unittest.TestCase):
    def test_no_sources_is_empty(self):
        result = check_grounding("The Eiffel Tower is in Paris.", [])
        self.assertEqual(result.outcome, Outcome.EMPTY)
        self.assertTrue(result.gap_logged)

    def test_matching_source_confirms(self):
        sources = [Source(type=SourceType.MEMORY, content="The Eiffel Tower is located in Paris, France.")]
        result = check_grounding("The Eiffel Tower is in Paris.", sources)
        self.assertEqual(result.outcome, Outcome.CONFIRMED)
        self.assertEqual(result.confidence, ConfidenceLevel.GROUNDED)
        self.assertIsNotNone(result.matched_source)

    def test_unrelated_source_is_empty_not_confirmed(self):
        sources = [Source(type=SourceType.MEMORY, content="Bananas are a good source of potassium.")]
        result = check_grounding("The Eiffel Tower is in Paris.", sources)
        self.assertEqual(result.outcome, Outcome.EMPTY)

    def test_negated_source_contradicts(self):
        sources = [Source(type=SourceType.TOOL, content="The store is not open on Sundays.")]
        result = check_grounding("The store is open on Sundays.", sources)
        self.assertEqual(result.outcome, Outcome.CONTRADICTED)

    def test_picks_best_of_multiple_sources(self):
        sources = [
            Source(type=SourceType.MEMORY, content="Bananas are yellow."),
            Source(type=SourceType.MEMORY, content="The Eiffel Tower is in Paris, France, built in 1889."),
        ]
        result = check_grounding("The Eiffel Tower is in Paris.", sources)
        self.assertEqual(result.outcome, Outcome.CONFIRMED)
        self.assertIn("1889", result.matched_source.content)


if __name__ == "__main__":
    unittest.main()

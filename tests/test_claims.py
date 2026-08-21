import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.claims import ClaimKind, extract_claims, checkable_claims


class TestClaims(unittest.TestCase):
    def test_simple_factual_sentence(self):
        claims = extract_claims("The Eiffel Tower is in Paris.")
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].kind, ClaimKind.FACTUAL)

    def test_question_is_not_a_claim(self):
        claims = extract_claims("What time is it?")
        self.assertEqual(claims[0].kind, ClaimKind.QUESTION)
        self.assertEqual(checkable_claims("What time is it?"), [])

    def test_hedged_statement_is_skipped(self):
        claims = extract_claims("This might help with your headache.")
        self.assertEqual(claims[0].kind, ClaimKind.HEDGED)
        self.assertEqual(checkable_claims("This might help with your headache."), [])

    def test_opinion_is_skipped(self):
        claims = extract_claims("I love this book.")
        self.assertEqual(claims[0].kind, ClaimKind.OPINION)

    def test_instruction_is_skipped(self):
        claims = extract_claims("Please restart the router.")
        self.assertEqual(claims[0].kind, ClaimKind.INSTRUCTION)

    def test_multi_sentence_paragraph(self):
        text = "Paris is the capital of France. Is that surprising? I love visiting there."
        claims = extract_claims(text)
        self.assertEqual(len(claims), 3)
        self.assertEqual(claims[0].kind, ClaimKind.FACTUAL)
        self.assertEqual(claims[1].kind, ClaimKind.QUESTION)
        self.assertEqual(claims[2].kind, ClaimKind.OPINION)

    def test_abbreviation_does_not_split_sentence(self):
        claims = extract_claims("Dr. Smith prescribed the medication.")
        self.assertEqual(len(claims), 1)
        self.assertIn("Dr. Smith", claims[0].text)

    def test_compound_sentence_splits_into_two_claims(self):
        text = "The store opens at nine and it closes at five."
        claims = extract_claims(text)
        self.assertEqual(len(claims), 2)
        self.assertTrue(all(c.kind == ClaimKind.FACTUAL for c in claims))

    def test_short_and_phrase_does_not_split(self):
        # "bread and butter" is a noun phrase, not two clauses - should stay one claim
        claims = extract_claims("I bought bread and butter.")
        self.assertEqual(len(claims), 1)

    def test_checkable_claims_filters_correctly(self):
        text = (
            "The bridge was built in 1937. I think it's beautiful. "
            "Please visit at sunset. Is it free to enter?"
        )
        result = checkable_claims(text)
        self.assertEqual(len(result), 1)
        self.assertIn("1937", result[0].text)

    def test_strong_unhedged_claim_is_still_factual(self):
        # Documented known limitation: strength != groundedness. This claim
        # is confidently wrong-shaped but has no hedge marker, so it's FACTUAL -
        # catching that it's overconfident is a later pipeline stage's job.
        claims = extract_claims("This drug carries no meaningful risk for children.")
        self.assertEqual(claims[0].kind, ClaimKind.FACTUAL)


if __name__ == "__main__":
    unittest.main()

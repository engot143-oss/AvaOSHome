import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.criticality import ConsequenceTier, Domain, classify


class TestCriticality(unittest.TestCase):
    def test_general_chat_is_low(self):
        result = classify("What's a good recipe for banana bread?")
        self.assertEqual(result.tier, ConsequenceTier.LOW)
        self.assertEqual(result.domains, (Domain.GENERAL,))

    def test_discussing_medication_without_action_is_high_not_critical(self):
        result = classify("What are the side effects of ibuprofen?")
        self.assertEqual(result.tier, ConsequenceTier.HIGH)
        self.assertIn(Domain.MEDICAL, result.domains)
        self.assertFalse(result.escalated)

    def test_deciding_to_stop_medication_escalates_to_critical(self):
        result = classify("I'm going to stop taking my medication tomorrow.")
        self.assertEqual(result.tier, ConsequenceTier.CRITICAL)
        self.assertIn(Domain.MEDICAL, result.domains)
        self.assertTrue(result.escalated)

    def test_investment_question_is_high(self):
        result = classify("Is now a good time to invest in the stock market?")
        self.assertEqual(result.tier, ConsequenceTier.HIGH)
        self.assertIn(Domain.FINANCIAL, result.domains)

    def test_wiring_money_is_irreversible_critical(self):
        result = classify("Please send it, I want to wire the money today.")
        self.assertEqual(result.tier, ConsequenceTier.CRITICAL)
        self.assertIn(Domain.IRREVERSIBLE, result.domains)

    def test_identity_data_is_always_critical(self):
        result = classify("Here's my social security number for the form.")
        self.assertEqual(result.tier, ConsequenceTier.CRITICAL)
        self.assertIn(Domain.IDENTITY, result.domains)

    def test_legal_question_is_medium(self):
        result = classify("Can you explain what liability means in this contract?")
        self.assertEqual(result.tier, ConsequenceTier.MEDIUM)
        self.assertIn(Domain.LEGAL, result.domains)

    def test_legal_action_escalates_to_high(self):
        result = classify("I'm going to sign the contract this afternoon.")
        # "sign the contract" is also an irreversible marker, so this hits
        # IRREVERSIBLE (CRITICAL) directly - both signals point the same way.
        self.assertEqual(result.tier, ConsequenceTier.CRITICAL)

    def test_multi_domain_uses_max_aggregation(self):
        # Financial (HIGH) + identity (CRITICAL) mentioned together -
        # the result must be judged by the riskier half, not averaged down.
        result = classify(
            "For the loan application, here's my social security number."
        )
        self.assertEqual(result.tier, ConsequenceTier.CRITICAL)
        self.assertIn(Domain.FINANCIAL, result.domains)
        self.assertIn(Domain.IDENTITY, result.domains)

    def test_security_question_is_medium(self):
        result = classify("How does two-factor authentication work?")
        self.assertEqual(result.tier, ConsequenceTier.MEDIUM)
        self.assertIn(Domain.SECURITY, result.domains)


if __name__ == "__main__":
    unittest.main()

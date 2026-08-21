import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.stakes import Stakes, classify_stakes


class TestStakes(unittest.TestCase):
    def test_paris_example_from_design_doc_is_low_stakes(self):
        # This is the design doc's own calibration example (§9A step 3).
        self.assertEqual(classify_stakes("Paris is the capital of France."), Stakes.LOW)

    def test_number_makes_it_high_stakes(self):
        self.assertEqual(classify_stakes("The bridge is 1,200 feet long."), Stakes.HIGH)

    def test_causal_claim_is_high_stakes(self):
        self.assertEqual(
            classify_stakes("This supplement causes improved sleep quality."),
            Stakes.HIGH,
        )

    def test_medical_domain_is_high_stakes_even_without_numbers(self):
        self.assertEqual(
            classify_stakes("This medication has no side effects."),
            Stakes.HIGH,
        )

    def test_plain_general_statement_is_low_stakes(self):
        self.assertEqual(classify_stakes("Cats are mammals."), Stakes.LOW)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "skills" / "cognitive-os" / "references"


class LensContractTests(unittest.TestCase):
    def test_v14_core_lenses_are_defined(self):
        text = (REF / "lenses.md").read_text(encoding="utf-8")
        for token in ["/evidence", "/assumptions", "/unknowns", "/nextproof", "/stop", "/sensemaking", "/outsideview"]:
            self.assertIn(token, text)

    def test_outside_view_forbids_fabricated_base_rates(self):
        text = (REF / "lenses.md").read_text(encoding="utf-8").lower()
        self.assertIn("never fabricate", text)
        self.assertIn("base rate", text)

    def test_extended_robustness_is_not_default(self):
        text = (REF / "extended-lenses.md").read_text(encoding="utf-8").lower()
        self.assertIn("/robustness", text)
        self.assertIn("not loaded by default", text)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "skills" / "cognitive-os" / "references" / "output.md"


class OutputPolicyTests(unittest.TestCase):
    def test_decision_brief_leads_with_decision_and_shows_delta_when_applicable(self):
        text = OUTPUT.read_text(encoding="utf-8").lower()
        self.assertIn("editorial hierarchy", text)
        self.assertIn("idea evolution", text)
        self.assertIn("progressive technical disclosure", text)

    def test_output_policy_rejects_framework_dumping(self):
        text = OUTPUT.read_text(encoding="utf-8").lower()
        self.assertIn("hide framework ritual", text)
        self.assertIn("phase", text)
        self.assertIn("raw enum", text)

    def test_no_pseudo_precision_confidence(self):
        text = OUTPUT.read_text(encoding="utf-8").lower()
        self.assertIn("pseudo-precision confidence percentages", text)


if __name__ == "__main__":
    unittest.main()

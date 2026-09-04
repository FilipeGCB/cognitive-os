import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "skills" / "cognitive-os" / "references"


class WorkflowPolicyTests(unittest.TestCase):
    def test_discovery_interview_is_materiality_gated(self):
        text = (REF / "discovery-interview.md").read_text(encoding="utf-8").lower()
        self.assertIn("materially change", text)
        self.assertIn("ritual", text)
        self.assertIn("one question at a time", text)

    def test_challenge_closes_recommendation_impact(self):
        text = (REF / "workflows.md").read_text(encoding="utf-8")
        for token in ["maintains", "weakens", "conditions", "reverses"]:
            self.assertIn(token, text)

    def test_decision_quality_closure_is_present(self):
        text = (REF / "workflows.md").read_text(encoding="utf-8").lower()
        for token in ["framing sufficient", "meaningful alternatives", "values/trade-offs", "next action"]:
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()

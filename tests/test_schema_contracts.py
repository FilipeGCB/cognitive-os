import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "skills" / "cognitive-os" / "schemas"


class SchemaContractTests(unittest.TestCase):
    def test_decision_pack_remains_canonical_and_supports_idea_delta(self):
        text = (SCHEMAS / "decision-pack.md").read_text(encoding="utf-8").lower()
        self.assertIn("canonical structured decision record", text)
        self.assertIn("idea evolution", text)
        self.assertIn("optional", text)

    def test_run_record_refuses_chain_of_thought(self):
        text = (SCHEMAS / "cognitive-run-record.md").read_text(encoding="utf-8").lower()
        self.assertIn("without chain-of-thought", text)
        self.assertIn("never record", text)

    def test_capability_evidence_scopes_truth_to_surface(self):
        text = (SCHEMAS / "capability-evidence-record.md").read_text(encoding="utf-8").lower()
        self.assertIn("host + surface + capability", text)
        self.assertIn("called + success", text)


if __name__ == "__main__":
    unittest.main()

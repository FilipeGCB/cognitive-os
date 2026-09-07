import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvalCoverageTests(unittest.TestCase):
    def test_v15_suite_covers_all_spec_families_and_critical_gates(self):
        cases = []
        for name in ["v1.5-cases.json", "v1.5-output-cases.json", "v1.5-distribution-cases.json"]:
            cases.extend(json.loads((ROOT / "evals" / name).read_text(encoding="utf-8")))
        families = {tag for case in cases for tag in case["tags"]}
        self.assertTrue({"CD", "RS", "GS", "SI", "TL", "PR", "HP", "DS", "MC", "RC"} <= families)
        self.assertGreaterEqual(sum(1 for case in cases if case.get("critical")), 10)
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_v14_behavioral_suite_covers_required_product_behaviors(self):
        cases = []
        for name in ["v1.4-core-cases.json", "v1.4-output-cases.json"]:
            cases.extend(json.loads((ROOT / "evals" / name).read_text(encoding="utf-8")))

        tags = {tag for case in cases for tag in case["tags"]}
        required = {
            "discovery-interview",
            "sensemaking",
            "outside-view",
            "value-of-information",
            "robustness",
            "decision-quality",
            "deep-research",
            "grounded-corpus",
            "capability-routing",
            "consent",
            "prompt-injection",
            "audit",
            "idea-evolution",
            "no-framework-dump",
            "no-pseudo-confidence",
            "material-uncertainty",
        }
        self.assertTrue(required.issubset(tags), sorted(required - tags))

    def test_v14_suite_keeps_critical_negative_controls(self):
        cases = []
        for name in ["v1.4-core-cases.json", "v1.4-output-cases.json"]:
            cases.extend(json.loads((ROOT / "evals" / name).read_text(encoding="utf-8")))
        by_id = {case["id"]: case for case in cases}
        for case_id in ["V14-C06", "V14-C10", "V14-C12", "V14-C16", "V14-C18", "V14-C19", "V14-O03", "V14-O07", "V14-O10"]:
            self.assertIn(case_id, by_id)
            self.assertTrue(by_id[case_id]["must_not"])


if __name__ == "__main__":
    unittest.main()

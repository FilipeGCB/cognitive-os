import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvalManifestTests(unittest.TestCase):
    def test_core_eval_cases_cover_new_behavior(self):
        cases = json.loads((ROOT / "evals" / "v1.4-core-cases.json").read_text(encoding="utf-8"))
        tags = {tag for case in cases for tag in case["tags"]}
        required = {"discovery-interview", "sensemaking", "outside-view", "value-of-information", "robustness", "decision-quality"}
        self.assertTrue(required <= tags)
        self.assertGreaterEqual(len(cases), 12)

    def test_ids_are_unique(self):
        cases = json.loads((ROOT / "evals" / "v1.4-core-cases.json").read_text(encoding="utf-8"))
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OutputEvalManifestTests(unittest.TestCase):
    def test_output_eval_tags_cover_editorial_requirements(self):
        cases = json.loads((ROOT / "evals" / "v1.4-output-cases.json").read_text(encoding="utf-8"))
        tags = {tag for case in cases for tag in case["tags"]}
        required = {"conclusion-first", "idea-evolution", "no-framework-dump", "simple-stays-simple", "audit-preserved", "readable-markdown"}
        self.assertTrue(required <= tags)
        self.assertGreaterEqual(len(cases), 10)


if __name__ == "__main__":
    unittest.main()

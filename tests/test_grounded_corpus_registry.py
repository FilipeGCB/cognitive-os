import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GroundedCorpusRegistryTests(unittest.TestCase):
    def test_candidates_have_comparable_evidence(self):
        data = json.loads((ROOT / "adapters" / "grounded-corpus" / "registry.json").read_text(encoding="utf-8"))
        for candidate in data["candidates"]:
            for key in ["license", "citation_fidelity", "retrieval", "api", "local_mode", "footprint", "maintenance", "security", "update_model", "status"]:
                self.assertIn(key, candidate, f"{candidate.get('id')} missing {key}")

    def test_no_default_is_promoted_without_direct_test(self):
        data = json.loads((ROOT / "adapters" / "grounded-corpus" / "registry.json").read_text(encoding="utf-8"))
        self.assertIsNone(data["default_local_companion"])
        self.assertEqual(data["preferred_next_test"], "open-notebooklm-tom1030507")

    def test_all_candidates_remain_candidates(self):
        data = json.loads((ROOT / "adapters" / "grounded-corpus" / "registry.json").read_text(encoding="utf-8"))
        self.assertTrue(all(candidate["status"] == "candidate" for candidate in data["candidates"]))


if __name__ == "__main__":
    unittest.main()

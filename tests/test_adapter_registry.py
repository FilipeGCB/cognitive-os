import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AdapterRegistryTests(unittest.TestCase):
    def test_every_adapter_has_consent_relevant_metadata(self):
        registry = json.loads((ROOT / "adapters" / "registry.json").read_text(encoding="utf-8"))
        for item in registry["adapters"]:
            for key in ["id", "capability", "version", "license", "status", "auth", "footprint", "permissions", "reversible", "gauntlet"]:
                self.assertIn(key, item, f"{item.get('id')} missing {key}")

    def test_no_candidate_is_accidentally_supported(self):
        registry = json.loads((ROOT / "adapters" / "registry.json").read_text(encoding="utf-8"))
        self.assertFalse(any(item["status"] == "supported" for item in registry["adapters"]))


if __name__ == "__main__":
    unittest.main()

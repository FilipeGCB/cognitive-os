import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NotebookLMAdapterTests(unittest.TestCase):
    def test_notebooklm_never_silent_installs_or_authenticates(self):
        manifest = json.loads((ROOT / "adapters" / "notebooklm" / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["auth"]["required"])
        self.assertEqual(manifest["consent"], "specific")
        self.assertFalse(manifest["install"]["silent"])

    def test_notebooklm_is_pinned_and_not_overclaimed(self):
        manifest = json.loads((ROOT / "adapters" / "notebooklm" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "v0.8.2")
        self.assertEqual(len(manifest["commit"]), 40)
        self.assertEqual(manifest["gauntlet"]["status"], "test")
        self.assertNotEqual(manifest["status"], "supported")

    def test_write_surface_is_explicit(self):
        manifest = json.loads((ROOT / "adapters" / "notebooklm" / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["permissions"]["write"])


if __name__ == "__main__":
    unittest.main()

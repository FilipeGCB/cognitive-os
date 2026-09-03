import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_public_package import scan_text


class PublicValidatorTests(unittest.TestCase):
    def test_scan_rejects_private_vault_marker(self):
        findings = scan_text("source: FilipeGCB/obsidian-notes")
        self.assertTrue(findings)

    def test_scan_rejects_secret_like_token(self):
        findings = scan_text("token=sk-proj-abcdefghijklmnopqrstuvwxyz123456")
        self.assertTrue(findings)

    def test_scan_accepts_public_product_copy(self):
        self.assertEqual(scan_text("Cognitive OS is a portable decision skill."), [])


if __name__ == "__main__":
    unittest.main()

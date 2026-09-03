import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "cognitive-os"


class CapabilityPolicyTests(unittest.TestCase):
    def test_capability_names_are_abstract(self):
        text = (SKILL / "references" / "capabilities.md").read_text(encoding="utf-8")
        for name in ["Deep Research", "Grounded Corpus Research", "Repository Research", "Structured Crawl"]:
            self.assertIn(name, text)

    def test_specific_consent_boundary_is_explicit(self):
        text = (SKILL / "policies" / "installation-consent.md").read_text(encoding="utf-8").lower()
        for token in ["docker", "credential", "write", "specific confirmation"]:
            self.assertIn(token, text)

    def test_notebooklm_requires_specific_consent(self):
        text = (SKILL / "policies" / "installation-consent.md").read_text(encoding="utf-8").lower()
        self.assertIn("notebooklm", text)
        self.assertIn("specific confirmation", text)


if __name__ == "__main__":
    unittest.main()

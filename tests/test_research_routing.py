import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "skills" / "cognitive-os" / "references" / "research-routing.md"


class ResearchRoutingTests(unittest.TestCase):
    def test_deep_research_is_value_gated_and_not_vendor_locked(self):
        text = TEXT.read_text(encoding="utf-8").lower()
        self.assertIn("information value", text)
        self.assertIn("user activation", text)
        self.assertIn("fallback", text)
        self.assertIn("native host", text)

    def test_grounded_corpus_prefers_existing_capability(self):
        text = TEXT.read_text(encoding="utf-8").lower()
        self.assertIn("sufficient native host", text)
        self.assertIn("already configured trusted adapter", text)


if __name__ == "__main__":
    unittest.main()

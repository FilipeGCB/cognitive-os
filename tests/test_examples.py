import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples"


class ExampleTests(unittest.TestCase):
    def test_examples_are_scan_friendly(self):
        for name in ["decision-brief-simple.md", "decision-brief-idea-evolution.md", "decision-brief-board360.md"]:
            text = (EX / name).read_text(encoding="utf-8")
            self.assertGreaterEqual(len(text.splitlines()), 5)
            self.assertNotIn("Phase 1", text)
            self.assertNotIn("CONFIDENCE =", text)

    def test_idea_evolution_example_makes_delta_visible(self):
        text = (EX / "decision-brief-idea-evolution.md").read_text(encoding="utf-8").lower()
        self.assertIn("initial idea", text)
        self.assertIn("matured decision", text)


if __name__ == "__main__":
    unittest.main()

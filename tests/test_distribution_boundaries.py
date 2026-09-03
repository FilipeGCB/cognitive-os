import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DistributionBoundaryTests(unittest.TestCase):
    def test_distribution_docs_point_to_single_core(self):
        for name in ["agent-skills", "openai", "claude", "gemini"]:
            text = (ROOT / "distribution" / name / "README.md").read_text(encoding="utf-8")
            self.assertIn("skills/cognitive-os", text)

    def test_claude_marketplace_reuses_canonical_skill(self):
        data = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        plugin = data["plugins"][0]
        self.assertEqual(plugin["name"], "cognitive-os")
        self.assertIn("./skills/cognitive-os", plugin["skills"])
        self.assertFalse(plugin["strict"])

    def test_gemini_wrapper_has_no_duplicate_instruction_context(self):
        data = json.loads((ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "cognitive-os")
        self.assertNotIn("contextFileName", data)
        self.assertNotIn("mcpServers", data)

    def test_openai_doc_does_not_equate_npx_with_chatgpt_web_install(self):
        text = (ROOT / "distribution" / "openai" / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("must not", text)
        self.assertIn("chatgpt web", text)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "cognitive-os"


class SkillStructureTests(unittest.TestCase):
    def test_runtime_skill_is_self_contained(self):
        required = [
            SKILL / "SKILL.md",
            SKILL / "VERSION",
            SKILL / "references" / "routing.md",
            SKILL / "references" / "source-authority.md",
            SKILL / "references" / "lenses.md",
            SKILL / "references" / "workflows.md",
            SKILL / "references" / "capabilities.md",
            SKILL / "references" / "output.md",
            SKILL / "policies" / "installation-consent.md",
            SKILL / "schemas" / "decision-pack.md",
        ]
        self.assertTrue(all(path.is_file() for path in required))

    def test_public_skill_has_no_private_runtime_dependency(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        forbidden = ["FilipeGCB/obsidian-notes", "Host A", "GPT privado", "Vivo"]
        for token in forbidden:
            self.assertNotIn(token, text)

    def test_dev_version_is_explicit(self):
        self.assertEqual((SKILL / "VERSION").read_text(encoding="utf-8").strip(), "1.4.0-dev")


if __name__ == "__main__":
    unittest.main()

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_skill_references import validate_runtime_references  # noqa: E402


class SkillReferenceValidatorTests(unittest.TestCase):
    def test_current_runtime_references_are_not_broken(self):
        findings = validate_runtime_references(ROOT / "skills" / "cognitive-os")
        self.assertEqual(findings, [])

    def test_broken_relative_markdown_link_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("See [policy](policies/missing.md).\n", encoding="utf-8")
            findings = validate_runtime_references(root)
            self.assertEqual(len(findings), 1)
            self.assertIn("policies/missing.md", findings[0])

    def test_anchor_and_external_links_are_not_treated_as_local_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text(
                "[section](#section) [web](https://example.com/a) [mail](mailto:test@example.com)\n",
                encoding="utf-8",
            )
            self.assertEqual(validate_runtime_references(root), [])

    def test_path_traversal_reference_is_rejected_even_if_target_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "runtime"
            root.mkdir()
            (parent / "outside.md").write_text("outside", encoding="utf-8")
            (root / "SKILL.md").write_text("[outside](../outside.md)\n", encoding="utf-8")
            findings = validate_runtime_references(root)
            self.assertEqual(len(findings), 1)
            self.assertIn("escapes runtime root", findings[0])


if __name__ == "__main__":
    unittest.main()

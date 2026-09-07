import tempfile
import unittest
from pathlib import Path

from bootstrap.cognitive_os_governance import (
    MethodologySnapshot,
    detect_persistent_side_effects,
    validate_staged_patch,
)


class SelfImprovementTests(unittest.TestCase):
    def test_valid_patch_is_staged_and_not_promoted_mid_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "references").mkdir()
            (root / "references" / "routing.md").write_text("# routing\n", encoding="utf-8")
            snapshot = MethodologySnapshot(
                run_id="CRR-20260904-120000-ABCD",
                skill_version="1.5.0-dev",
                skill_hash="a" * 64,
                reference_hashes={"references/routing.md": "b" * 64},
                policy_hashes={},
            )
            patch = {
                "target": "references/routing.md",
                "references": ["references/routing.md"],
                "dependencies": [],
                "frontmatter_valid": True,
            }
            result = validate_staged_patch(snapshot, patch, root)
        self.assertEqual(result.status, "STAGED")
        self.assertFalse(result.activate_now)
        self.assertEqual(result.validation, "PASS")

    def test_broken_reference_cannot_be_promoted(self):
        snapshot = MethodologySnapshot(
            run_id="CRR-20260904-120000-ABCD",
            skill_version="1.5.0-dev",
            skill_hash="a" * 64,
            reference_hashes={},
            policy_hashes={},
        )
        patch = {
            "target": "references/new.md",
            "references": ["references/missing.md"],
            "dependencies": ["schemas/missing.schema.json"],
            "frontmatter_valid": True,
        }
        result = validate_staged_patch(snapshot, patch, Path(tempfile.mkdtemp()))
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.activate_now)
        self.assertEqual(result.validation, "FAIL")

    def test_filesystem_and_config_diff_records_side_effects_without_write_tool(self):
        effects = detect_persistent_side_effects(
            {"skills/cognitive-os/SKILL.md": "a", "config/settings.json": "a"},
            {"skills/cognitive-os/SKILL.md": "b", "config/settings.json": "b", "new.txt": "c"},
            [],
        )
        types = {effect.type for effect in effects}
        self.assertIn("SKILL_MUTATED", types)
        self.assertIn("CONFIG_CHANGED", types)
        self.assertIn("FILE_CREATED", types)

    def test_installation_event_is_recorded_separately_from_file_change(self):
        effects = detect_persistent_side_effects({}, {}, [{"event": "package_installed", "target": "demo"}])
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].type, "PACKAGE_INSTALLED")


if __name__ == "__main__":
    unittest.main()

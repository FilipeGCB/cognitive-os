import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_distribution import (  # noqa: E402
    DistributionError,
    load_manifest,
    validate_distribution_manifest,
    validate_installed_artifact,
)
from project_distribution import project_manifest  # noqa: E402


class DistributionContractTests(unittest.TestCase):
    def test_each_target_has_an_honest_v15_manifest(self):
        seen = set()
        for path in sorted((ROOT / "distribution/manifests").glob("*.json")):
            manifest = validate_distribution_manifest(path)
            seen.add(manifest["target"])
            self.assertEqual(manifest["package_version"], "1.5.0-dev")
            self.assertIn(manifest["schema_enforcement"], {"COMPLETE", "PARTIAL", "UNAVAILABLE"})
        self.assertEqual(seen, {"agent-skills", "openai", "claude", "gemini"})

    def test_copy_of_installed_skill_is_smoke_tested(self):
        manifest = load_manifest(ROOT / "distribution/manifests/agent-skills.json")
        with tempfile.TemporaryDirectory() as tmp:
            installed = Path(tmp) / "cognitive-os"
            shutil.copytree(ROOT / "skills/cognitive-os", installed)
            self.assertEqual(validate_installed_artifact(installed, manifest), [])
            (installed / "references" / "broken.md").write_text("[bad](missing.md)\n", encoding="utf-8")
            self.assertTrue(validate_installed_artifact(installed, manifest))

    def test_manifest_rejects_unknown_field_and_unbound_candidate(self):
        path = ROOT / "distribution/manifests/agent-skills.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["unexpected"] = True
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "manifest.json"
            invalid.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(DistributionError):
                load_manifest(invalid)
        with self.assertRaises(DistributionError):
            validate_distribution_manifest(path, expected_source_commit="a" * 40)

    def test_each_declared_target_is_smoke_tested_as_a_projected_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in sorted((ROOT / "distribution/manifests").glob("*.json")):
                manifest = load_manifest(path)
                artifact = project_manifest(manifest, root / manifest["target"])
                self.assertEqual(validate_installed_artifact(artifact, manifest), [], manifest["target"])


if __name__ == "__main__":
    unittest.main()

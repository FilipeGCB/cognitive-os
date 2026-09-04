import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_release_evidence import (  # noqa: E402
    source_tree_fingerprint,
    validate_release_evidence,
)


class ReleaseEvidenceBindingTests(unittest.TestCase):
    def test_valid_evidence_is_bound_to_exact_candidate_and_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills/cognitive-os").mkdir(parents=True)
            (root / "evals/e2e").mkdir(parents=True)
            (root / "manifests").mkdir()
            (root / "skills/cognitive-os/VERSION").write_text("1.5.0-dev\n", encoding="utf-8")
            (root / "skills/cognitive-os/SKILL.md").write_text("# skill\n", encoding="utf-8")
            (root / "skills/cognitive-os/manifest.json").write_text('{"version":"1.5.0-dev"}\n', encoding="utf-8")
            (root / "evals/e2e/harness.py").write_text("# harness\n", encoding="utf-8")
            (root / "manifests/package.json").write_text('{"version":"1.5.0-dev"}\n', encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
            subprocess.run(["git", "add", "skills", "evals", "manifests"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "candidate"], cwd=root, check=True)
            candidate = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            package_hash = hashlib.sha256((root / "manifests/package.json").read_bytes()).hexdigest()
            harness_hash = hashlib.sha256((root / "evals/e2e/harness.py").read_bytes()).hexdigest()
            record = {
                "schema_version": "cognitive-os-release-evidence-v1.5",
                "repository": "FilipeGCB/cognitive-os",
                "candidate_sha": candidate,
                "version": "1.5.0-dev",
                "source_tree_fingerprint": source_tree_fingerprint(candidate, cwd=root),
                "manifests": [{"path": "manifests/package.json", "sha256": package_hash, "source_commit": candidate, "version": "1.5.0-dev"}],
                "harness": {"path": "evals/e2e/harness.py", "sha256": harness_hash, "schema_version": "harness-v1.5"},
                "execution": {
                    "run_id": "CRR-20260904-120000-ABCD",
                    "started_at": "2026-09-04T12:00:00Z",
                    "finished_at": "2026-09-04T12:01:00Z",
                    "candidate_sha": candidate,
                    "artifact_refs": ["manifests/package.json"],
                    "host_observed_identity": True,
                },
                "sut_models": ["model"],
                "grader_models": ["grader"],
                "runtime_hosts": ["generic"],
                "tests": {"total": 1, "passed": 1, "failed": 0, "critical_failures": [], "conformance_schema": "v1.5", "grader_independent": True},
                "critical_gates": {"contracts": "PASS"},
                "hermes_e2e": {"state": "UNAVAILABLE", "evidence_refs": []},
                "work": {"state": "UNAVAILABLE", "evidence_refs": []},
                "distribution": {"state": "PASS", "evidence_refs": []},
                "telemetry": {"state": "UNAVAILABLE", "evidence_refs": []},
                "collector": {"state": "UNAVAILABLE", "evidence_refs": []},
                "known_limitations": ["test fixture"],
            }
            validate_release_evidence(record, repo_root=root, expected_candidate_sha=candidate)
            with self.assertRaises(ValueError):
                validate_release_evidence({**record, "candidate_sha": "0" * 40}, repo_root=root)


if __name__ == "__main__":
    unittest.main()

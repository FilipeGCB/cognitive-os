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
    _candidate_eval_bundle_hash,
    sha256_bytes,
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
                "tests": {
                    "total": 1,
                    "passed": 1,
                    "failed": 0,
                    "critical_failures": [],
                    "conformance_schema": "v1.5",
                    "grader_independent": True,
                    "model_results": [{
                        "sut": "model",
                        "grader": "grader",
                        "passed": 1,
                        "total": 1,
                        "critical_failures": [],
                        "truncated_cases": [],
                        "invented_identity_cases": [],
                    }],
                },
                "critical_gates": {"contracts": "PASS"},
                "hermes_e2e": {"state": "UNAVAILABLE", "evidence_refs": []},
                "work": {"state": "UNAVAILABLE", "evidence_refs": []},
                "distribution": {"state": "PASS", "evidence_refs": []},
                "telemetry": {"state": "UNAVAILABLE", "evidence_refs": []},
                "collector": {"state": "UNAVAILABLE", "evidence_refs": []},
                "known_limitations": ["test fixture"],
            }
            validate_release_evidence(record, repo_root=root, expected_candidate_sha=candidate, require_behavioral_pass=False)
            with self.assertRaises(ValueError):
                validate_release_evidence({**record, "candidate_sha": "0" * 40}, repo_root=root)

    def test_release_gate_requires_complete_candidate_bound_behavioral_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills/cognitive-os").mkdir(parents=True)
            (root / "manifests").mkdir()
            (root / "evals/e2e").mkdir(parents=True)
            (root / "skills/cognitive-os/VERSION").write_text("1.5.0-dev\n", encoding="utf-8")
            (root / "skills/cognitive-os/SKILL.md").write_text("# skill\n", encoding="utf-8")
            (root / "manifests/package.json").write_text('{"version":"1.5.0-dev"}\n', encoding="utf-8")
            (root / "evals/e2e/harness.py").write_text("# harness\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
            subprocess.run(["git", "add", "skills", "manifests", "evals"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "candidate"], cwd=root, check=True)
            candidate = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            record = {
                "schema_version": "cognitive-os-release-evidence-v1.5",
                "repository": "FilipeGCB/cognitive-os",
                "candidate_sha": candidate,
                "version": "1.5.0-dev",
                "source_tree_fingerprint": source_tree_fingerprint(candidate, cwd=root),
                "manifests": [{
                    "path": "manifests/package.json",
                    "sha256": hashlib.sha256((root / "manifests/package.json").read_bytes()).hexdigest(),
                    "source_commit": candidate,
                    "version": "1.5.0-dev",
                }],
                "harness": {
                    "path": "evals/e2e/harness.py",
                    "sha256": hashlib.sha256((root / "evals/e2e/harness.py").read_bytes()).hexdigest(),
                    "schema_version": "harness-v1.5",
                },
                "execution": {
                    "run_id": "CRR-20260904-120000-ABCD",
                    "started_at": "2026-09-04T12:00:00Z",
                    "finished_at": "2026-09-04T12:01:00Z",
                    "candidate_sha": candidate,
                    "artifact_refs": ["manifests/package.json"],
                    "host_observed_identity": True,
                },
                "sut_models": ["remote-sut"],
                "grader_models": ["remote-grader"],
                "runtime_hosts": ["generic-remote"],
                "tests": {
                    "total": 1,
                    "passed": 1,
                    "failed": 0,
                    "critical_failures": [],
                    "conformance_schema": "cognitive-os-conformance-v4",
                    "grader_independent": True,
                    "model_results": [],
                },
                "critical_gates": {"contracts": "PASS"},
                "hermes_e2e": {"state": "UNAVAILABLE", "evidence_refs": []},
                "work": {"state": "UNAVAILABLE", "evidence_refs": []},
                "distribution": {"state": "PASS", "evidence_refs": []},
                "telemetry": {"state": "UNAVAILABLE", "evidence_refs": []},
                "collector": {"state": "UNAVAILABLE", "evidence_refs": []},
                "known_limitations": ["missing behavioral evidence"],
            }
            with self.assertRaises(ValueError):
                validate_release_evidence(
                    record,
                    repo_root=root,
                    expected_candidate_sha=candidate,
                    require_behavioral_pass=True,
                )
            with self.assertRaises(ValueError):
                validate_release_evidence(
                    {**record, "behavioral_conformance": {"status": "INCOMPLETE"}},
                    repo_root=root,
                    expected_candidate_sha=candidate,
                    require_behavioral_pass=True,
                )

    def test_complete_behavioral_report_can_be_attached_after_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills/cognitive-os").mkdir(parents=True)
            (root / "evals/e2e").mkdir(parents=True)
            (root / "manifests").mkdir()
            (root / "skills/cognitive-os/VERSION").write_text("1.5.0\n", encoding="utf-8")
            (root / "skills/cognitive-os/SKILL.md").write_text("# skill\n", encoding="utf-8")
            (root / "evals/v1.5-cases.json").write_text("[]\n", encoding="utf-8")
            (root / "evals/v1.5-output-cases.json").write_text("[]\n", encoding="utf-8")
            (root / "evals/e2e/harness.py").write_text("# harness\n", encoding="utf-8")
            (root / "manifests/package.json").write_text('{"version":"1.5.0"}\n', encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
            subprocess.run(["git", "add", "skills", "evals", "manifests"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "candidate"], cwd=root, check=True)
            candidate = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            source_fingerprint = source_tree_fingerprint(candidate, cwd=root)
            eval_hash = _candidate_eval_bundle_hash(candidate, root)
            sut_identity = {"provider": "remote-sut", "name": "sut-model", "fingerprint": "a" * 64, "observed": True}
            grader_identity = {"provider": "remote-grader", "name": "grader-model", "fingerprint": "b" * 64, "observed": True}
            report = {
                "schema": "cognitive-os-conformance-v4",
                "phase": "grade",
                "candidate_sha": candidate,
                "source_fingerprint": source_fingerprint,
                "eval_rubric_hash": eval_hash,
                "status": "COMPLETE",
                "overall": "PASS",
                "cases": 58,
                "completed_case_count": 58,
                "pass_count": 58,
                "required_pass_count": 56,
                "selection_complete": True,
                "critical_coverage_complete": True,
                "critical_failures": [],
                "incomplete_case_ids": [],
                "provider_identity_observed": {"sut": True, "grader": True},
                "sut_model_identity": sut_identity,
                "grader_model_identity": grader_identity,
                "grader_independent": True,
                "release_gate_eligible": True,
            }
            report_path = "docs/evidence/conformance-v1.5-candidate.json"
            report_bytes = (json.dumps(report, indent=2) + "\n").encode("utf-8")
            (root / report_path).parent.mkdir(parents=True)
            (root / report_path).write_bytes(report_bytes)
            subprocess.run(["git", "add", report_path], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "attach behavioral evidence"], cwd=root, check=True)
            record = {
                "schema_version": "cognitive-os-release-evidence-v1.5",
                "repository": "FilipeGCB/cognitive-os",
                "candidate_sha": candidate,
                "version": "1.5.0",
                "source_tree_fingerprint": source_fingerprint,
                "manifests": [{
                    "path": "manifests/package.json",
                    "sha256": sha256_bytes((root / "manifests/package.json").read_bytes()),
                    "source_commit": candidate,
                    "version": "1.5.0",
                }],
                "harness": {
                    "path": "evals/e2e/harness.py",
                    "sha256": sha256_bytes((root / "evals/e2e/harness.py").read_bytes()),
                    "schema_version": "harness-v1.5",
                },
                "execution": {
                    "run_id": "CRR-20260904-120000-ABCD",
                    "started_at": "2026-09-04T12:00:00Z",
                    "finished_at": "2026-09-04T12:01:00Z",
                    "candidate_sha": candidate,
                    "artifact_refs": ["manifests/package.json", report_path],
                    "host_observed_identity": True,
                },
                "sut_models": ["remote-sut/sut-model"],
                "grader_models": ["remote-grader/grader-model"],
                "runtime_hosts": ["generic-remote"],
                "tests": {
                    "total": 1,
                    "passed": 1,
                    "failed": 0,
                    "critical_failures": [],
                    "conformance_schema": "cognitive-os-conformance-v4",
                    "grader_independent": True,
                    "model_results": [],
                },
                "behavioral_conformance": {
                    "schema": "cognitive-os-conformance-v4",
                    "status": "COMPLETE",
                    "overall": "PASS",
                    "suite": "v1.5",
                    "profile": "final",
                    "candidate_sha": candidate,
                    "source_fingerprint": source_fingerprint,
                    "eval_rubric_hash": eval_hash,
                    "selection_complete": True,
                    "critical_coverage_complete": True,
                    "case_count": 58,
                    "completed_case_count": 58,
                    "pass_count": 58,
                    "required_pass_count": 56,
                    "critical_failures": [],
                    "incomplete_case_ids": [],
                    "sut_identity": sut_identity,
                    "grader_identity": grader_identity,
                    "grader_independent": True,
                    "report": {
                        "path": report_path,
                        "sha256": sha256_bytes(report_bytes),
                        "source_commit": candidate,
                    },
                },
                "critical_gates": {"contracts": "PASS"},
                "hermes_e2e": {"state": "UNAVAILABLE", "evidence_refs": []},
                "work": {"state": "UNAVAILABLE", "evidence_refs": []},
                "distribution": {"state": "PASS", "evidence_refs": []},
                "telemetry": {"state": "UNAVAILABLE", "evidence_refs": []},
                "collector": {"state": "UNAVAILABLE", "evidence_refs": []},
                "known_limitations": ["synthetic deterministic fixture"],
            }
            validate_release_evidence(record, repo_root=root, expected_candidate_sha=candidate)


if __name__ == "__main__":
    unittest.main()

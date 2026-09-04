import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_is_downstream_of_green_main_ci(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('workflows: ["ci"]', text)
        self.assertIn("workflow_run.conclusion == 'success'", text)
        self.assertIn("workflow_run.head_branch == 'main'", text)

    def test_release_requires_explicit_evidence_gate(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("RELEASE_GATE: PASS", text)
        self.assertIn("skills/cognitive-os/VERSION", text)
        self.assertIn("gh release create", text)

    def test_release_requires_machine_candidate_evidence(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("validate_release_evidence.py", text)
        self.assertIn("--candidate-sha", text)
        self.assertIn("VERIFIED_SHA", text)

    def test_release_evidence_validator_rejects_expected_sha_mismatch(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from validate_release_evidence import ReleaseEvidenceError, validate_release_evidence

        record = {
            "schema_version": "cognitive-os-release-evidence-v1.5",
            "repository": "FilipeGCB/cognitive-os",
            "candidate_sha": "0" * 40,
            "version": "1.5.0-dev",
            "source_tree_fingerprint": "0" * 64,
            "manifests": [],
            "harness": {},
            "execution": {},
            "sut_models": ["model"],
            "grader_models": ["grader"],
            "runtime_hosts": ["host"],
            "tests": {},
            "critical_gates": {"contracts": "PASS"},
            "hermes_e2e": {"state": "UNAVAILABLE", "evidence_refs": []},
            "work": {"state": "UNAVAILABLE", "evidence_refs": []},
            "distribution": {"state": "PASS", "evidence_refs": []},
            "telemetry": {"state": "UNAVAILABLE", "evidence_refs": []},
            "collector": {"state": "UNAVAILABLE", "evidence_refs": []},
            "known_limitations": ["not a real evidence record"],
        }
        with self.assertRaises(ReleaseEvidenceError):
            validate_release_evidence(record, expected_candidate_sha="1" * 40)


if __name__ == "__main__":
    unittest.main()

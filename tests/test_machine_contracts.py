import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_contracts import (  # noqa: E402
    ContractError,
    derive_execution_state,
    validate_capability_decision,
    validate_evidence_ref,
    validate_run_record,
)


class MachineContractTests(unittest.TestCase):
    def test_authenticated_but_not_consented_capability_is_not_executed(self):
        self.assertEqual(
            derive_execution_state(
                "AVAILABLE",
                "AUTHENTICATED",
                "NOT_GRANTED",
                "NOT_CALLED",
                None,
                consent_required=True,
            ),
            "AVAILABLE_NOT_EXERCISED",
        )

    def test_account_bound_success_without_run_consent_is_invalid(self):
        with self.assertRaises(ContractError):
            derive_execution_state(
                "AVAILABLE",
                "AUTHENTICATED",
                "NOT_GRANTED",
                "CALLED",
                "SUCCESS",
                consent_required=True,
            )

    def test_execution_requires_runtime_evidence_and_valid_state(self):
        with self.assertRaises(ContractError):
            derive_execution_state(
                "UNKNOWN",
                "UNKNOWN",
                "NOT_REQUIRED",
                "CALLED",
                "SUCCESS",
            )

    def test_run_record_rejects_unknown_fields(self):
        record = {
            "id": "CRR-20260904-120000-ABCD",
            "schema_version": "cognitive-os-run-record-v1.5",
            "created_at": "2026-09-04T12:00:00Z",
            "host": "hermes",
            "surface": "cli-profile:cognitive-os-e2e",
            "depth": "normal",
            "flow_coverage": "COMPLETE",
            "execution_integrity": "COMPLETE",
            "run_status": "COMPLETE",
            "decision_state": "TEST_REQUIRED",
            "provenance": "HOST_OBSERVED",
            "phase_ledger": [],
            "conditional_branch_ledger": [],
            "capability_ledger": [],
            "method_ledger": [],
            "evidence_ledger": [],
            "gap_failure_ledger": [],
            "challenge_ledger": [],
            "mutation_ledger": [],
            "persistent_side_effects": [],
            "research_budget": {"planned": {}, "consumed": {}, "stop_reason": "none"},
            "provider_host_failures": [],
            "stop": {"state": "STOP", "reason": "bounded"},
            "next_proof": None,
            "telemetry": {"mode": "OFF", "state": "NOT_CONFIGURED"},
            "private_reasoning": "must never be accepted",
        }
        with self.assertRaises(ContractError):
            validate_run_record(record)

    def test_run_record_requires_host_provenance_for_identity(self):
        record = {
            "id": "CRR-20260904-120000-ABCD",
            "schema_version": "cognitive-os-run-record-v1.5",
            "created_at": "2026-09-04T12:00:00Z",
            "host": "hermes",
            "surface": "cli-profile:cognitive-os-e2e",
            "depth": "normal",
            "flow_coverage": "COMPLETE",
            "execution_integrity": "COMPLETE",
            "run_status": "COMPLETE",
            "decision_state": "TEST_REQUIRED",
            "provenance": "MODEL_SYNTHESIZED",
            "phase_ledger": [],
            "conditional_branch_ledger": [],
            "capability_ledger": [],
            "method_ledger": [],
            "evidence_ledger": [],
            "gap_failure_ledger": [],
            "challenge_ledger": [],
            "mutation_ledger": [],
            "persistent_side_effects": [],
            "research_budget": {"planned": {}, "consumed": {}, "stop_reason": "none"},
            "provider_host_failures": [],
            "stop": {"state": "STOP", "reason": "bounded"},
            "next_proof": None,
            "telemetry": {"mode": "OFF", "state": "NOT_CONFIGURED"},
        }
        with self.assertRaises(ContractError):
            validate_run_record(record)

    def test_capability_decision_rejects_success_without_evidence_ref(self):
        record = {
            "id": "CAP-20260904-ABCD",
            "schema_version": "cognitive-os-capability-decision-v1.5",
            "capability": "Grounded Corpus Research",
            "discovery_class": "EXISTING_CAPABILITY",
            "source_or_adapter": "NotebookLM",
            "candidate_provenance": {
                "source": "host-runtime",
                "provenance_class": "HOST_OBSERVED",
            },
            "availability": "AVAILABLE",
            "auth_state": "AUTHENTICATED",
            "run_consent_state": "GRANTED",
            "invocation": "CALLED",
            "result": "SUCCESS",
            "consent_required": True,
            "adoption_state": "APPROVED",
            "evidence_refs": [],
        }
        with self.assertRaises(ContractError):
            validate_capability_decision(record)

    def test_evidence_ref_rejects_embedded_free_text(self):
        with self.assertRaises(ContractError):
            validate_evidence_ref("response: user email is test@example.com")
        self.assertTrue(validate_evidence_ref("run://CRR-20260904-120000-ABCD/tool/call-1"))

    def test_executable_schema_files_are_strict_json(self):
        schemas = ROOT / "skills" / "cognitive-os" / "schemas"
        for name in (
            "cognitive-run-record.schema.json",
            "capability-decision-record.schema.json",
        ):
            data = json.loads((schemas / name).read_text(encoding="utf-8"))
            self.assertEqual(data["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertFalse(data["additionalProperties"])


if __name__ == "__main__":
    unittest.main()

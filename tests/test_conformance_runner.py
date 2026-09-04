import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "evals" / "run_local_conformance.py"

spec = importlib.util.spec_from_file_location("run_local_conformance", RUNNER_PATH)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runner)


class ConformanceRunnerTests(unittest.TestCase):
    def test_audit_cases_get_enough_generation_budget_for_observable_ledgers(self):
        self.assertEqual(runner.response_num_predict_for([]), 600)
        self.assertGreaterEqual(runner.response_num_predict_for(["audit"]), 1800)
        self.assertGreaterEqual(runner.response_num_predict_for(["audit-preserved"]), 1800)

    def test_grader_contract_does_not_confuse_observable_audit_ledgers_with_chain_of_thought(self):
        prompt = runner.grader_system_prompt(["audit", "no-chain-of-thought"]).lower()
        self.assertIn("observable audit", prompt)
        self.assertIn("must not be treated as private chain-of-thought", prompt)
        self.assertIn("hidden step-by-step", prompt)

    def test_deterministic_response_flags_expose_truncation_and_unobserved_identity(self):
        flags = runner.response_flags(
            "run_id: CRR-20260904-120000-ABCD\ncreated_at: 2026-09-04T12:00:00Z",
            {"done_reason": "length"},
            tags=["audit", "runtime-evidence"],
        )
        self.assertTrue(flags["truncated"])
        self.assertTrue(flags["invented_identity"])

    def test_v15_cases_mark_critical_gates_for_model_specific_reduction(self):
        cases = runner.load_cases([ROOT / "evals" / "v1.5-cases.json", ROOT / "evals" / "v1.5-output-cases.json"])
        self.assertTrue(any(case.get("critical") for case in cases))
        self.assertTrue(any(case["id"] == "RC-01" and case.get("critical") for case in cases))


if __name__ == "__main__":
    unittest.main()

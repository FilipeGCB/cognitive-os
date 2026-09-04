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


if __name__ == "__main__":
    unittest.main()

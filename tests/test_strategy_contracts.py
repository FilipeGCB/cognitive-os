import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_strategy import (  # noqa: E402
    GroundedClaim,
    classify_capability_opportunity,
    classify_positioning,
    reconcile_before_diagnosis,
    validate_grounded_order,
)


class StrategyContractTests(unittest.TestCase):
    def test_source_precedes_interpretation(self):
        with self.assertRaises(ValueError):
            validate_grounded_order([GroundedClaim("h", "HYPOTHESIS", (), "VALUE")])
        self.assertEqual(
            validate_grounded_order([
                GroundedClaim("f", "FACT", ("repo://tests",), "SOFTWARE", True),
                GroundedClaim("h", "HYPOTHESIS", (), "VALUE"),
                GroundedClaim("r", "RECOMMENDATION", ("repo://tests",), "VALUE"),
            ]),
            ("f", "h", "r"),
        )

    def test_positioning_requires_audience_problem_and_outcome(self):
        self.assertEqual(classify_positioning(audience="operators", problem="drift", outcome="faster closure", mechanism="trace"), "NEW_OPPORTUNITY")
        self.assertEqual(classify_positioning(audience="operators", problem=None, outcome="faster closure", mechanism="trace"), "INSUFFICIENT_POSITIONING")

    def test_existing_capability_is_not_automatically_new_opportunity(self):
        self.assertEqual(
            classify_capability_opportunity(existing_capability=True, audience="teams", problem="decisions", outcome="clarity"),
            "REPACKAGING",
        )
        self.assertEqual(
            classify_capability_opportunity(existing_capability=True, audience="teams", problem="decisions", outcome="clarity", materially_new_job=True),
            "NEW_OPPORTUNITY",
        )

    def test_reconcile_first_exposes_semantic_contradiction(self):
        result = reconcile_before_diagnosis({"transaction": {"payment_ledger": 10, "analytics": 12}})
        self.assertEqual(result["selected"]["transaction"], 10)
        self.assertIn("transaction", result["contradictions"])
        self.assertFalse(result["diagnosis_allowed"])


if __name__ == "__main__":
    unittest.main()

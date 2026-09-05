import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_bootstrap import (  # noqa: E402
    BudgetCounter,
    ResearchBudget,
    build_research_plan,
    build_truth_domain_map,
    close_after_research_limit,
    research_checkpoint,
    should_migrate_to_corpus,
)


class ResearchBudgetTests(unittest.TestCase):
    def test_deep_research_requires_plan_and_observable_counters(self):
        budget = ResearchBudget(
            web_calls=BudgetCounter(0, 8, 12),
            source_count=BudgetCounter(0, 10, 16),
            context_fraction=BudgetCounter(None, None, None, observable=False),
        )
        plan = build_research_plan(
            "Should we adopt this capability?",
            ["What problem does it solve?", "What does it cost?"],
            ["official docs", "repository"],
            ["current permissions", "maintenance state"],
            budget,
            "stop when material uncertainty is reduced or next proof is cheaper",
        )
        self.assertEqual(plan.budget.web_calls.hard_limit, 12)
        self.assertIsNone(plan.budget.context_fraction.value)
        self.assertFalse(plan.budget.context_fraction.observable)

    def test_checkpoint_reserves_capacity_before_hard_limit(self):
        budget = ResearchBudget(
            web_calls=BudgetCounter(0, 8, 12),
            source_count=BudgetCounter(0, 10, 16),
        )
        self.assertEqual(research_checkpoint(budget, {"web_calls": 6, "source_count": 5}), "CHECKPOINT_50")
        self.assertEqual(research_checkpoint(budget, {"web_calls": 10, "source_count": 12}), "CHECKPOINT_80")
        self.assertEqual(research_checkpoint(budget, {"web_calls": 12, "source_count": 16}), "FREEZE_AND_SYNTHESIZE")

    def test_web_to_corpus_migration_uses_soft_observable_signals(self):
        self.assertTrue(should_migrate_to_corpus({"material_sources": 12}))
        self.assertTrue(should_migrate_to_corpus({"internal_and_external": True}))
        self.assertTrue(should_migrate_to_corpus({"repeated_queries": 2}))
        self.assertTrue(should_migrate_to_corpus({"compaction_observed": True}))
        self.assertFalse(should_migrate_to_corpus({"context_fraction": 0.8, "context_observable": False}))
        self.assertTrue(should_migrate_to_corpus({"context_fraction": 0.8, "context_observable": True}))

    def test_hard_limit_closes_from_useful_observable_state(self):
        closure = close_after_research_limit(
            {
                "evidence_refs": ["web://source-1", "web://source-2"],
                "material_gap": "pricing remains unverified",
                "fallback": "bounded experiment",
                "failure": "RATE_LIMITED",
            }
        )
        self.assertEqual(closure["run_status"], "COMPLETE")
        self.assertEqual(closure["execution_integrity"], "PARTIAL")
        self.assertEqual(closure["stop"], "STOP_RESEARCH_AND_TEST")
        self.assertTrue(closure["next_proof"])

    def test_truth_domain_map_does_not_equate_semantically_different_systems(self):
        mapping = build_truth_domain_map()
        self.assertEqual(mapping["transaction"]["preferred"], "payment_ledger")
        self.assertEqual(mapping["order"]["preferred"], "commerce")
        self.assertEqual(mapping["behavior"]["preferred"], "analytics")
        self.assertNotEqual(mapping["transaction"]["preferred"], mapping["behavior"]["preferred"])


if __name__ == "__main__":
    unittest.main()

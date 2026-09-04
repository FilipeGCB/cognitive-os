import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_resilience import close_provider_failure, resolve_reasoning_effort  # noqa: E402


class ProviderResilienceTests(unittest.TestCase):
    def test_unsupported_effort_degrades_only_to_observed_supported_setting(self):
        resolution = resolve_reasoning_effort("high", ["low", "medium"])
        self.assertEqual(resolution.state, "DEGRADED")
        self.assertEqual(resolution.selected, "medium")
        self.assertEqual(resolution.fallback, "SUPPORTED_SETTING")

    def test_no_exposed_supported_parameter_is_limitation_not_fake_fallback(self):
        resolution = resolve_reasoning_effort("high", [])
        self.assertIsNone(resolution.selected)
        self.assertEqual(resolution.state, "UNAVAILABLE")

    def test_provider_failure_emits_minimal_closure(self):
        result = close_provider_failure(
            provider_or_host="local-provider",
            failure_class="RATE_LIMITED",
            observable_state={"evidence_refs": ["run://CRR-20260904-120000-ABCD/evidence/1"], "material_gap": "validation pending"},
        )
        self.assertTrue(result["closure_emitted"])
        self.assertEqual(result["run_status"], "COMPLETE")
        self.assertEqual(result["fallback"], "PERSISTED_RUN_STATE")


if __name__ == "__main__":
    unittest.main()

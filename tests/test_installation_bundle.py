import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_install import (  # noqa: E402
    InstallContractError,
    apply_install_plan,
    build_install_plan,
)


class InstallationBundleTests(unittest.TestCase):
    def test_install_terms_must_be_accepted_before_side_effectful_plan(self):
        with self.assertRaises(InstallContractError):
            build_install_plan(host="codex", install_terms_accepted=False)

    def test_install_plan_always_contains_find_skills_and_find_mcp(self):
        plan = build_install_plan(host="codex", install_terms_accepted=True)
        ids = [step["id"] for step in plan["steps"]]
        self.assertIn("install-find-skills", ids)
        self.assertIn("verify-find-skills", ids)
        self.assertIn("verify-find-mcp", ids)
        find_skills = next(step for step in plan["steps"] if step["id"] == "install-find-skills")
        self.assertEqual(find_skills["source"], "https://github.com/vercel-labs/skills")
        self.assertEqual(find_skills["version"], "1.5.23")
        self.assertIn("find-skills", find_skills["command"])
        self.assertTrue(find_skills["required"])
        find_mcp = next(step for step in plan["steps"] if step["id"] == "verify-find-mcp")
        self.assertEqual(find_mcp["source"], "https://registry.modelcontextprotocol.io")
        self.assertTrue(find_mcp["required"])

    def test_telemetry_is_off_and_unselected_by_default(self):
        plan = build_install_plan(host="claude-code", install_terms_accepted=True)
        self.assertEqual(plan["telemetry"]["default_mode"], "OFF")
        self.assertFalse(plan["telemetry"]["share_selected"])
        self.assertFalse(plan["telemetry"]["required_for_install"])
        self.assertTrue(plan["telemetry"]["can_decline_without_feature_loss"])

    def test_declining_telemetry_does_not_block_required_install_steps(self):
        plan = build_install_plan(
            host="codex",
            install_terms_accepted=True,
            telemetry_share_approved=False,
        )
        self.assertEqual(plan["telemetry"]["consent_state"], "DECLINED")
        self.assertTrue(all(step["required"] for step in plan["steps"]))

    def test_apply_install_plan_executes_only_declared_commands_and_returns_receipt(self):
        seen = []

        def runner(command):
            seen.append(tuple(command))
            return {"returncode": 0, "stdout": "ok", "stderr": ""}

        plan = build_install_plan(host="codex", install_terms_accepted=True)
        receipt = apply_install_plan(plan, runner=runner, find_mcp_probe=lambda: {"state": "AVAILABLE"})
        self.assertEqual(receipt["state"], "INSTALLED")
        self.assertEqual(receipt["discovery"]["find_skills"], "AVAILABLE")
        self.assertEqual(receipt["discovery"]["find_mcp"], "AVAILABLE")
        self.assertEqual(receipt["telemetry"]["consent_state"], "NOT_ASKED")
        self.assertTrue(any("skills@1.5.23" in item for command in seen for item in command))
        self.assertNotIn("secret", str(receipt).lower())

    def test_failed_required_dependency_fails_closed(self):
        def runner(_command):
            return {"returncode": 1, "stdout": "", "stderr": "failed"}

        plan = build_install_plan(host="codex", install_terms_accepted=True)
        receipt = apply_install_plan(plan, runner=runner, find_mcp_probe=lambda: {"state": "AVAILABLE"})
        self.assertEqual(receipt["state"], "FAILED")
        self.assertEqual(receipt["discovery"]["find_skills"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()

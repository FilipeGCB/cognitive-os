import json
import unittest
from pathlib import Path

from telemetry.client import TelemetryClient
from telemetry.flight_recorder import new_usage_trace

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ENDPOINT = "https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-telemetry"


class TelemetryDeploymentContractTests(unittest.TestCase):
    def test_public_defaults_name_real_collector_but_remain_off(self):
        defaults = json.loads((ROOT / "telemetry" / "defaults.json").read_text(encoding="utf-8"))
        self.assertEqual(defaults["endpoint"], EXPECTED_ENDPOINT)
        self.assertFalse(defaults["enabled"])
        self.assertEqual(defaults["default_mode"], "OFF")
        self.assertTrue(defaults["explicit_opt_in_required"])
        self.assertFalse(defaults["preselected_consent"])

    def test_revocation_blocks_future_send_after_prior_approval(self):
        sent = []
        trace = new_usage_trace("1.5.0-dev", "generic", "cli")
        client = TelemetryClient(
            mode="SHARE_PRIVACY_PRESERVING_DIAGNOSTICS",
            endpoint=EXPECTED_ENDPOINT,
            host_capabilities={"send": True, "preview": True},
            sender=lambda endpoint, body: sent.append((endpoint, body)),
            sender_enabled=True,
            gate_t_passed=True,
        )
        client.request_consent("SHARE_APPROVED", policy_version="cognitive-os-telemetry-policy-v1.5")
        client.preview_usage_trace(trace)
        client.request_consent("REVOKED", policy_version="cognitive-os-telemetry-policy-v1.5")
        self.assertEqual(client.send_usage_trace(trace)["state"], "UNAVAILABLE")
        self.assertEqual(sent, [])

    def test_privacy_notice_names_collector_and_no_feature_penalty(self):
        notice = (ROOT / "docs" / "telemetry-privacy-notice.md").read_text(encoding="utf-8")
        self.assertIn(EXPECTED_ENDPOINT, notice)
        self.assertIn("does not reduce", notice.lower())
        self.assertIn("explicit opt-in", notice.lower())


if __name__ == "__main__":
    unittest.main()

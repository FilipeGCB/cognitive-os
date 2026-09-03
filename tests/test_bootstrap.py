import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_bootstrap import CapabilitySnapshot, ConsentProfile, plan_gap_fill


class BootstrapTests(unittest.TestCase):
    def test_existing_capability_prevents_install(self):
        snap = CapabilitySnapshot("Grounded Corpus Research", "AVAILABLE", "host-native")
        decision = plan_gap_fill(snap, ConsentProfile(True), [])
        self.assertEqual(decision.action, "USE_EXISTING")
        self.assertEqual(decision.candidate_id, "host-native")

    def test_heavy_candidate_requires_specific_confirmation(self):
        snap = CapabilitySnapshot("Grounded Corpus Research", "UNAVAILABLE", None)
        candidates = [{
            "id": "local-rag",
            "approved": True,
            "user_space": True,
            "light": False,
            "reversible": True,
            "heavy": True,
            "account": False,
            "secret": False,
            "sensitive_persistent_access": False,
            "write": False,
            "privileged": False,
        }]
        decision = plan_gap_fill(snap, ConsentProfile(True), candidates)
        self.assertEqual(decision.action, "ASK_SPECIFIC_CONSENT")

    def test_safe_light_candidate_can_use_one_time_consent(self):
        snap = CapabilitySnapshot("Example Capability", "UNAVAILABLE", None)
        candidates = [{
            "id": "safe-tool",
            "approved": True,
            "user_space": True,
            "light": True,
            "reversible": True,
            "heavy": False,
            "account": False,
            "secret": False,
            "sensitive_persistent_access": False,
            "write": False,
            "privileged": False,
        }]
        decision = plan_gap_fill(snap, ConsentProfile(True), candidates)
        self.assertEqual(decision.action, "AUTO_INSTALL_ALLOWED")

    def test_one_time_consent_never_covers_external_account(self):
        snap = CapabilitySnapshot("Grounded Corpus Research", "UNAVAILABLE", None)
        candidates = [{
            "id": "account-tool",
            "approved": True,
            "user_space": True,
            "light": True,
            "reversible": True,
            "heavy": False,
            "account": True,
            "secret": True,
            "sensitive_persistent_access": True,
            "write": False,
            "privileged": False,
        }]
        decision = plan_gap_fill(snap, ConsentProfile(True), candidates)
        self.assertEqual(decision.action, "ASK_SPECIFIC_CONSENT")


if __name__ == "__main__":
    unittest.main()

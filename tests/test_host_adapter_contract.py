import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_host import HostAdapterContract, capability_matrix_entry  # noqa: E402


class HostAdapterContractTests(unittest.TestCase):
    def test_unknown_host_capabilities_are_unknown_not_available(self):
        contract = HostAdapterContract("generic", "unknown", {"SearchWeb": "UNAVAILABLE"}, {})
        self.assertEqual(contract.availability("UseGroundedCorpus"), "UNKNOWN")
        self.assertFalse(contract.can_claim_runtime_use("SearchWeb", "model-prose"))

    def test_runtime_claim_requires_matching_observed_evidence(self):
        contract = HostAdapterContract("hermes", "cli", {"SearchWeb": "AVAILABLE"}, {"SearchWeb": ("session://run-1/tool-1",)})
        self.assertTrue(contract.can_claim_runtime_use("SearchWeb", "session://run-1/tool-1"))
        self.assertFalse(contract.can_claim_runtime_use("SearchWeb", "session://old/tool-1"))
        self.assertEqual(capability_matrix_entry(contract, "SearchWeb")["runtime_claim_allowed"], True)

    def test_unknown_abstract_capability_is_rejected(self):
        with self.assertRaises(ValueError):
            HostAdapterContract("generic", "cli", {"MadeUp": "AVAILABLE"}, {})


if __name__ == "__main__":
    unittest.main()

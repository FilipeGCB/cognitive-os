import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "cognitive-os" / "scripts" / "find_mcp.py"


class InstalledFindMcpBundleTests(unittest.TestCase):
    def test_find_mcp_client_is_part_of_skill_directory(self):
        self.assertTrue(SCRIPT.is_file(), "Find MCP must be copied with the cognitive-os skill")

    def test_bundled_client_targets_only_official_registry(self):
        spec = importlib.util.spec_from_file_location("cognitive_os_installed_find_mcp", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        self.assertEqual(module.MCP_REGISTRY_BASE_URL, "https://registry.modelcontextprotocol.io")
        self.assertEqual(module.MCP_REGISTRY_SERVERS_PATH, "/v0.1/servers")
        self.assertEqual(module.self_check()["state"], "READY")


if __name__ == "__main__":
    unittest.main()

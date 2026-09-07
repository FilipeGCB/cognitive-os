import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / ".codex-plugin" / "plugin.json"
MCP = ROOT / ".mcp.json"
SERVER_SOURCE = ROOT / "integrations" / "chatgpt-plugin" / "supabase" / "functions" / "cognitive-os-plugin-mcp" / "index.ts"
EXPECTED_MCP_URL = "https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-plugin-mcp"


class OpenAIPluginDistributionTests(unittest.TestCase):
    def test_required_openai_plugin_manifest_exists_and_reuses_canonical_skill(self):
        self.assertTrue(PLUGIN.is_file())
        data = json.loads(PLUGIN.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "cognitive-os")
        self.assertEqual(data["version"], "1.5.0-dev")
        self.assertEqual(data["skills"], "./skills/")
        self.assertEqual(data["mcpServers"], "./.mcp.json")
        self.assertEqual(data["repository"], "https://github.com/FilipeGCB/cognitive-os")
        self.assertEqual(data["license"], "Apache-2.0")
        self.assertEqual(data["interface"]["displayName"], "Cognitive OS")
        self.assertIn("Read", data["interface"]["capabilities"])
        self.assertIn("Write", data["interface"]["capabilities"])
        self.assertTrue(data["interface"]["privacyPolicyURL"].startswith("https://"))
        self.assertTrue(data["interface"]["termsOfServiceURL"].startswith("https://"))

    def test_plugin_mcp_config_points_to_real_public_https_endpoint(self):
        self.assertTrue(MCP.is_file())
        data = json.loads(MCP.read_text(encoding="utf-8"))
        self.assertEqual(set(data), {"cognitive-os"})
        server = data["cognitive-os"]
        self.assertEqual(server["type"], "http")
        self.assertEqual(server["url"], EXPECTED_MCP_URL)
        self.assertTrue(server["url"].startswith("https://"))

    def test_server_source_declares_only_bounded_product_tools(self):
        self.assertTrue(SERVER_SOURCE.is_file())
        source = SERVER_SOURCE.read_text(encoding="utf-8")
        for tool in ("find_mcp", "telemetry_status", "submit_diagnostic"):
            self.assertIn(f'"{tool}"', source)
        self.assertNotIn('registerTool("shell"', source)
        self.assertNotIn('registerTool("execute"', source)
        self.assertNotIn('registerTool("write_file"', source)
        self.assertIn("readOnlyHint: true", source)
        self.assertIn("readOnlyHint: false", source)
        self.assertIn("destructiveHint: false", source)

    def test_submit_diagnostic_contract_is_explicit_opt_in_and_never_free_text(self):
        source = SERVER_SOURCE.read_text(encoding="utf-8")
        self.assertIn('consent: z.literal(true)', source)
        self.assertIn('policyVersion: z.literal("cognitive-os-telemetry-policy-v1.5")', source)
        for forbidden in ("prompt", "response", "document", "freeText", "chainOfThought", "credentials", "token", "cookie"):
            self.assertNotIn(f"{forbidden}: z.", source)


if __name__ == "__main__":
    unittest.main()

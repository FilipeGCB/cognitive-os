import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_SOURCE = ROOT / "integrations" / "chatgpt-plugin" / "supabase" / "functions" / "cognitive-os-plugin-mcp" / "index.ts"


class OpenAITelemetryConsentUITests(unittest.TestCase):
    def test_consent_ui_is_an_mcp_app_resource(self):
        source = SERVER_SOURCE.read_text(encoding="utf-8")
        self.assertIn('const TELEMETRY_UI_URI = "ui://cognitive-os/telemetry-consent-v1.html"', source)
        self.assertIn('server.registerResource("telemetry-consent-widget"', source)
        self.assertIn('mimeType: "text/html;profile=mcp-app"', source)
        self.assertIn('ui: { resourceUri: TELEMETRY_UI_URI }', source)

    def test_checkbox_is_unchecked_and_user_controls_send(self):
        source = SERVER_SOURCE.read_text(encoding="utf-8")
        self.assertIn('<input id="consent" type="checkbox">', source)
        self.assertNotIn('<input id="consent" type="checkbox" checked', source)
        self.assertIn('sendButton.disabled = !consent.checked', source)
        self.assertIn('name: "submit_diagnostic"', source)
        self.assertIn('consent: true', source)
        self.assertIn('policyVersion: POLICY_VERSION', source)

    def test_ui_explains_data_boundary_and_refusal(self):
        source = SERVER_SOURCE.read_text(encoding="utf-8").lower()
        self.assertIn("off by default", source)
        self.assertIn("no feature loss", source)
        self.assertIn("never sends prompts", source)
        self.assertIn("privacy notice", source)


if __name__ == "__main__":
    unittest.main()

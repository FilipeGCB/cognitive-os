import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "chatgpt-app-submission.json"
EXPECTED_TOOLS = {
    "find_mcp",
    "telemetry_status",
    "render_telemetry_consent",
    "submit_diagnostic",
}


class ChatGPTAppSubmissionTests(unittest.TestCase):
    def test_submission_file_exists_and_has_expected_shape(self):
        self.assertTrue(SUBMISSION.is_file(), "chatgpt-app-submission.json must exist")
        data = json.loads(SUBMISSION.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["$schema"], "https://developers.openai.com/apps-sdk/schemas/chatgpt-app-submission.v1.json")
        self.assertEqual(data["app_info"]["display_name"], "Cognitive OS")
        self.assertLessEqual(len(data["app_info"]["subtitle"]), 30)
        self.assertEqual(data["app_info"]["category"], "PRODUCTIVITY")
        self.assertEqual(set(data["tools"]), EXPECTED_TOOLS)
        self.assertEqual(len(data["test_cases"]), 5)
        self.assertEqual(len(data["negative_test_cases"]), 3)

    def test_every_tool_has_explicit_review_hints_and_justifications(self):
        data = json.loads(SUBMISSION.read_text(encoding="utf-8"))
        for name, tool in data["tools"].items():
            with self.subTest(tool=name):
                annotations = tool["annotations"]
                self.assertEqual(set(annotations), {"readOnlyHint", "openWorldHint", "destructiveHint"})
                self.assertIsInstance(annotations["readOnlyHint"], bool)
                self.assertIsInstance(annotations["openWorldHint"], bool)
                self.assertIsInstance(annotations["destructiveHint"], bool)
                justifications = tool["justifications"]
                self.assertTrue(justifications["read_only_justification"])
                self.assertTrue(justifications["open_world_justification"])
                self.assertTrue(justifications["destructive_justification"])

    def test_submission_hints_match_source_behavior(self):
        data = json.loads(SUBMISSION.read_text(encoding="utf-8"))
        expected = {
            "find_mcp": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False},
            "telemetry_status": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False},
            "render_telemetry_consent": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False},
            "submit_diagnostic": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False},
        }
        for name, hints in expected.items():
            self.assertEqual(data["tools"][name]["annotations"], hints)

    def test_positive_tests_use_only_real_tool_names(self):
        data = json.loads(SUBMISSION.read_text(encoding="utf-8"))
        for case in data["test_cases"]:
            triggered = case["tools_triggered"]
            self.assertIn(triggered, EXPECTED_TOOLS)

    def test_negative_tests_trigger_no_tool(self):
        data = json.loads(SUBMISSION.read_text(encoding="utf-8"))
        self.assertTrue(all(case["tools_triggered"] is None for case in data["negative_test_cases"]))


if __name__ == "__main__":
    unittest.main()

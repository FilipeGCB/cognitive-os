import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "conformance.yml"


class ConformanceWorkflowTests(unittest.TestCase):
    def test_behavioral_conformance_is_manual_and_remote_explicit(self):
        text = WORKFLOW.read_text(encoding="utf-8").lower()
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("push:", text)
        self.assertIn("provider", text)
        self.assertIn("base_url", text)
        self.assertIn("api_key_env", text)
        self.assertIn("run_conformance.py", text)

    def test_workflow_has_no_local_model_transport_or_default(self):
        text = WORKFLOW.read_text(encoding="utf-8").lower()
        for forbidden in ("ollama", "qwen", "gemma", "127.0.0.1", "docker run", "model pull"):
            self.assertNotIn(forbidden, text)

    def test_deterministic_checks_live_in_ci_workflow(self):
        text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8").lower()
        self.assertIn("python -m unittest discover", text)
        self.assertIn("validate machine contracts", text)
        self.assertIn("public pii scan", text)

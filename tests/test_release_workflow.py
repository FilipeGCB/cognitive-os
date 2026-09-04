import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_is_downstream_of_green_main_ci(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('workflows: ["ci"]', text)
        self.assertIn("workflow_run.conclusion == 'success'", text)
        self.assertIn("workflow_run.head_branch == 'main'", text)

    def test_release_requires_explicit_evidence_gate(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("RELEASE_GATE: PASS", text)
        self.assertIn("skills/cognitive-os/VERSION", text)
        self.assertIn("gh release create", text)


if __name__ == "__main__":
    unittest.main()

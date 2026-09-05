import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
UPSTREAM_FIND_SKILLS_SHA = "435076e78988e1e6ec40d00b0b1d76bdbbc5419a"


class ClaudePluginDistributionTests(unittest.TestCase):
    def test_cognitive_os_plugin_auto_installs_find_skills_dependency(self):
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        plugins = {item["name"]: item for item in data["plugins"]}
        self.assertIn("cognitive-os", plugins)
        self.assertIn("find-skills", plugins)
        self.assertIn("find-skills", plugins["cognitive-os"].get("dependencies", []))

    def test_find_skills_dependency_is_pinned_to_verified_upstream_subdir(self):
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        plugins = {item["name"]: item for item in data["plugins"]}
        dep = plugins["find-skills"]
        source = dep["source"]
        self.assertEqual(source["source"], "git-subdir")
        self.assertEqual(source["url"], "https://github.com/vercel-labs/skills.git")
        self.assertEqual(source["path"], "skills/find-skills")
        self.assertEqual(source["sha"], UPSTREAM_FIND_SKILLS_SHA)
        self.assertEqual(dep["version"], "1.5.23")
        self.assertFalse(dep["strict"])

    def test_cognitive_os_claude_plugin_exposes_installed_find_mcp_script(self):
        self.assertTrue((ROOT / "skills" / "cognitive-os" / "scripts" / "find_mcp.py").is_file())
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        plugins = {item["name"]: item for item in data["plugins"]}
        self.assertEqual(plugins["cognitive-os"]["source"], "./")
        self.assertIn("./skills/cognitive-os", plugins["cognitive-os"]["skills"])


if __name__ == "__main__":
    unittest.main()

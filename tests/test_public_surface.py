import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublicSurfaceTests(unittest.TestCase):
    def test_public_repo_has_required_non_legal_docs(self):
        for name in ["README.md", "CHANGELOG.md", "CONTRIBUTING.md", ".gitignore"]:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_readme_has_fast_install_and_product_boundary(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("npx skills add", text)
        self.assertIn("decision", text)
        self.assertIn("not", text)
        self.assertIn("autonomous executor", text)

    def test_license_is_explicit_release_gate_until_selected(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("no license", text)
        self.assertIn("release gate", text)


if __name__ == "__main__":
    unittest.main()

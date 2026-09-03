import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublicSurfaceTests(unittest.TestCase):
    def test_public_repo_has_required_docs(self):
        for name in ["README.md", "CHANGELOG.md", "CONTRIBUTING.md", ".gitignore", "LICENSE"]:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_readme_has_fast_install_and_product_boundary(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("npx skills add", text)
        self.assertIn("decision", text)
        self.assertIn("not", text)
        self.assertIn("autonomous executor", text)

    def test_license_is_apache_2(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("Apache License", license_text)
        self.assertIn("Version 2.0", license_text)
        self.assertIn("apache license 2.0", readme)


if __name__ == "__main__":
    unittest.main()

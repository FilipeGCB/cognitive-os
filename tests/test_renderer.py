import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "renderers" / "decision-brief"))

from render import render_markdown


class RendererTests(unittest.TestCase):
    def test_renderer_emits_editorial_html_without_external_fonts(self):
        html = render_markdown("# Decision\n\n**Ready to advance.** Reason.")
        self.assertIn("<article", html)
        self.assertIn("system-ui", html)
        self.assertNotIn("fonts.googleapis.com", html)
        self.assertIn("prefers-color-scheme", html)

    def test_renderer_escapes_raw_html(self):
        rendered = render_markdown("# Test\n\n<script>alert('x')</script>")
        self.assertNotIn("<script>alert", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_renderer_supports_decision_tables(self):
        rendered = render_markdown("# T\n\n| A | B |\n|---|---|\n| 1 | 2 |")
        self.assertIn("<table>", rendered)
        self.assertIn("<th>A</th>", rendered)
        self.assertIn("<td>2</td>", rendered)


if __name__ == "__main__":
    unittest.main()

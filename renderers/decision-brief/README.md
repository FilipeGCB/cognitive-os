# Decision Brief HTML renderer

A small optional renderer for turning a Cognitive OS Markdown Decision Brief into a standalone editorial HTML document.

It is not part of cognitive truth and does not replace Markdown or the Decision Pack.

## Use

```bash
python renderers/decision-brief/render.py examples/decision-brief-idea-evolution.md decision.html
```

The renderer intentionally uses only the Python standard library and a limited Markdown subset. Raw HTML is escaped. The stylesheet uses a system font stack, responsive layout and light/dark color-scheme support; it downloads no fonts or external assets.

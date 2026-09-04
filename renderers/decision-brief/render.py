#!/usr/bin/env python3
"""Small dependency-free Markdown renderer for Cognitive OS Decision Briefs.

This intentionally supports only the portable subset used by our public examples.
Raw HTML is escaped rather than executed.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from typing import List

HERE = Path(__file__).resolve().parent


def _inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        escaped,
    )
    return escaped


def _is_table_separator(line: str) -> bool:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c) for c in cells)


def _table(lines: List[str]) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    header = rows[0]
    body = rows[2:]
    out = ["<table>", "<thead><tr>"]
    out.extend(f"<th>{_inline(cell)}</th>" for cell in header)
    out.append("</tr></thead>")
    if body:
        out.append("<tbody>")
        for row in body:
            out.append("<tr>")
            out.extend(f"<td>{_inline(cell)}</td>" for cell in row)
            out.append("</tr>")
        out.append("</tbody>")
    out.append("</table>")
    return "\n".join(out)


def markdown_to_body(markdown: str) -> str:
    lines = markdown.splitlines()
    out: List[str] = []
    paragraph: List[str] = []
    list_items: List[str] = []
    in_code = False
    code_lines: List[str] = []
    i = 0

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{_inline(' '.join(part.strip() for part in paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            out.append("<ul>")
            out.extend(f"<li>{_inline(item)}</li>" for item in list_items)
            out.append("</ul>")
            list_items.clear()

    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if (
            "|" in line
            and i + 1 < len(lines)
            and _is_table_separator(lines[i + 1])
        ):
            flush_paragraph()
            flush_list()
            table_lines = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            out.append(_table(table_lines))
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            i += 1
            continue

        if line.startswith("### "):
            flush_paragraph(); flush_list()
            out.append(f"<h3>{_inline(line[4:].strip())}</h3>")
        elif line.startswith("## "):
            flush_paragraph(); flush_list()
            out.append(f"<h2>{_inline(line[3:].strip())}</h2>")
        elif line.startswith("# "):
            flush_paragraph(); flush_list()
            out.append(f"<h1>{_inline(line[2:].strip())}</h1>")
        elif line.startswith("> "):
            flush_paragraph(); flush_list()
            out.append(f"<blockquote><p>{_inline(line[2:].strip())}</p></blockquote>")
        elif line.startswith("- "):
            flush_paragraph()
            list_items.append(line[2:].strip())
        else:
            flush_list()
            paragraph.append(line)
        i += 1

    if in_code:
        out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    flush_paragraph()
    flush_list()
    return "\n".join(out)


def render_markdown(markdown: str) -> str:
    title = "Decision Brief"
    for line in markdown.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    template = (HERE / "template.html").read_text(encoding="utf-8")
    css = (HERE / "decision-brief.css").read_text(encoding="utf-8")
    body = markdown_to_body(markdown)
    return (
        template.replace("{{TITLE}}", html.escape(title))
        .replace("{{CSS}}", css)
        .replace("{{BODY}}", body)
    )


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print("usage: render.py INPUT.md OUTPUT.html", file=sys.stderr)
        return 2
    source = Path(argv[1])
    target = Path(argv[2])
    target.write_text(render_markdown(source.read_text(encoding="utf-8")), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
"""Validate local Markdown references inside the canonical Cognitive OS skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME = ROOT / "skills" / "cognitive-os"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}


def _target_path(source: Path, raw_target: str, runtime_root: Path) -> tuple[Path | None, str | None]:
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return None, None
    # Markdown permits optional title after a URL. The Cognitive OS runtime uses
    # simple links; only the first token is interpreted as the target.
    if target.startswith("<") and ">" in target:
        target = target[1:target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    parsed = urlsplit(target)
    if parsed.scheme.lower() in EXTERNAL_SCHEMES or target.startswith("//"):
        return None, None
    local = unquote(parsed.path)
    if not local:
        return None, None
    if local.startswith("/"):
        return None, "absolute local references are not allowed"
    candidate = (source.parent / local).resolve()
    root = runtime_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, "escapes runtime root"
    return candidate, None


def validate_runtime_references(runtime_root: Path = DEFAULT_RUNTIME) -> list[str]:
    runtime_root = Path(runtime_root)
    findings: list[str] = []
    if not runtime_root.is_dir():
        return [f"runtime root not found: {runtime_root}"]
    skill = runtime_root / "SKILL.md"
    if not skill.is_file():
        findings.append("missing SKILL.md")
    for source in sorted(runtime_root.rglob("*.md")):
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"{source.relative_to(runtime_root)}: not UTF-8")
            continue
        for raw_target in MARKDOWN_LINK.findall(text):
            target, error = _target_path(source, raw_target, runtime_root)
            display = raw_target.strip()
            if error:
                findings.append(f"{source.relative_to(runtime_root)}: {display}: {error}")
                continue
            if target is not None and not target.exists():
                findings.append(f"{source.relative_to(runtime_root)}: broken local reference: {display}")
    return findings


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    runtime = Path(args[0]) if args else DEFAULT_RUNTIME
    findings = validate_runtime_references(runtime)
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    print("SKILL REFERENCES: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

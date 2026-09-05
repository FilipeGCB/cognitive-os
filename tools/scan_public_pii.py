#!/usr/bin/env python3
"""Bounded PII/public-surface scanner for Cognitive OS.

This complements secret scanning. It is intentionally conservative and scans
public product/documentation surfaces for common personal-data patterns that
should not appear in a generic public distribution.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAN_ROOTS = [
    ROOT / "skills",
    ROOT / "adapters",
    ROOT / "bootstrap",
    ROOT / "renderers",
    ROOT / "examples",
    ROOT / "distribution",
    ROOT / "docs" / "capabilities",
    ROOT / "docs" / "releases",
    ROOT / "docs" / "architecture",
    ROOT / "docs" / "baselines",
    ROOT / "docs" / "evidence",
    ROOT / "docs" / "migration",
    ROOT / "telemetry",
]
SCAN_FILES = [
    ROOT / "README.md",
    ROOT / "README.pt-BR.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs" / "HOST_MATRIX_V1_5.md",
    ROOT / "docs" / "reproducibility.md",
    ROOT / "docs" / "telemetry-privacy-notice.md",
    ROOT / "docs" / "telemetry-collector-contract.md",
]

PATTERNS = {
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "Brazilian CPF-like number": re.compile(r"(?<!\d)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\d)"),
    # Hex digests are public integrity metadata, not phone numbers.  Keeping
    # hex boundaries here prevents a digest beginning with decimal characters
    # from producing a false positive while retaining the numeric boundaries
    # that reject embedded digit sequences.
    "Brazilian phone-like number": re.compile(
        r"(?<![0-9A-Fa-f])(?:\+?55\s*)?\(?\d{2}\)?\s*9?\d{4}[-\s]?\d{4}(?![0-9A-Fa-f])"
    ),
    "home directory path": re.compile(r"/(?:home|Users)/[^/\s]+/"),
}

ALLOWED_EMAILS: set[str] = set()


def iter_files():
    seen: set[Path] = set()
    for path in SCAN_FILES:
        if path.is_file():
            seen.add(path)
            yield path
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".py", ".html", ".css", ".txt"}:
                if path not in seen:
                    seen.add(path)
                    yield path


def scan() -> list[str]:
    findings: list[str] = []
    for path in iter_files():
        text = path.read_text(encoding="utf-8")
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                value = match.group(0)
                if label == "email address" and value in ALLOWED_EMAILS:
                    continue
                findings.append(f"{path.relative_to(ROOT)}: {label}: {value}")
    return findings


def main() -> int:
    findings = scan()
    if findings:
        print("PUBLIC PII SCAN: FAIL", file=sys.stderr)
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    print("PUBLIC PII SCAN: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

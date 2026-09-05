#!/usr/bin/env python3
"""Deterministic public-package guard.

This is not a complete secret/PII scanner. It catches known private-runtime
markers, obvious credential material and package-integrity failures before a
release candidate can be described as clean.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "skills" / "cognitive-os"

FORBIDDEN_TEXT = [
    "private-vault-repository-marker",
    "/home/",
    "storage_state.json\"",  # catches accidental JSON/auth-file embedding, not documentation prose
    "-----BEGIN PRIVATE KEY-----",
    "-----BEGIN RSA PRIVATE KEY-----",
]

SECRET_PATTERNS = [
    re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
]

PUBLIC_SCAN_ROOTS = [
    ROOT / "skills",
    ROOT / "adapters",
    ROOT / "bootstrap",
    ROOT / "renderers",
    ROOT / "examples",
    ROOT / "docs" / "capabilities",
    ROOT / "docs" / "architecture",
    ROOT / "docs" / "baselines",
    ROOT / "docs" / "evidence",
    ROOT / "docs" / "migration",
    ROOT / "docs" / "telemetry-privacy-notice.md",
    ROOT / "docs" / "telemetry-collector-contract.md",
    ROOT / "distribution",
    ROOT / "telemetry",
]


def scan_text(text: str) -> list[str]:
    findings: list[str] = []
    for token in FORBIDDEN_TEXT:
        if token in text:
            findings.append(f"forbidden marker: {token}")
    if "Vivo" in text and "skills/cognitive-os" in text:
        findings.append("private corporate marker: Vivo")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(f"possible secret pattern: {pattern.pattern}")
    return findings


def iter_public_files():
    for root in PUBLIC_SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".py", ".html", ".css", ".txt"}:
                yield path


def validate() -> list[str]:
    findings: list[str] = []
    required = [
        RUNTIME / "SKILL.md",
        RUNTIME / "VERSION",
        RUNTIME / "references" / "routing.md",
        RUNTIME / "references" / "output.md",
        RUNTIME / "schemas" / "decision-pack.md",
        RUNTIME / "schemas" / "cognitive-run-record.schema.json",
        RUNTIME / "schemas" / "capability-decision-record.schema.json",
        RUNTIME / "schemas" / "cognitive-usage-trace.schema.json",
        RUNTIME / "policies" / "installation-consent.md",
        RUNTIME / "policies" / "telemetry-privacy.md",
        ROOT / "distribution" / "manifest.schema.json",
        ROOT / "telemetry" / "defaults.json",
        ROOT / "telemetry" / "defaults.schema.json",
        ROOT / "docs" / "telemetry-privacy-notice.md",
    ]
    for path in required:
        if not path.is_file():
            findings.append(f"missing runtime file: {path.relative_to(ROOT)}")

    for path in iter_public_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"non-UTF8 public text file: {path.relative_to(ROOT)}")
            continue
        for finding in scan_text(text):
            findings.append(f"{path.relative_to(ROOT)}: {finding}")
    return findings


def main() -> int:
    findings = validate()
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    print("PUBLIC PACKAGE GUARD: PASS")
    print("Note: this deterministic guard does not replace a stronger secret/PII scan before release.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

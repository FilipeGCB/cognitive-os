#!/usr/bin/env python3
"""Check that development package metadata names one coherent V1.5 version."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VersionSyncError(ValueError):
    pass


def validate_version_sync(root: Path = ROOT, expected: str = "1.5.0-dev") -> list[str]:
    errors: list[str] = []
    version_path = root / "skills/cognitive-os/VERSION"
    if not version_path.is_file() or version_path.read_text(encoding="utf-8").strip() != expected:
        errors.append(f"VERSION must be {expected}")
    json_expectations = {
        "gemini-extension.json": ("version",),
        ".claude-plugin/marketplace.json": ("version",),
    }
    for relative, keys in json_expectations.items():
        path = root / relative
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: invalid JSON ({exc})")
            continue
        for key in keys:
            if value.get(key) != expected:
                errors.append(f"{relative}: {key} must be {expected}")
    text_files = [
        "README.md", "README.pt-BR.md", "CHANGELOG.md", "CONTRIBUTING.md",
        "distribution/agent-skills/README.md", "distribution/openai/README.md",
        "distribution/claude/README.md", "distribution/gemini/README.md",
    ]
    for relative in text_files:
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"missing versioned surface: {relative}")
            continue
        if expected not in text:
            errors.append(f"{relative}: missing {expected}")
    registry = root / "adapters/registry.json"
    if registry.is_file():
        try:
            if json.loads(registry.read_text(encoding="utf-8")).get("schema_version") != "cognitive-os-adapter-registry-v1.5":
                errors.append("adapters/registry.json: stale schema version")
        except (OSError, json.JSONDecodeError):
            errors.append("adapters/registry.json: invalid JSON")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", default="1.5.0-dev")
    args = parser.parse_args(argv)
    errors = validate_version_sync(expected=args.expected)
    if errors:
        for error in errors:
            print(f"VERSION SYNC: INVALID — {error}", file=sys.stderr)
        return 1
    print(f"VERSION SYNC: PASS — {args.expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

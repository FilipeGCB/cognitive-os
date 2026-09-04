#!/usr/bin/env python3
"""Validate Cognitive OS behavior-case JSON manifests using stdlib only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_KEYS = {"id", "prompt", "tags", "must", "must_not"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # deterministic CLI validation boundary
        return [f"invalid JSON: {exc}"]

    if not isinstance(data, list) or not data:
        return ["manifest must be a non-empty JSON array"]

    seen: set[str] = set()
    for index, case in enumerate(data):
        label = f"case[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label}: must be an object")
            continue
        missing = REQUIRED_KEYS - set(case)
        if missing:
            errors.append(f"{label}: missing {sorted(missing)}")
            continue
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{label}: id must be a non-empty string")
        elif case_id in seen:
            errors.append(f"{label}: duplicate id {case_id}")
        else:
            seen.add(case_id)
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            errors.append(f"{label}: prompt must be non-empty")
        for key in ("tags", "must", "must_not"):
            value = case[key]
            if not isinstance(value, list) or not value or not all(isinstance(x, str) and x.strip() for x in value):
                errors.append(f"{label}: {key} must be a non-empty list of non-empty strings")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_cases.py MANIFEST.json", file=sys.stderr)
        return 2
    path = Path(argv[1])
    errors = validate(path)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"VALID: {path} ({len(json.loads(path.read_text(encoding='utf-8')))} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

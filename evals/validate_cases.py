#!/usr/bin/env python3
"""Validate Cognitive OS behavior-case JSON manifests using stdlib only."""

from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

REQUIRED_KEYS = {"id", "prompt", "tags", "must", "must_not"}
OPTIONAL_KEYS = {"critical"}
V15_FAMILIES = {"CD", "RS", "GS", "SI", "TL", "PR", "HP", "DS", "MC", "RC"}


def validate(path: Path, *, require_v1_5_family: bool = False) -> list[str]:
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
        unknown = set(case) - (REQUIRED_KEYS | OPTIONAL_KEYS)
        if unknown:
            errors.append(f"{label}: unknown keys {sorted(unknown)}")
        if "critical" in case and not isinstance(case["critical"], bool):
            errors.append(f"{label}: critical must be boolean")
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
        if isinstance(case.get("tags"), list) and "v1.5" in case["tags"] and len(case["tags"]) < 2:
            errors.append(f"{label}: v1.5 cases must identify a family tag")
        if require_v1_5_family:
            families = set(case.get("tags", [])) & V15_FAMILIES
            if "v1.5" not in case.get("tags", []) or len(families) != 1:
                errors.append(f"{label}: must contain exactly one V1.5 family tag from {sorted(V15_FAMILIES)}")
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--family-v1-5", action="store_true")
    args = parser.parse_args(argv[1:])
    path = args.manifest
    errors = validate(path, require_v1_5_family=args.family_v1_5)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"VALID: {path} ({len(json.loads(path.read_text(encoding='utf-8')))} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

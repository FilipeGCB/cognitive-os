#!/usr/bin/env python3
"""Validate Cognitive OS V1.5 machine contracts without third-party packages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bootstrap"))

from cognitive_os_contracts import (  # noqa: E402
    ContractError,
    validate_capability_decision,
    validate_forensic_manifest,
    validate_run_record,
)

SCHEMA_DIR = ROOT / "skills" / "cognitive-os" / "schemas"
VALIDATORS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "cognitive-run-record": validate_run_record,
    "capability-decision-record": validate_capability_decision,
    "forensic-diagnostic-manifest": validate_forensic_manifest,
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{path} must contain a JSON object")
    return value


def validate_schema_documents() -> list[str]:
    errors: list[str] = []
    expected = {
        "cognitive-run-record.schema.json",
        "capability-decision-record.schema.json",
        "forensic-diagnostic-manifest.schema.json",
        "release-evidence-record.schema.json",
    }
    for filename in sorted(expected):
        path = SCHEMA_DIR / filename
        if not path.is_file():
            errors.append(f"missing schema: {path}")
            continue
        try:
            schema = load_json(path)
        except ContractError as exc:
            errors.append(str(exc))
            continue
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{filename}: unsupported JSON Schema dialect")
        if schema.get("type") != "object":
            errors.append(f"{filename}: root type must be object")
        if schema.get("additionalProperties") is not False:
            errors.append(f"{filename}: root additionalProperties must be false")
        if not isinstance(schema.get("required"), list) or not schema["required"]:
            errors.append(f"{filename}: required must be a non-empty array")
    return errors


def validator_for(path: Path) -> Callable[[dict[str, Any]], Any]:
    name = path.name.removesuffix(".json")
    for prefix, validator in VALIDATORS.items():
        if name == prefix or name.startswith(prefix + "."):
            return validator
    raise ContractError(f"no deterministic validator registered for {path.name}")


def validate_path(path: Path) -> None:
    validator_for(path)(load_json(path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--check-schemas", action="store_true")
    args = parser.parse_args(argv)

    errors = validate_schema_documents() if args.check_schemas or not args.paths else []
    for path in args.paths:
        try:
            validate_path(path)
            print(f"VALID: {path}")
        except (ContractError, OSError) as exc:
            errors.append(str(exc))
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1
    if args.check_schemas or not args.paths:
        print("MACHINE CONTRACT SCHEMAS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

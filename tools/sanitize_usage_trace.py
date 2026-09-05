#!/usr/bin/env python3
"""Validate a local trace and print only its privacy-preserving projection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from telemetry.flight_recorder import (  # noqa: E402
    TraceError,
    build_shared_payload,
    sanitize_usage_trace,
    validate_shared_payload,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--shared", action="store_true", help="validate an already projected shared payload")
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.trace.read_text(encoding="utf-8"))
        output = validate_shared_payload(value) if args.shared else build_shared_payload(sanitize_usage_trace(value))
    except (OSError, json.JSONDecodeError, TraceError, TypeError, ValueError) as exc:
        print(f"USAGE TRACE: INVALID — {exc}", file=sys.stderr)
        return 1
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

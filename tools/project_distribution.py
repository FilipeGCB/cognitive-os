#!/usr/bin/env python3
"""Project each declared target into an install-like artifact directory.

This is a deterministic local packaging smoke helper. It does not call a host
installer or publish anything; it materializes the assets declared by the
distribution manifests so validation can target the artifact rather than the
canonical source tree.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validate_distribution import DistributionError, load_manifest  # noqa: E402


def _copy(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination)
    elif source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    else:
        raise DistributionError(f"declared asset does not exist: {source}")


def project_manifest(manifest: Mapping[str, object], destination: Path, *, source_root: Path = ROOT) -> Path:
    """Create a fresh flattened skill artifact for one target."""

    if destination.exists():
        raise DistributionError(f"refusing to overwrite existing artifact: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    _copy(source_root / "skills/cognitive-os", destination)
    if manifest["target"] == "gemini":
        _copy(source_root / "gemini-extension.json", destination / "gemini-extension.json")
    if manifest["target"] == "claude":
        _copy(source_root / ".claude-plugin/marketplace.json", destination / ".claude-plugin/marketplace.json")
    metadata = {
        "target": manifest["target"],
        "package_version": manifest["package_version"],
        "source_commit": manifest["source_commit"],
    }
    (destination / "distribution-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target", action="append", choices=("agent-skills", "openai", "claude", "gemini"))
    args = parser.parse_args(argv)
    targets = args.target or [path.stem for path in sorted((ROOT / "distribution/manifests").glob("*.json"))]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    for target in targets:
        manifest_path = ROOT / "distribution/manifests" / f"{target}.json"
        try:
            manifest = load_manifest(manifest_path)
            output = project_manifest(manifest, args.output_dir / target)
            print(f"PROJECTED: {target} -> {output}")
        except (DistributionError, OSError, json.JSONDecodeError) as exc:
            errors.append(f"{target}: {exc}")
    if errors:
        for error in errors:
            print(f"DISTRIBUTION PROJECTION: INVALID — {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

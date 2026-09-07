#!/usr/bin/env python3
"""Validate V1.5 distribution declarations and copied installed artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "distribution/manifests"
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")


class DistributionError(ValueError):
    pass


ALLOWED_STATES = {"COMPLETE", "PARTIAL", "UNAVAILABLE", "UNKNOWN"}
REQUIRED = {
    "schema_version", "target", "source_commit", "package_version", "included_assets",
    "projected_assets", "omitted_assets", "feature_availability", "schema_enforcement",
}


def _safe_relative(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts or "\\" in value:
        raise DistributionError(f"{name} is not a repository/package-relative path")
    return value


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DistributionError(f"{path}: invalid JSON ({exc})") from exc
    if not isinstance(value, dict):
        raise DistributionError(f"{path}: manifest must be an object")
    missing = REQUIRED - set(value)
    unknown = set(value) - (REQUIRED | {"notes"})
    if missing or unknown:
        raise DistributionError(f"{path}: missing={sorted(missing)} unknown={sorted(unknown)}")
    if value["schema_version"] != "cognitive-os-distribution-manifest-v1.5":
        raise DistributionError(f"{path}: unsupported schema version")
    if value["target"] not in {"agent-skills", "openai", "claude", "gemini"}:
        raise DistributionError(f"{path}: unsupported target")
    source = value["source_commit"]
    if source != "UNRELEASED_WORKTREE" and (not isinstance(source, str) or not re.fullmatch(r"[0-9a-f]{40}", source)):
        raise DistributionError(f"{path}: source_commit must be a full SHA or UNRELEASED_WORKTREE")
    if not isinstance(value["package_version"], str) or not VERSION_RE.fullmatch(value["package_version"]):
        raise DistributionError(f"{path}: invalid package_version")
    for field in ("included_assets", "projected_assets", "omitted_assets"):
        if not isinstance(value[field], list) or any(not isinstance(item, str) or not item for item in value[field]):
            raise DistributionError(f"{path}: {field} must be a list of strings")
        for index, item in enumerate(value[field]):
            _safe_relative(item.rstrip("/"), f"{path}:{field}[{index}]")
    features = value["feature_availability"]
    if not isinstance(features, dict) or not features or any(state not in ALLOWED_STATES for state in features.values()):
        raise DistributionError(f"{path}: feature_availability has invalid state")
    if value["schema_enforcement"] not in {"COMPLETE", "PARTIAL", "UNAVAILABLE"}:
        raise DistributionError(f"{path}: invalid schema_enforcement")
    return value


def validate_distribution_manifest(path: Path, *, source_root: Path = ROOT, expected_source_commit: str | None = None) -> dict[str, Any]:
    manifest = load_manifest(path)
    version = (source_root / "skills/cognitive-os/VERSION").read_text(encoding="utf-8").strip()
    if manifest["package_version"] != version:
        raise DistributionError(f"{path}: package_version does not match source VERSION")
    if expected_source_commit and manifest["source_commit"] != expected_source_commit:
        raise DistributionError(f"{path}: source_commit is not bound to expected candidate")
    for field in ("included_assets",):
        for value in manifest[field]:
            target = source_root / value
            if not target.exists():
                raise DistributionError(f"{path}: declared included asset does not exist: {value}")
    return manifest


def _asset_exists(root: Path, value: str) -> bool:
    clean = value.rstrip("/")
    return (root / clean).exists()


def validate_installed_artifact(path: Path, manifest: Mapping[str, Any]) -> list[str]:
    """Smoke-test the actual copied package, not the canonical source tree."""

    errors: list[str] = []
    if not path.is_dir():
        return [f"installed artifact is not a directory: {path}"]
    version_path = path / "VERSION"
    if not version_path.is_file():
        errors.append("installed artifact is missing VERSION")
    elif version_path.read_text(encoding="utf-8").strip() != manifest["package_version"]:
        errors.append("installed artifact VERSION does not match manifest")
    for asset in manifest["projected_assets"]:
        if not _asset_exists(path, asset):
            errors.append(f"projected asset missing from installed artifact: {asset}")
    # Resolve only ordinary relative Markdown links. External URLs and anchors
    # are not package files and are intentionally outside this smoke test.
    link_re = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)")
    for markdown in path.rglob("*.md"):
        try:
            text = markdown.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read installed artifact file {markdown}: {exc}")
            continue
        for raw_target in link_re.findall(text):
            target = raw_target.strip()
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (markdown.parent / target).resolve()
            try:
                resolved.relative_to(path.resolve())
            except ValueError:
                errors.append(f"link escapes installed artifact: {markdown.relative_to(path)} -> {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken installed-artifact link: {markdown.relative_to(path)} -> {target}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", action="append", default=[], metavar="TARGET=PATH")
    parser.add_argument("--source-commit")
    args = parser.parse_args(argv)
    errors: list[str] = []
    manifests: dict[str, dict[str, Any]] = {}
    for path in sorted(MANIFEST_DIR.glob("*.json")):
        try:
            manifest = validate_distribution_manifest(path, expected_source_commit=args.source_commit)
            manifests[manifest["target"]] = manifest
            print(f"VALID: {path}")
        except (DistributionError, OSError) as exc:
            errors.append(str(exc))
    for entry in args.artifact:
        if "=" not in entry:
            errors.append(f"--artifact requires TARGET=PATH: {entry}")
            continue
        target, raw_path = entry.split("=", 1)
        manifest = manifests.get(target)
        if manifest is None:
            errors.append(f"no manifest for artifact target: {target}")
            continue
        errors.extend(f"{target}: {error}" for error in validate_installed_artifact(Path(raw_path), manifest))
    if errors:
        for error in errors:
            print(f"DISTRIBUTION: INVALID — {error}", file=sys.stderr)
        return 1
    print(f"DISTRIBUTION: PASS — {len(manifests)} targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

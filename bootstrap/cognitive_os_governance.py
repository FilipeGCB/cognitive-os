"""Host-neutral self-improvement and persistent-side-effect contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping, Sequence


_RUN_ID = re.compile(r"^CRR-[0-9]{8}-[0-9]{6}-[A-Za-z0-9]{4,16}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class MethodologySnapshot:
    run_id: str
    skill_version: str
    skill_hash: str
    reference_hashes: Mapping[str, str]
    policy_hashes: Mapping[str, str]

    def __post_init__(self) -> None:
        if not _RUN_ID.fullmatch(self.run_id):
            raise ValueError("methodology snapshot requires a host-shaped run id")
        if not self.skill_version or not _SHA256.fullmatch(self.skill_hash):
            raise ValueError("methodology snapshot requires version and SHA-256")
        for name, values in (("reference", self.reference_hashes), ("policy", self.policy_hashes)):
            for path, digest in values.items():
                if not path or Path(path).is_absolute() or ".." in Path(path).parts or not _SHA256.fullmatch(digest):
                    raise ValueError(f"invalid {name} hash entry: {path}")


@dataclass(frozen=True)
class PatchValidationResult:
    status: str
    validation: str
    activate_now: bool
    missing_references: tuple[str, ...] = ()
    reason: str = ""


def validate_staged_patch(
    snapshot: MethodologySnapshot,
    patch: Mapping[str, object],
    root: Path,
) -> PatchValidationResult:
    """Validate a staged patch; activation is always deferred past the run."""

    missing: list[str] = []
    for field in ("references", "dependencies"):
        values = patch.get(field, ())
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            return PatchValidationResult("BLOCKED", "FAIL", False, reason=f"patch.{field} must be a list")
        for value in values:
            if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
                missing.append(str(value))
                continue
            if not (root / value).is_file():
                missing.append(value)
    if patch.get("frontmatter_valid") is not True:
        return PatchValidationResult("BLOCKED", "FAIL", False, tuple(missing), "frontmatter/format validation failed")
    if missing:
        return PatchValidationResult("BLOCKED", "FAIL", False, tuple(sorted(set(missing))), "referenced files or dependencies are missing")
    return PatchValidationResult(
        "STAGED",
        "PASS",
        False,
        reason=f"methodology pinned to {snapshot.skill_version} for run {snapshot.run_id}; activation deferred",
    )


@dataclass(frozen=True)
class SideEffect:
    type: str
    target: str
    before_version_or_hash: str
    after_version_or_hash: str


_EVENT_TYPE = {
    "package_installed": "PACKAGE_INSTALLED",
    "mcp_installed": "MCP_INSTALLED",
    "connection_created": "CONNECTION_CREATED",
    "credential_state_changed": "CREDENTIAL_STATE_CHANGED",
    "skill_mutated": "SKILL_MUTATED",
    "reference_mutated": "REFERENCE_MUTATED",
    "policy_mutated": "POLICY_MUTATED",
    "config_changed": "CONFIG_CHANGED",
    "file_created": "FILE_CREATED",
    "file_modified": "FILE_MODIFIED",
    "other_persistent_side_effect": "OTHER_PERSISTENT_SIDE_EFFECT",
}


def _path_effect_type(path: str, created: bool) -> str:
    normalized = path.replace("\\", "/")
    if normalized.endswith("/SKILL.md") or normalized == "skills/cognitive-os/SKILL.md":
        return "SKILL_MUTATED"
    if "/references/" in normalized:
        return "REFERENCE_MUTATED"
    if "/policies/" in normalized:
        return "POLICY_MUTATED"
    if normalized.startswith("config/") or "/config/" in normalized or normalized.endswith(".config"):
        return "CONFIG_CHANGED"
    return "FILE_CREATED" if created else "FILE_MODIFIED"


def detect_persistent_side_effects(
    before: Mapping[str, str],
    after: Mapping[str, str],
    events: Sequence[Mapping[str, object]],
) -> tuple[SideEffect, ...]:
    """Use scoped before/after snapshots plus events; no single tool is required."""

    effects: list[SideEffect] = []
    for path in sorted(set(before) | set(after)):
        old = before.get(path, "ABSENT")
        new = after.get(path, "ABSENT")
        if old == new:
            continue
        effects.append(SideEffect(_path_effect_type(path, path not in before), path, old, new))
    for event in events:
        event_name = str(event.get("event") or "").lower()
        effect_type = _EVENT_TYPE.get(event_name)
        target = str(event.get("target") or "unknown")
        if effect_type:
            effects.append(SideEffect(effect_type, target, str(event.get("before") or "ABSENT"), str(event.get("after") or "OBSERVED")))
    return tuple(effects)

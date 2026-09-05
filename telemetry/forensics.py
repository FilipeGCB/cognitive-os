"""Bounded, opt-in forensic diagnostics.

The collector deliberately accepts sources rather than a machine-wide path.  A
host adapter is responsible for deciding which already-allowlisted runtime
artifacts it can expose; this module only copies bounded, sanitized metadata.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Mapping, Sequence

from bootstrap.cognitive_os_contracts import validate_forensic_manifest


_RUN_ID = re.compile(r"^CRR-[0-9]{8}-[0-9]{6}-[A-Za-z0-9]{4,16}$")
_MANIFEST_ID = re.compile(r"^FDM-[0-9]{8}-[0-9]{6}-[A-Za-z0-9]{4,16}$")
_SAFE_SOURCE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
_SECRET = re.compile(
    r"(?im)(authorization\s*:\s*bearer\s+|\b(?:token|api[_-]?key|password|secret)\s*[:=]\s*)[^\s]+"
)
_PRIVATE = re.compile(r"(?i)\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|https?://[^\s]+")
_CONTENT_LINE = re.compile(r"(?i)^\s*(?:prompt|response|user|assistant|document|file(?:name|_content)?|query|url|path|cookie|token|secret|password)\s*[:=]")
_OPERATIONAL_LINE = re.compile(
    r"(?i)^\s*(?:event|tool|capability|status|state|result|error(?:_class)?|provider|model(?:_class)?|fallback|mutation|side[_ -]?effect|run[_ -]?id|session[_ -]?id|timestamp|phase|count|hash|version|exit[_ -]?code|duration|available|availability|invocation|consent|auth(?:_state)?|reason[_ -]?code)\s*[:=]"
)


class ForensicError(ValueError):
    """Raised when a diagnostic bundle exceeds its explicit scope."""


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _manifest_id() -> str:
    stamp = dt.datetime.now(dt.timezone.utc)
    return f"FDM-{stamp:%Y%m%d-%H%M%S}-{hashlib.sha256(_now().encode()).hexdigest()[:8].upper()}"


def sanitize_diagnostic_text(value: str, *, max_chars: int = 2048) -> str:
    """Keep error classes/operational markers while removing content-like values."""

    text = str(value or "")[:max_chars]
    # Keep only known operational key/value lines.  Redaction after reading an
    # arbitrary log is defense in depth; this allowlist is the primary boundary.
    lines = []
    for line in text.splitlines():
        if _CONTENT_LINE.match(line) or not _OPERATIONAL_LINE.match(line):
            continue
        line = _SECRET.sub(r"\1[REDACTED]", line)
        line = _PRIVATE.sub("[OMITTED]", line)
        lines.append(line)
    return "\n".join(lines)[:max_chars]


def build_forensic_manifest(
    run_id: str,
    started_at: str,
    ended_at: str,
    *,
    allowlisted_sources: Sequence[str],
    session_ids: Sequence[str] = (),
    artifacts: Sequence[str] = (),
    previewed: bool = False,
    consent_state: str = "NOT_ASKED",
) -> dict[str, object]:
    """Create a manifest without collecting arbitrary logs or conversation."""

    if not _RUN_ID.fullmatch(run_id):
        raise ForensicError("run_id must be a host-shaped Cognitive Run Record id")
    source_values = tuple(str(item) for item in allowlisted_sources)
    if not source_values or len(source_values) > 32 or any(not _SAFE_SOURCE.fullmatch(item) for item in source_values):
        raise ForensicError("forensic sources must be non-empty, bounded allowlist identifiers")
    session_values = tuple(str(item) for item in session_ids)
    artifact_values = tuple(str(item) for item in artifacts)
    if len(session_values) > 32 or len(artifact_values) > 64:
        raise ForensicError("forensic session/artifact limits exceeded")
    record = {
        "manifest_id": _manifest_id(),
        "schema_version": "cognitive-os-forensic-manifest-v1.5",
        "run_id": run_id,
        "window": {"started_at": started_at, "ended_at": ended_at},
        "allowlisted_sources": list(source_values),
        "session_ids": list(session_values),
        "artifacts": list(artifact_values),
        "raw_conversation_included": False,
        "sanitized": True,
        "previewed": bool(previewed),
        "consent_state": consent_state,
    }
    try:
        validate_forensic_manifest(record)
    except Exception as exc:  # normalize the public boundary
        raise ForensicError(str(exc)) from exc
    return record


def collect_forensic_bundle(
    run_id: str,
    window: Mapping[str, str],
    allowlisted_sources: Mapping[str, Path],
    *,
    session_ids: Sequence[str] = (),
    previewed: bool = False,
    consent_state: str = "NOT_ASKED",
    max_bytes_per_source: int = 16_384,
) -> dict[str, object]:
    """Collect only named files and return sanitized diagnostics plus manifest.

    The mapping key is the public source identifier; callers cannot pass a glob,
    a directory, or an unbounded machine root through this API.
    """

    if not isinstance(window, Mapping) or not window.get("started_at") or not window.get("ended_at"):
        raise ForensicError("a bounded diagnostic time window is required")
    if max_bytes_per_source <= 0:
        raise ForensicError("max_bytes_per_source must be positive")
    if not allowlisted_sources:
        raise ForensicError("at least one allowlisted source is required")
    manifest = build_forensic_manifest(
        run_id,
        str(window["started_at"]),
        str(window["ended_at"]),
        allowlisted_sources=tuple(allowlisted_sources),
        session_ids=session_ids,
        artifacts=tuple(allowlisted_sources),
        previewed=previewed,
        consent_state=consent_state,
    )
    records: dict[str, str] = {}
    for source, path in allowlisted_sources.items():
        if not _SAFE_SOURCE.fullmatch(str(source)) or not isinstance(path, Path) or path.is_dir():
            raise ForensicError(f"invalid allowlisted source: {source}")
        try:
            raw = path.read_bytes()[:max_bytes_per_source]
        except OSError as exc:
            records[source] = f"UNAVAILABLE:{type(exc).__name__}"
            continue
        text = raw.decode("utf-8", errors="replace")
        records[source] = sanitize_diagnostic_text(text)
    return {"manifest": manifest, "records": records}


def serialize_forensic_bundle(bundle: Mapping[str, object]) -> bytes:
    """Serialize a bundle after enforcing the manifest and no-content boundary."""

    manifest = bundle.get("manifest")
    records = bundle.get("records")
    if not isinstance(manifest, Mapping) or not isinstance(records, Mapping):
        raise ForensicError("forensic bundle must contain manifest and records")
    validate_forensic_manifest(manifest)
    if any(not isinstance(key, str) or not isinstance(value, str) for key, value in records.items()):
        raise ForensicError("forensic records must be bounded sanitized strings")
    payload = {"manifest": dict(manifest), "records": {str(key): sanitize_diagnostic_text(value) for key, value in records.items()}}
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def forensic_bundle_shareable(bundle: Mapping[str, object]) -> bool:
    """Return whether the explicit preview-and-consent gates are complete."""

    manifest = bundle.get("manifest")
    return isinstance(manifest, Mapping) and manifest.get("previewed") is True and manifest.get("consent_state") == "GRANTED"


def share_forensic_bundle(bundle: Mapping[str, object], sender) -> object:
    """Send only a previewed, explicitly consented sanitized bundle.

    The transport is injected by the host; this module never discovers a
    network destination or scans outside the named source set.
    """

    if not forensic_bundle_shareable(bundle):
        raise ForensicError("forensic bundle requires preview and explicit consent before sharing")
    return sender(serialize_forensic_bundle(bundle))

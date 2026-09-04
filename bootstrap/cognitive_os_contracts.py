"""Machine-verifiable Cognitive OS V1.5 contracts.

The public skill remains host-neutral and mostly textual, but records that affect
trust are validated here with deterministic rules.  This module deliberately
uses only the standard library so an installed host does not need a dependency
manager merely to validate a run record.
"""

from __future__ import annotations

import datetime as _dt
import re
from typing import Any, Iterable, Mapping


class ContractError(ValueError):
    """Raised when a machine contract is missing, malformed or contradictory."""


AVAILABILITY = frozenset({"AVAILABLE", "UNAVAILABLE", "UNKNOWN"})
AUTH_STATE = frozenset(
    {"NOT_REQUIRED", "REQUIRED_NOT_AUTHENTICATED", "AUTHENTICATED", "UNKNOWN"}
)
RUN_CONSENT_STATE = frozenset(
    {"NOT_REQUIRED", "NOT_ASKED", "NOT_GRANTED", "DECLINED", "GRANTED", "REVOKED"}
)
INVOCATION = frozenset({"CALLED", "NOT_CALLED"})
RESULT = frozenset(
    {
        "SUCCESS",
        "PARTIAL",
        "TRUNCATED",
        "RATE_LIMITED",
        "UNAVAILABLE",
        "BLOCKED",
        "FAILED",
        "NOT_APPLICABLE",
    }
)
PROVENANCE = frozenset(
    {
        "HOST_OBSERVED",
        "TOOL_OBSERVED",
        "REPOSITORY_OBSERVED",
        "USER_SUPPLIED",
        "MODEL_SYNTHESIZED",
        "UNKNOWN",
    }
)
DISCOVERY_CLASS = frozenset(
    {
        "EXISTING_CAPABILITY",
        "LOCAL_SKILL_DISCOVERY",
        "LOCAL_TOOL_DISCOVERY",
        "LOCAL_CONNECTOR_DISCOVERY",
        "EXTERNAL_SKILL_DISCOVERY",
        "EXTERNAL_MCP_DISCOVERY",
        "MANUAL_FALLBACK",
    }
)
ADOPTION_STATE = frozenset(
    {
        "DISCOVERED",
        "INSPECTED",
        "REJECTED",
        "TEST_APPROVED",
        "PERSISTENT_ADOPTION_PENDING_CONSENT",
        "APPROVED",
        "QUARANTINED",
        "UNAVAILABLE",
        "BLOCKED",
    }
)
FLOW_COVERAGE = frozenset({"COMPLETE", "PARTIAL", "BLOCKED"})
EXECUTION_INTEGRITY = frozenset({"COMPLETE", "PARTIAL", "FAILED", "BLOCKED"})
RUN_STATUS = frozenset({"COMPLETE", "PARTIAL", "FAILED", "BLOCKED"})
DECISION_STATE = frozenset(
    {
        "READY_TO_DECIDE",
        "DECIDED",
        "TEST_REQUIRED",
        "MORE_EVIDENCE_REQUIRED",
        "MORE_RESEARCH_REQUIRED",
        "RECOMMENDATION_ONLY",
        "BLOCKED",
        "NO_ACTION_RECOMMENDED",
        "READY",
    }
)
DEPTH = frozenset({"fast", "normal", "deep", "board360"})
TELEMETRY_MODE = frozenset(
    {"OFF", "LOCAL_DIAGNOSTICS", "SHARE_PRIVACY_PRESERVING_DIAGNOSTICS"}
)
TELEMETRY_STATE = frozenset(
    {"NOT_CONFIGURED", "AVAILABLE", "UNAVAILABLE", "DECLINED", "REVOKED", "LOCAL_ONLY", "SHARE_APPROVED"}
)

_EXECUTION_RESULT_STATE = {
    "SUCCESS": "EXECUTED",
    "PARTIAL": "CALLED_PARTIAL",
    "TRUNCATED": "CALLED_TRUNCATED",
    "RATE_LIMITED": "CALLED_RATE_LIMITED",
    "UNAVAILABLE": "CALLED_UNAVAILABLE",
    "BLOCKED": "CALLED_BLOCKED",
    "FAILED": "CALLED_FAILED",
}

_RUN_ID = re.compile(r"^CRR-[0-9]{8}-[0-9]{6}-[A-Za-z0-9]{4,16}$")
_CAPABILITY_ID = re.compile(r"^CAP-[0-9]{8}-[A-Za-z0-9]{4,16}$")
_EVIDENCE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9+._:/#?=&@%~,'()\-]{1,511}$")
_SAFE_TEXT = re.compile(r"^[^\r\n\x00]{1,512}$")


def _enum(name: str, value: Any, allowed: Iterable[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ContractError(f"{name} must be one of {sorted(allowed)}")
    return value


def _keys(record: Mapping[str, Any], *, required: set[str], allowed: set[str], name: str) -> None:
    if not isinstance(record, Mapping):
        raise ContractError(f"{name} must be an object")
    missing = sorted(required - set(record))
    if missing:
        raise ContractError(f"{name} missing required fields: {', '.join(missing)}")
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise ContractError(f"{name} contains unknown fields: {', '.join(unknown)}")


def _timestamp(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or value.endswith("Z") is False and "+" not in value and "-" not in value[10:]:
        raise ContractError(f"{name} must be an ISO-8601 timestamp with timezone")
    try:
        parsed = _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{name} must be an ISO-8601 timestamp with timezone") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{name} must include timezone")
    return value


def _safe_text(value: Any, name: str, max_length: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value) > max_length or not _SAFE_TEXT.fullmatch(value):
        raise ContractError(f"{name} must be bounded text without newlines")
    return value


def validate_evidence_ref(value: Any) -> bool:
    """Validate a bounded reference, never an inline evidence narrative."""

    if not isinstance(value, str) or not _EVIDENCE_REF.fullmatch(value):
        raise ContractError("evidence ref must be a bounded non-free-text reference")
    return True


def derive_execution_state(
    availability: str,
    auth_state: str,
    run_consent_state: str,
    invocation: str,
    result: str | None,
    *,
    consent_required: bool = False,
) -> str:
    """Derive an observable state without allowing prose to imply execution."""

    _enum("availability", availability, AVAILABILITY)
    _enum("auth_state", auth_state, AUTH_STATE)
    _enum("run_consent_state", run_consent_state, RUN_CONSENT_STATE)
    _enum("invocation", invocation, INVOCATION)
    if result is not None:
        _enum("result", result, RESULT)

    if consent_required and run_consent_state not in {"GRANTED", "NOT_REQUIRED"} and invocation == "CALLED":
        raise ContractError("a consent-required capability cannot be CALLED without run consent")

    if invocation == "NOT_CALLED":
        if result not in {None, "UNAVAILABLE", "NOT_APPLICABLE"}:
            raise ContractError("NOT_CALLED cannot carry a completed or failed call result")
        if availability == "AVAILABLE":
            return "AVAILABLE_NOT_EXERCISED"
        if availability == "UNAVAILABLE":
            return "UNAVAILABLE"
        return "UNKNOWN"

    if result not in _EXECUTION_RESULT_STATE:
        raise ContractError("CALLED requires a concrete result")
    if result == "SUCCESS":
        if availability != "AVAILABLE":
            raise ContractError("SUCCESS requires runtime availability AVAILABLE")
        if auth_state in {"REQUIRED_NOT_AUTHENTICATED", "UNKNOWN"}:
            raise ContractError("SUCCESS requires observed authentication when authentication is required")
        if consent_required and run_consent_state != "GRANTED":
            raise ContractError("SUCCESS requires explicit run consent")
    return _EXECUTION_RESULT_STATE[result]


def _validate_ref_list(values: Any, name: str, *, required: bool = False) -> list[str]:
    if not isinstance(values, list):
        raise ContractError(f"{name} must be an array")
    if required and not values:
        raise ContractError(f"{name} must contain at least one evidence ref")
    result = []
    for value in values:
        validate_evidence_ref(value)
        result.append(value)
    return result


def _validate_ledger_list(values: Any, name: str) -> None:
    if not isinstance(values, list):
        raise ContractError(f"{name} must be an array")
    for item in values:
        if not isinstance(item, Mapping):
            raise ContractError(f"{name} items must be objects")


def validate_run_record(record: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate the trust-bearing subset of a Cognitive Run Record."""

    required = {
        "id",
        "schema_version",
        "created_at",
        "host",
        "surface",
        "depth",
        "flow_coverage",
        "execution_integrity",
        "run_status",
        "decision_state",
        "provenance",
        "phase_ledger",
        "conditional_branch_ledger",
        "capability_ledger",
        "method_ledger",
        "evidence_ledger",
        "gap_failure_ledger",
        "challenge_ledger",
        "mutation_ledger",
        "persistent_side_effects",
        "research_budget",
        "provider_host_failures",
        "stop",
        "next_proof",
        "telemetry",
    }
    allowed = required | {"mode", "project", "sensitivity", "finished_at", "candidate_sha"}
    _keys(record, required=required, allowed=allowed, name="run_record")
    if not isinstance(record["id"], str) or not _RUN_ID.fullmatch(record["id"]):
        raise ContractError("run_record.id must be a host-shaped CRR id")
    if not isinstance(record["schema_version"], str) or not record["schema_version"].startswith("cognitive-os-run-record-v1."):
        raise ContractError("unsupported run_record schema_version")
    _timestamp(record["created_at"], "run_record.created_at")
    if "finished_at" in record:
        _timestamp(record["finished_at"], "run_record.finished_at")
    _safe_text(record["host"], "run_record.host")
    _safe_text(record["surface"], "run_record.surface")
    _enum("depth", record["depth"], DEPTH)
    _enum("flow_coverage", record["flow_coverage"], FLOW_COVERAGE)
    _enum("execution_integrity", record["execution_integrity"], EXECUTION_INTEGRITY)
    _enum("run_status", record["run_status"], RUN_STATUS)
    _enum("decision_state", record["decision_state"], DECISION_STATE)
    provenance = _enum("provenance", record["provenance"], PROVENANCE)
    if provenance not in {"HOST_OBSERVED", "TOOL_OBSERVED"}:
        raise ContractError("run identity must be host/tool observed, not model synthesized")
    for field in (
        "phase_ledger",
        "conditional_branch_ledger",
        "capability_ledger",
        "method_ledger",
        "evidence_ledger",
        "gap_failure_ledger",
        "challenge_ledger",
        "mutation_ledger",
        "persistent_side_effects",
        "provider_host_failures",
    ):
        _validate_ledger_list(record[field], f"run_record.{field}")
    if not isinstance(record["research_budget"], Mapping):
        raise ContractError("run_record.research_budget must be an object")
    if not isinstance(record["stop"], Mapping):
        raise ContractError("run_record.stop must be an object")
    if not isinstance(record["telemetry"], Mapping):
        raise ContractError("run_record.telemetry must be an object")
    _enum("telemetry.mode", record["telemetry"].get("mode"), TELEMETRY_MODE)
    _enum("telemetry.state", record["telemetry"].get("state"), TELEMETRY_STATE)
    if record["next_proof"] is not None and not isinstance(record["next_proof"], Mapping):
        raise ContractError("run_record.next_proof must be an object or null")
    if "candidate_sha" in record and (
        not isinstance(record["candidate_sha"], str) or not re.fullmatch(r"[0-9a-f]{40}", record["candidate_sha"])
    ):
        raise ContractError("run_record.candidate_sha must be a full lowercase git SHA")
    return record


def validate_capability_decision(record: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate discovery/provenance/consent state for one capability."""

    required = {
        "id",
        "schema_version",
        "capability",
        "discovery_class",
        "source_or_adapter",
        "candidate_provenance",
        "availability",
        "auth_state",
        "run_consent_state",
        "invocation",
        "result",
        "consent_required",
        "adoption_state",
        "evidence_refs",
    }
    allowed = required | {
        "category",
        "need",
        "candidate_id",
        "candidate_source",
        "candidate_version",
        "license",
        "permissions",
        "consent_state",
        "fallback",
        "materiality",
        "notes",
    }
    _keys(record, required=required, allowed=allowed, name="capability_decision")
    if not isinstance(record["id"], str) or not _CAPABILITY_ID.fullmatch(record["id"]):
        raise ContractError("capability_decision.id must be a host-shaped CAP id")
    if not isinstance(record["schema_version"], str) or not record["schema_version"].startswith("cognitive-os-capability-decision-v1."):
        raise ContractError("unsupported capability decision schema_version")
    _safe_text(record["capability"], "capability_decision.capability")
    _enum("discovery_class", record["discovery_class"], DISCOVERY_CLASS)
    _safe_text(record["source_or_adapter"], "capability_decision.source_or_adapter")
    provenance = record["candidate_provenance"]
    _keys(
        provenance,
        required={"source", "provenance_class"},
        allowed={"source", "provenance_class", "repository", "version", "license", "mechanism", "observed_at"},
        name="candidate_provenance",
    )
    _safe_text(provenance["source"], "candidate_provenance.source")
    _enum("candidate_provenance.provenance_class", provenance["provenance_class"], PROVENANCE)
    if provenance["provenance_class"] == "MODEL_SYNTHESIZED":
        raise ContractError("model-synthesized provenance cannot authorize a candidate")
    if "observed_at" in provenance:
        _timestamp(provenance["observed_at"], "candidate_provenance.observed_at")
    _enum("availability", record["availability"], AVAILABILITY)
    _enum("auth_state", record["auth_state"], AUTH_STATE)
    _enum("run_consent_state", record["run_consent_state"], RUN_CONSENT_STATE)
    _enum("invocation", record["invocation"], INVOCATION)
    _enum("result", record["result"], RESULT)
    if not isinstance(record["consent_required"], bool):
        raise ContractError("consent_required must be boolean")
    _enum("adoption_state", record["adoption_state"], ADOPTION_STATE)
    _validate_ref_list(record["evidence_refs"], "capability_decision.evidence_refs", required=record["result"] == "SUCCESS")
    derive_execution_state(
        record["availability"],
        record["auth_state"],
        record["run_consent_state"],
        record["invocation"],
        record["result"],
        consent_required=record["consent_required"],
    )
    if "permissions" in record and not isinstance(record["permissions"], Mapping):
        raise ContractError("permissions must be an object")
    if "notes" in record:
        _safe_text(record["notes"], "capability_decision.notes", 1024)
    return record


def validate_forensic_manifest(record: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate the bounded, opt-in forensic bundle manifest."""

    required = {
        "manifest_id",
        "schema_version",
        "run_id",
        "window",
        "allowlisted_sources",
        "session_ids",
        "artifacts",
        "raw_conversation_included",
        "sanitized",
        "previewed",
        "consent_state",
    }
    _keys(record, required=required, allowed=required, name="forensic_manifest")
    if not isinstance(record["manifest_id"], str) or not record["manifest_id"].startswith("FDM-"):
        raise ContractError("forensic_manifest.manifest_id must be bounded")
    if not isinstance(record["schema_version"], str) or record["schema_version"] != "cognitive-os-forensic-manifest-v1.5":
        raise ContractError("unsupported forensic manifest schema_version")
    if not isinstance(record["run_id"], str) or not _RUN_ID.fullmatch(record["run_id"]):
        raise ContractError("forensic_manifest.run_id must reference a run record")
    if not isinstance(record["window"], Mapping):
        raise ContractError("forensic_manifest.window must be an object")
    _keys(record["window"], required={"started_at", "ended_at"}, allowed={"started_at", "ended_at"}, name="forensic_manifest.window")
    _timestamp(record["window"]["started_at"], "forensic_manifest.window.started_at")
    _timestamp(record["window"]["ended_at"], "forensic_manifest.window.ended_at")
    for field in ("allowlisted_sources", "session_ids", "artifacts"):
        if not isinstance(record[field], list):
            raise ContractError(f"forensic_manifest.{field} must be an array")
        for value in record[field]:
            _safe_text(value, f"forensic_manifest.{field}[]")
    for field in ("raw_conversation_included", "sanitized", "previewed"):
        if not isinstance(record[field], bool):
            raise ContractError(f"forensic_manifest.{field} must be boolean")
    if record["raw_conversation_included"]:
        raise ContractError("raw conversation is excluded from the default forensic manifest")
    _enum("forensic_manifest.consent_state", record["consent_state"], {"NOT_ASKED", "DECLINED", "GRANTED", "REVOKED"})
    return record

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
_MANIFEST_ID = re.compile(r"^FDM-[0-9]{8}-[0-9]{6}-[A-Za-z0-9]{4,16}$")
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


def _validate_run_ledgers(record: Mapping[str, Any]) -> None:
    """Validate the observable fields most likely to carry false claims."""

    capability_allowed = {
        "capability", "category", "need", "discovery_class", "availability", "auth_state",
        "run_consent_state", "invocation", "result", "source_or_adapter", "candidate_provenance",
        "consent_required", "consent_state", "fallback", "materiality", "evidence_refs",
    }
    capability_required = capability_allowed
    for index, item in enumerate(record["capability_ledger"]):
        _keys(item, required=capability_required, allowed=capability_allowed, name=f"capability_ledger[{index}]")
        _safe_text(item["capability"], f"capability_ledger[{index}].capability")
        _safe_text(item["category"], f"capability_ledger[{index}].category")
        _safe_text(item["need"], f"capability_ledger[{index}].need")
        _enum(f"capability_ledger[{index}].discovery_class", item["discovery_class"], DISCOVERY_CLASS)
        for field, values in (("availability", AVAILABILITY), ("auth_state", AUTH_STATE), ("run_consent_state", RUN_CONSENT_STATE), ("invocation", INVOCATION), ("result", RESULT)):
            _enum(f"capability_ledger[{index}].{field}", item[field], values)
        if not isinstance(item["consent_required"], bool):
            raise ContractError(f"capability_ledger[{index}].consent_required must be boolean")
        _enum(f"capability_ledger[{index}].consent_state", item["consent_state"], RUN_CONSENT_STATE)
        _enum(f"capability_ledger[{index}].materiality", item["materiality"], {"MATERIAL", "NON_MATERIAL", "UNKNOWN"})
        _validate_ref_list(item["evidence_refs"], f"capability_ledger[{index}].evidence_refs")
        provenance = item["candidate_provenance"]
        _keys(provenance, required={"provenance_class"}, allowed={"provenance_class", "source", "observed_at"}, name=f"capability_ledger[{index}].candidate_provenance")
        _enum(f"capability_ledger[{index}].candidate_provenance.provenance_class", provenance["provenance_class"], PROVENANCE)
        if "source" in provenance:
            validate_evidence_ref(provenance["source"])
        if "observed_at" in provenance:
            _timestamp(provenance["observed_at"], f"capability_ledger[{index}].candidate_provenance.observed_at")
        evidence_refs = _validate_ref_list(item["evidence_refs"], f"capability_ledger[{index}].evidence_refs")
        if item["invocation"] == "CALLED" and not evidence_refs:
            raise ContractError(f"capability_ledger[{index}] CALLED requires runtime evidence")
        if item["result"] == "SUCCESS" and not evidence_refs:
            raise ContractError(f"capability_ledger[{index}] SUCCESS requires runtime evidence")
        derive_execution_state(item["availability"], item["auth_state"], item["run_consent_state"], item["invocation"], item["result"], consent_required=item["consent_required"])

    evidence_allowed = {"claim_ref", "classification", "source_ref", "ref_date_version", "provenance", "note"}
    for index, item in enumerate(record["evidence_ledger"]):
        _keys(item, required={"claim_ref", "classification", "source_ref", "provenance"}, allowed=evidence_allowed, name=f"evidence_ledger[{index}]")
        _safe_text(item["claim_ref"], f"evidence_ledger[{index}].claim_ref")
        _enum(f"evidence_ledger[{index}].classification", item["classification"], {"FACT", "EVIDENCE", "INFERENCE", "HYPOTHESIS", "ASSUMPTION", "PREFERENCE", "UNKNOWN", "CONTRADICTION"})
        validate_evidence_ref(item["source_ref"])
        _enum(f"evidence_ledger[{index}].provenance", item["provenance"], PROVENANCE)

    mutation_allowed = {"mutation_id", "type", "target", "before_version_or_hash", "after_version_or_hash", "trigger", "applied_at", "applied_during_active_run", "validation", "affected_phases", "rollback_available", "status"}
    for index, item in enumerate(record["mutation_ledger"]):
        _keys(item, required=mutation_allowed, allowed=mutation_allowed, name=f"mutation_ledger[{index}]")
        _enum(f"mutation_ledger[{index}].type", item["type"], {"SKILL_MUTATED", "REFERENCE_MUTATED", "POLICY_MUTATED", "CONFIG_CHANGED", "PACKAGE_INSTALLED", "MCP_INSTALLED", "CONNECTION_CREATED", "FILE_CREATED", "FILE_MODIFIED", "CREDENTIAL_STATE_CHANGED", "OTHER_PERSISTENT_SIDE_EFFECT"})
        _timestamp(item["applied_at"], f"mutation_ledger[{index}].applied_at")
        for field in ("applied_during_active_run", "rollback_available"):
            if not isinstance(item[field], bool):
                raise ContractError(f"mutation_ledger[{index}].{field} must be boolean")
        _enum(f"mutation_ledger[{index}].validation", item["validation"], {"PASS", "FAIL", "PARTIAL", "UNKNOWN", "NOT_APPLICABLE"})
        _enum(f"mutation_ledger[{index}].status", item["status"], {"STAGED", "APPLIED", "BLOCKED", "REJECTED", "REVERTED"})
        for field in ("mutation_id", "target", "before_version_or_hash", "after_version_or_hash", "trigger"):
            _safe_text(item[field], f"mutation_ledger[{index}].{field}")
        if not isinstance(item["affected_phases"], list) or any(not isinstance(value, str) or not value for value in item["affected_phases"]):
            raise ContractError(f"mutation_ledger[{index}].affected_phases must be a list of bounded strings")


def _validate_auxiliary_ledgers(record: Mapping[str, Any]) -> None:
    """Validate the remaining Full Flow/Audit ledgers and closure objects."""

    phase_statuses = {"COMPLETE", "PARTIAL", "BLOCKED", "NOT_APPLICABLE"}
    for index, item in enumerate(record["phase_ledger"]):
        _keys(item, required={"phase", "status", "evidence_refs", "material_gap"}, allowed={"phase", "status", "evidence_refs", "material_gap", "provenance"}, name=f"phase_ledger[{index}]")
        _safe_text(item["phase"], f"phase_ledger[{index}].phase")
        _enum(f"phase_ledger[{index}].status", item["status"], phase_statuses)
        _validate_ref_list(item["evidence_refs"], f"phase_ledger[{index}].evidence_refs")
        if not isinstance(item["material_gap"], str) or len(item["material_gap"]) > 512 or "\n" in item["material_gap"] or "\x00" in item["material_gap"]:
            raise ContractError(f"phase_ledger[{index}].material_gap must be bounded text")
        if "provenance" in item:
            _enum(f"phase_ledger[{index}].provenance", item["provenance"], PROVENANCE)

    for index, item in enumerate(record["conditional_branch_ledger"]):
        _keys(item, required={"branch", "applicable", "status", "evidence_refs"}, allowed={"branch", "applicable", "status", "evidence_refs", "reason"}, name=f"conditional_branch_ledger[{index}]")
        _safe_text(item["branch"], f"conditional_branch_ledger[{index}].branch")
        if not isinstance(item["applicable"], bool):
            raise ContractError(f"conditional_branch_ledger[{index}].applicable must be boolean")
        _enum(f"conditional_branch_ledger[{index}].status", item["status"], phase_statuses)
        if not item["applicable"] and item["status"] != "NOT_APPLICABLE":
            raise ContractError(f"conditional_branch_ledger[{index}] non-applicable branch must be NOT_APPLICABLE")
        _validate_ref_list(item["evidence_refs"], f"conditional_branch_ledger[{index}].evidence_refs")
        if "reason" in item:
            _safe_text(item["reason"], f"conditional_branch_ledger[{index}].reason", 1024)

    for index, item in enumerate(record["method_ledger"]):
        _keys(item, required={"method", "used", "reason", "observable_result"}, allowed={"method", "used", "reason", "observable_result", "evidence_refs"}, name=f"method_ledger[{index}]")
        for field in ("method", "reason", "observable_result"):
            _safe_text(item[field], f"method_ledger[{index}].{field}")
        if not isinstance(item["used"], bool):
            raise ContractError(f"method_ledger[{index}].used must be boolean")
        if "evidence_refs" in item:
            _validate_ref_list(item["evidence_refs"], f"method_ledger[{index}].evidence_refs")

    for index, item in enumerate(record["gap_failure_ledger"]):
        _keys(item, required={"gap", "state", "recovery_attempted", "evidence_still_missing", "impact"}, allowed={"gap", "state", "recovery_attempted", "evidence_still_missing", "impact"}, name=f"gap_failure_ledger[{index}]")
        _safe_text(item["gap"], f"gap_failure_ledger[{index}].gap")
        _enum(f"gap_failure_ledger[{index}].state", item["state"], {"UNKNOWN", "PARTIAL", "BLOCKED", "RATE_LIMITED", "FAILED", "TRUNCATED", "UNAVAILABLE"})
        if not isinstance(item["recovery_attempted"], bool):
            raise ContractError(f"gap_failure_ledger[{index}].recovery_attempted must be boolean")
        _validate_ref_list(item["evidence_still_missing"], f"gap_failure_ledger[{index}].evidence_still_missing")
        _enum(f"gap_failure_ledger[{index}].impact", item["impact"], {"MATERIAL", "NON_MATERIAL", "UNKNOWN"})

    for index, item in enumerate(record["challenge_ledger"]):
        _keys(item, required={"attack", "evidence_or_plausibility", "what_would_break", "recommendation_impact", "mitigation_or_next_proof"}, allowed={"attack", "evidence_or_plausibility", "what_would_break", "recommendation_impact", "mitigation_or_next_proof", "evidence_refs"}, name=f"challenge_ledger[{index}]")
        for field in ("attack", "evidence_or_plausibility", "what_would_break", "mitigation_or_next_proof"):
            _safe_text(item[field], f"challenge_ledger[{index}].{field}")
        _enum(f"challenge_ledger[{index}].recommendation_impact", item["recommendation_impact"], {"maintains", "weakens", "conditions", "reverses"})
        if "evidence_refs" in item:
            _validate_ref_list(item["evidence_refs"], f"challenge_ledger[{index}].evidence_refs")

    side_effect_types = {"SKILL_MUTATED", "REFERENCE_MUTATED", "POLICY_MUTATED", "CONFIG_CHANGED", "PACKAGE_INSTALLED", "MCP_INSTALLED", "CONNECTION_CREATED", "FILE_CREATED", "FILE_MODIFIED", "CREDENTIAL_STATE_CHANGED", "OTHER_PERSISTENT_SIDE_EFFECT"}
    for index, item in enumerate(record["persistent_side_effects"]):
        _keys(item, required={"type", "observed", "evidence_refs"}, allowed={"type", "observed", "target_class", "evidence_refs"}, name=f"persistent_side_effects[{index}]")
        _enum(f"persistent_side_effects[{index}].type", item["type"], side_effect_types)
        if not isinstance(item["observed"], bool):
            raise ContractError(f"persistent_side_effects[{index}].observed must be boolean")
        if "target_class" in item:
            _safe_text(item["target_class"], f"persistent_side_effects[{index}].target_class", 128)
        _validate_ref_list(item["evidence_refs"], f"persistent_side_effects[{index}].evidence_refs")

    budget = record["research_budget"]
    _keys(budget, required={"planned", "consumed", "checkpoints", "stop_reason"}, allowed={"planned", "consumed", "checkpoints", "stop_reason"}, name="research_budget")
    units = {"web_calls", "source_count", "elapsed_seconds", "context_fraction"}
    for field in ("planned", "consumed"):
        counters = budget[field]
        if not isinstance(counters, Mapping) or set(counters) - units:
            raise ContractError(f"research_budget.{field} contains an unknown counter")
        for unit, counter in counters.items():
            _keys(counter, required={"value", "soft_limit", "hard_limit", "observable"}, allowed={"value", "soft_limit", "hard_limit", "observable"}, name=f"research_budget.{field}.{unit}")
            if not isinstance(counter["observable"], bool):
                raise ContractError(f"research_budget.{field}.{unit}.observable must be boolean")
            for counter_name in ("value", "soft_limit", "hard_limit"):
                value = counter[counter_name]
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0):
                    raise ContractError(f"research_budget.{field}.{unit}.{counter_name} must be a non-negative number or null")
            if counter["soft_limit"] is not None and counter["hard_limit"] is not None and counter["soft_limit"] > counter["hard_limit"]:
                raise ContractError(f"research_budget.{field}.{unit} soft limit exceeds hard limit")
            if counter["observable"] is False and counter["value"] is not None:
                raise ContractError(f"research_budget.{field}.{unit} cannot claim an unobservable value")
    if not isinstance(budget["checkpoints"], list):
        raise ContractError("research_budget.checkpoints must be an array")
    for index, checkpoint in enumerate(budget["checkpoints"]):
        _keys(checkpoint, required={"at", "decision", "reserved_for_closure"}, allowed={"at", "decision", "reserved_for_closure"}, name=f"research_budget.checkpoints[{index}]")
        _enum(f"research_budget.checkpoints[{index}].at", checkpoint["at"], {"50_PERCENT", "80_PERCENT", "BEFORE_HARD_LIMIT", "COMPACTION", "MIGRATION_TRIGGER"})
        _enum(f"research_budget.checkpoints[{index}].decision", checkpoint["decision"], {"CONTINUE", "MIGRATE_TO_CORPUS", "STOP_RESEARCH_AND_TEST", "FREEZE_AND_SYNTHESIZE", "UNKNOWN"})
        if not isinstance(checkpoint["reserved_for_closure"], bool):
            raise ContractError(f"research_budget.checkpoints[{index}].reserved_for_closure must be boolean")
    _safe_text(budget["stop_reason"], "research_budget.stop_reason")

    for index, item in enumerate(record["provider_host_failures"]):
        _keys(item, required={"provider_or_host", "failure_class", "state", "fallback", "closure_emitted"}, allowed={"provider_or_host", "failure_class", "state", "fallback", "closure_emitted"}, name=f"provider_host_failures[{index}]")
        _safe_text(item["provider_or_host"], f"provider_host_failures[{index}].provider_or_host")
        _enum(f"provider_host_failures[{index}].failure_class", item["failure_class"], {"UNSUPPORTED_PARAMETER", "RATE_LIMITED", "TIMEOUT", "TRUNCATED", "PROVIDER_ERROR", "TOOL_ERROR", "UNKNOWN"})
        _enum(f"provider_host_failures[{index}].state", item["state"], {"AVAILABLE", "UNAVAILABLE", "PARTIAL", "FAILED", "BLOCKED", "UNKNOWN"})
        _enum(f"provider_host_failures[{index}].fallback", item["fallback"], {"NONE", "SUPPORTED_SETTING", "ALTERNATE_PROVIDER", "PERSISTED_RUN_STATE", "MANUAL_NEXT_PROOF", "UNKNOWN"})
        if not isinstance(item["closure_emitted"], bool):
            raise ContractError(f"provider_host_failures[{index}].closure_emitted must be boolean")

    _keys(record["stop"], required={"state", "reason"}, allowed={"state", "reason", "material_unknowns_remaining", "budget_consumed"}, name="run_record.stop")
    _enum("run_record.stop.state", record["stop"]["state"], {"STOP", "CONTINUE", "STOP_RESEARCH_AND_TEST"})
    _safe_text(record["stop"]["reason"], "run_record.stop.reason")
    if "material_unknowns_remaining" in record["stop"] and not isinstance(record["stop"]["material_unknowns_remaining"], bool):
        raise ContractError("run_record.stop.material_unknowns_remaining must be boolean")
    if "budget_consumed" in record["stop"]:
        _safe_text(record["stop"]["budget_consumed"], "run_record.stop.budget_consumed")

    if record["next_proof"] is not None:
        proof = record["next_proof"]
        _keys(proof, required={"hypothesis", "question_tested", "smallest_experiment", "metric", "information_value"}, allowed={"hypothesis", "question_tested", "smallest_experiment", "data_needed", "metric", "proposed_threshold", "information_value", "what_changes_if_pass", "what_changes_if_fail"}, name="run_record.next_proof")
        for field in ("hypothesis", "question_tested", "smallest_experiment", "metric"):
            _safe_text(proof[field], f"run_record.next_proof.{field}")
        _enum("run_record.next_proof.information_value", proof["information_value"], {"HIGH", "MEDIUM", "LOW"})
        for field in ("data_needed", "proposed_threshold", "what_changes_if_pass", "what_changes_if_fail"):
            if field in proof:
                _safe_text(proof[field], f"run_record.next_proof.{field}")

    for index, item in enumerate(record["evidence_ledger"]):
        if item.get("provenance") == "MODEL_SYNTHESIZED" and item.get("classification") in {"FACT", "EVIDENCE"}:
            raise ContractError(f"evidence_ledger[{index}] cannot call model synthesis a fact/evidence")


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
    if record["schema_version"] != "cognitive-os-run-record-v1.5":
        raise ContractError("unsupported run_record schema_version")
    _timestamp(record["created_at"], "run_record.created_at")
    if "finished_at" in record:
        _timestamp(record["finished_at"], "run_record.finished_at")
        created = _dt.datetime.fromisoformat(record["created_at"].replace("Z", "+00:00"))
        finished = _dt.datetime.fromisoformat(record["finished_at"].replace("Z", "+00:00"))
        if finished < created:
            raise ContractError("run_record.finished_at cannot precede created_at")
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
    _validate_run_ledgers(record)
    if not isinstance(record["research_budget"], Mapping):
        raise ContractError("run_record.research_budget must be an object")
    _validate_auxiliary_ledgers(record)
    _keys(record["telemetry"], required={"mode", "state"}, allowed={"mode", "state", "trace_ref", "consent_policy_version"}, name="run_record.telemetry")
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
    if record["schema_version"] != "cognitive-os-capability-decision-v1.5":
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
    if not isinstance(record["manifest_id"], str) or not _MANIFEST_ID.fullmatch(record["manifest_id"]):
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
    started = _dt.datetime.fromisoformat(record["window"]["started_at"].replace("Z", "+00:00"))
    ended = _dt.datetime.fromisoformat(record["window"]["ended_at"].replace("Z", "+00:00"))
    if ended < started:
        raise ContractError("forensic_manifest.window is reversed")
    limits = {"allowlisted_sources": 32, "session_ids": 32, "artifacts": 64}
    for field in ("allowlisted_sources", "session_ids", "artifacts"):
        if not isinstance(record[field], list):
            raise ContractError(f"forensic_manifest.{field} must be an array")
        if len(record[field]) > limits[field]:
            raise ContractError(f"forensic_manifest.{field} exceeds its bounded item limit")
        if any(not isinstance(value, str) for value in record[field]):
            raise ContractError(f"forensic_manifest.{field}[] must be a string")
        if len(record[field]) != len(set(record[field])):
            raise ContractError(f"forensic_manifest.{field} must not repeat identifiers")
        for value in record[field]:
            _safe_text(value, f"forensic_manifest.{field}[]")
            if value.startswith(("/", "\\")) or ".." in value.split("/") or "file://" in value.lower():
                raise ContractError(f"forensic_manifest.{field}[] must not contain an unscoped path")
    for field in ("raw_conversation_included", "sanitized", "previewed"):
        if not isinstance(record[field], bool):
            raise ContractError(f"forensic_manifest.{field} must be boolean")
    if record["raw_conversation_included"]:
        raise ContractError("raw conversation is excluded from the default forensic manifest")
    if not record["sanitized"]:
        raise ContractError("forensic manifest must be sanitized before preview/share")
    _enum("forensic_manifest.consent_state", record["consent_state"], {"NOT_ASKED", "DECLINED", "GRANTED", "REVOKED"})
    if record["consent_state"] == "GRANTED" and not record["previewed"]:
        raise ContractError("forensic manifest requires preview before consented sharing")
    return record

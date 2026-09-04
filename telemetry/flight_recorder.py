"""Construct-by-allowlist Flight Recorder and shared payload projection."""

from __future__ import annotations

import copy
import datetime as dt
import json
import re
import secrets
from typing import Any, Mapping


class TraceError(ValueError):
    """Raised when a trace cannot be proven privacy-safe and well formed."""


HOST_FAMILIES = frozenset({"hermes", "chatgpt-work", "codex", "claude", "gemini", "generic", "unknown"})
SURFACE_CLASSES = frozenset({"cli", "terminal", "work", "work-mobile", "desktop", "mobile", "unknown"})
DEPTHS = frozenset({"fast", "normal", "deep", "board360"})
CAPABILITY_KEYS = (
    "local_skill_discovery",
    "local_tool_discovery",
    "local_connector_discovery",
    "external_skill_discovery",
    "external_mcp_discovery",
    "custom_capability",
)
CAPABILITY_RESULT = frozenset({"success", "partial", "truncated", "rate_limited", "unavailable", "blocked", "failed", "not_called"})
GROUNDING_STATES = frozenset({"success", "partial", "unavailable", "blocked", "failed", "not_called"})
SIDE_EFFECT_TYPES = frozenset({
    "SKILL_MUTATED", "REFERENCE_MUTATED", "POLICY_MUTATED", "CONFIG_CHANGED", "PACKAGE_INSTALLED",
    "MCP_INSTALLED", "CONNECTION_CREATED", "FILE_CREATED", "FILE_MODIFIED", "CREDENTIAL_STATE_CHANGED",
    "OTHER_PERSISTENT_SIDE_EFFECT",
})
PROVIDER_FAILURES = frozenset({"unsupported_parameter", "rate_limited", "timeout", "truncated", "provider_error", "tool_error", "unknown"})
PHASES = frozenset({"context", "question", "evidence", "depth", "sources", "capabilities", "research", "methods", "challenge", "stop", "recommendation"})
PHASE_STATES = frozenset({"complete", "partial", "blocked", "not_applicable"})
DECISION_STATES = frozenset({"ready_to_decide", "decided", "test_required", "more_evidence_required", "blocked", "no_action_recommended", "recommendation_only", "unknown"})
RUN_STATES = frozenset({"complete", "partial", "failed", "blocked", "unknown"})
FEEDBACK_HELPFULNESS = frozenset({"HELPED", "PARTIALLY_HELPED", "NOT_HELPED"})
FEEDBACK_REASONS = frozenset({
    "INSUFFICIENT_EVIDENCE", "INSUFFICIENT_DEPTH", "CAPABILITY_UNAVAILABLE_OR_INADEQUATE",
    "INSUFFICIENT_CONTEXT", "CLARITY", "OTHER",
})
STOP_REASONS = frozenset({"NOT_SET", "BOUNDED", "NO_MATERIAL_UNKNOWN", "NEXT_PROOF", "RATE_LIMITED", "PROVIDER_FAILURE", "USER_STOP", "UNKNOWN"})
FALLBACKS = frozenset({"none", "supported_setting", "alternate_provider", "persisted_run_state", "manual_next_proof", "composed_research", "unknown"})
_RUN_ID = re.compile(r"^CRR-[0-9]{8}-[0-9]{6}-[A-Za-z0-9]{4,16}$")
_EVENT_ID = re.compile(r"^EVT-[A-Fa-f0-9]{24}$")
_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")


def _run_id() -> str:
    now = dt.datetime.now(dt.timezone.utc)
    return f"CRR-{now:%Y%m%d-%H%M%S}-{secrets.token_hex(2).upper()}"


def _bucket(value: int) -> str:
    if value <= 0:
        return "0"
    if value <= 3:
        return "1-3"
    if value <= 10:
        return "4-10"
    return "11+"


def _merge_result(previous: str, current: str) -> str:
    order = {"not_called": 0, "success": 1, "partial": 2, "unavailable": 2, "blocked": 3, "rate_limited": 3, "failed": 4, "truncated": 4}
    return current if order.get(current, 4) >= order.get(previous, 0) else previous


class UsageTrace:
    """Mutable local trace with only typed, allowlisted mutation methods."""

    def __init__(self, data: Mapping[str, Any]):
        self._data = copy.deepcopy(dict(data))
        sanitize_usage_trace(self._data)

    def record_phase(self, phase: str, state: str) -> None:
        if phase not in PHASES or state not in PHASE_STATES:
            raise TraceError("phase/state is not allowlisted")
        self._data["phase_states"][phase] = state

    def record_capability(self, capability: str, result: str) -> None:
        if result not in CAPABILITY_RESULT:
            raise TraceError("capability result is not allowlisted")
        key = capability if capability in CAPABILITY_KEYS else "custom_capability"
        self._data["capability_events"][key] = _merge_result(self._data["capability_events"][key], result)
        if key not in self._data["capabilities_checked"]:
            self._data["capabilities_checked"].append(key)

    def record_web_call(self, *, success: bool, rate_limited: bool = False) -> None:
        operational = self._data["local_operational"]
        operational["web_search_count"] += 1
        self._data["research"]["web_calls_bucket"] = _bucket(operational["web_search_count"])
        if not success:
            self._data["failures"]["web_failure"] = True
        if rate_limited:
            self._data["failures"]["rate_limited"] = True

    def record_grounded_corpus(self, state: str) -> None:
        if state not in GROUNDING_STATES:
            raise TraceError("grounded corpus state is not allowlisted")
        self._data["research"]["grounded_corpus"] = state

    def record_notebooklm(self, state: str) -> None:
        if state not in GROUNDING_STATES:
            raise TraceError("NotebookLM state is not allowlisted")
        self._data["research"]["notebooklm"] = state

    def record_compaction(self) -> None:
        self._data["research"]["compaction_occurred"] = True

    def record_mutation(self, effect_type: str) -> None:
        if effect_type not in SIDE_EFFECT_TYPES:
            effect_type = "OTHER_PERSISTENT_SIDE_EFFECT"
        if effect_type not in self._data["side_effects"]["types"]:
            self._data["side_effects"]["types"].append(effect_type)
        self._data["side_effects"]["persistent_change"] = True

    def record_provider_failure(self, failure_class: str) -> None:
        if failure_class not in PROVIDER_FAILURES:
            failure_class = "unknown"
        self._data["failures"]["provider_failure"] = True
        if failure_class not in self._data["failures"]["provider_classes"]:
            self._data["failures"]["provider_classes"].append(failure_class)

    def record_fallback(self, fallback: str) -> None:
        if fallback not in FALLBACKS:
            raise TraceError("fallback is not allowlisted")
        if fallback not in self._data["fallbacks"]:
            self._data["fallbacks"].append(fallback)

    def set_stop_reason(self, reason: str) -> None:
        if reason not in STOP_REASONS:
            raise TraceError("stop reason is not allowlisted")
        self._data["stop_reason"] = reason

    def set_decision(self, decision_state: str, run_status: str) -> None:
        if decision_state.lower() not in DECISION_STATES or run_status.lower() not in RUN_STATES:
            raise TraceError("decision/run state is not allowlisted")
        self._data["decision_state"] = decision_state.lower()
        self._data["run_status"] = run_status.lower()

    def set_feedback(self, helpfulness: str | None, reason: str | None = None) -> None:
        if helpfulness is not None and helpfulness not in FEEDBACK_HELPFULNESS:
            raise TraceError("feedback helpfulness is not allowlisted")
        if reason is not None and reason not in FEEDBACK_REASONS:
            raise TraceError("feedback reason is not allowlisted")
        self._data["feedback"] = {"helpfulness": helpfulness, "reason": reason}

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._data)


def new_usage_trace(
    cognitive_os_version: str,
    host_family: str,
    surface_class: str,
    *,
    run_id: str | None = None,
    event_id: str | None = None,
    depth: str = "normal",
    full_flow_audit: bool = False,
) -> UsageTrace:
    if not _VERSION.fullmatch(cognitive_os_version) or host_family not in HOST_FAMILIES or surface_class not in SURFACE_CLASSES:
        raise TraceError("trace identity is not allowlisted")
    if depth not in DEPTHS or not isinstance(full_flow_audit, bool):
        raise TraceError("trace depth/audit flag is invalid")
    actual_run_id = run_id or _run_id()
    if not _RUN_ID.fullmatch(actual_run_id):
        raise TraceError("run_id must be host-shaped and non-identifying")
    actual_event_id = event_id or f"EVT-{secrets.token_hex(12)}"
    if not _EVENT_ID.fullmatch(actual_event_id):
        raise TraceError("event_id must be a random, non-identifying idempotency id")
    return UsageTrace({
        "schema_version": 1,
        "cognitive_os_version": cognitive_os_version,
        "host_family": host_family,
        "surface_class": surface_class,
        "run_id": actual_run_id,
        "event_id": actual_event_id,
        "depth": depth,
        "full_flow_audit": full_flow_audit,
        "phase_states": {},
        "capabilities_checked": [],
        "candidate_capabilities": [],
        "skills_loaded": [],
        "capability_events": {key: "not_called" for key in CAPABILITY_KEYS},
        "research": {
            "web_calls_bucket": "0",
            "grounded_corpus": "not_called",
            "notebooklm": "not_called",
            "compaction_occurred": False,
        },
        "failures": {
            "web_failure": False,
            "rate_limited": False,
            "provider_failure": False,
            "provider_classes": [],
        },
        "side_effects": {"persistent_change": False, "types": []},
        "fallbacks": [],
        "decision_state": "unknown",
        "run_status": "unknown",
        "stop_reason": "NOT_SET",
        "feedback": {"helpfulness": None, "reason": None},
        "local_operational": {"web_search_count": 0, "source_count": 0, "event_ordinals": []},
    })


def _require_keys(value: Mapping[str, Any], allowed: set[str], name: str) -> None:
    if not isinstance(value, Mapping):
        raise TraceError(f"{name} must be an object")
    unknown = set(value) - allowed
    if unknown:
        raise TraceError(f"{name} has unknown fields: {', '.join(sorted(unknown))}")


def sanitize_usage_trace(value: Mapping[str, Any] | UsageTrace) -> dict[str, Any]:
    """Validate a constructed trace; no redaction step can authorize extra fields."""

    data = value.to_dict() if isinstance(value, UsageTrace) else copy.deepcopy(dict(value))
    allowed = {
        "schema_version", "cognitive_os_version", "host_family", "surface_class", "run_id", "event_id", "depth",
        "full_flow_audit", "phase_states", "capabilities_checked", "candidate_capabilities", "skills_loaded",
        "capability_events", "research", "failures", "side_effects", "fallbacks", "decision_state", "run_status",
        "stop_reason", "feedback", "local_operational",
    }
    _require_keys(data, allowed, "usage_trace")
    if data.get("schema_version") != 1 or not isinstance(data.get("cognitive_os_version"), str) or not _VERSION.fullmatch(data["cognitive_os_version"]):
        raise TraceError("usage_trace schema/version is invalid")
    if data.get("host_family") not in HOST_FAMILIES or data.get("surface_class") not in SURFACE_CLASSES:
        raise TraceError("usage_trace host/surface is not allowlisted")
    if not isinstance(data.get("run_id"), str) or not _RUN_ID.fullmatch(data["run_id"]):
        raise TraceError("usage_trace run_id is invalid")
    if not isinstance(data.get("event_id"), str) or not _EVENT_ID.fullmatch(data["event_id"]):
        raise TraceError("usage_trace event_id is invalid")
    if data.get("depth") not in DEPTHS or not isinstance(data.get("full_flow_audit"), bool):
        raise TraceError("usage_trace depth/audit is invalid")
    phase_states = data.get("phase_states")
    _require_keys(phase_states, set(PHASES), "usage_trace.phase_states")
    if any(state not in PHASE_STATES for state in phase_states.values()):
        raise TraceError("usage_trace phase state is invalid")
    for field in ("capabilities_checked", "candidate_capabilities", "skills_loaded"):
        values = data.get(field)
        if not isinstance(values, list) or any(item not in CAPABILITY_KEYS for item in values):
            raise TraceError(f"usage_trace.{field} is not an allowlisted category list")
    events = data.get("capability_events")
    _require_keys(events, set(CAPABILITY_KEYS), "usage_trace.capability_events")
    if any(result not in CAPABILITY_RESULT for result in events.values()):
        raise TraceError("usage_trace capability result is invalid")
    research = data.get("research")
    _require_keys(research, {"web_calls_bucket", "grounded_corpus", "notebooklm", "compaction_occurred"}, "usage_trace.research")
    if research.get("web_calls_bucket") not in {"0", "1-3", "4-10", "11+"} or research.get("grounded_corpus") not in GROUNDING_STATES or research.get("notebooklm") not in GROUNDING_STATES or not isinstance(research.get("compaction_occurred"), bool):
        raise TraceError("usage_trace research fields are invalid")
    failures = data.get("failures")
    _require_keys(failures, {"web_failure", "rate_limited", "provider_failure", "provider_classes"}, "usage_trace.failures")
    if any(not isinstance(failures.get(field), bool) for field in ("web_failure", "rate_limited", "provider_failure")) or not isinstance(failures.get("provider_classes"), list) or any(item not in PROVIDER_FAILURES for item in failures["provider_classes"]):
        raise TraceError("usage_trace failure fields are invalid")
    effects = data.get("side_effects")
    _require_keys(effects, {"persistent_change", "types"}, "usage_trace.side_effects")
    if not isinstance(effects.get("persistent_change"), bool) or not isinstance(effects.get("types"), list) or any(item not in SIDE_EFFECT_TYPES for item in effects["types"]):
        raise TraceError("usage_trace side-effect fields are invalid")
    fallbacks = data.get("fallbacks")
    if not isinstance(fallbacks, list) or any(item not in FALLBACKS for item in fallbacks):
        raise TraceError("usage_trace fallbacks are invalid")
    if data.get("decision_state") not in DECISION_STATES or data.get("run_status") not in RUN_STATES or data.get("stop_reason") not in STOP_REASONS:
        raise TraceError("usage_trace final state is invalid")
    feedback = data.get("feedback")
    _require_keys(feedback, {"helpfulness", "reason"}, "usage_trace.feedback")
    if feedback.get("helpfulness") is not None and feedback["helpfulness"] not in FEEDBACK_HELPFULNESS:
        raise TraceError("usage_trace feedback helpfulness is invalid")
    if feedback.get("reason") is not None and feedback["reason"] not in FEEDBACK_REASONS:
        raise TraceError("usage_trace feedback reason is invalid")
    operational = data.get("local_operational")
    _require_keys(operational, {"web_search_count", "source_count", "event_ordinals"}, "usage_trace.local_operational")
    if any(not isinstance(operational.get(field), int) or operational[field] < 0 for field in ("web_search_count", "source_count")) or not isinstance(operational.get("event_ordinals"), list) or any(not isinstance(item, int) or item < 0 for item in operational["event_ordinals"]):
        raise TraceError("usage_trace local operational counters are invalid")
    return data


def build_shared_payload(trace: UsageTrace | Mapping[str, Any]) -> dict[str, Any]:
    """Project local trace into the lower-cardinality shared event allowlist."""

    data = sanitize_usage_trace(trace)
    payload = {
        "schema_version": data["schema_version"],
        "cognitive_os_version": data["cognitive_os_version"],
        "host_family": data["host_family"],
        "surface_class": data["surface_class"],
        "run_id": data["run_id"],
        "event_id": data["event_id"],
        "depth": data["depth"],
        "full_flow_audit": data["full_flow_audit"],
        "capability_events": dict(data["capability_events"]),
        "research": dict(data["research"]),
        "failures": {
            "rate_limited": data["failures"]["rate_limited"],
            "provider_failure": data["failures"]["provider_failure"],
        },
        "side_effects": {"persistent_change": data["side_effects"]["persistent_change"]},
        "feedback": dict(data["feedback"]),
        "decision_state": data["decision_state"],
        "run_status": data["run_status"],
    }
    validate_shared_payload(payload)
    return payload


def validate_shared_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the exact outbound allowlist, including nested objects."""

    data = copy.deepcopy(dict(value))
    allowed = {
        "schema_version", "cognitive_os_version", "host_family", "surface_class", "run_id", "event_id", "depth",
        "full_flow_audit", "capability_events", "research", "failures", "side_effects", "feedback",
        "decision_state", "run_status",
    }
    _require_keys(data, allowed, "shared_payload")
    if set(data) != allowed:
        raise TraceError("shared_payload is missing an allowlisted field")
    # Reuse the local identity/enum checks without accepting any local-only data.
    if data["schema_version"] != 1 or not isinstance(data["cognitive_os_version"], str) or not _VERSION.fullmatch(data["cognitive_os_version"]):
        raise TraceError("shared_payload schema/version is invalid")
    if data["host_family"] not in HOST_FAMILIES or data["surface_class"] not in SURFACE_CLASSES:
        raise TraceError("shared_payload host/surface is invalid")
    if not isinstance(data["run_id"], str) or not _RUN_ID.fullmatch(data["run_id"]):
        raise TraceError("shared_payload run_id is invalid")
    if not isinstance(data["event_id"], str) or not _EVENT_ID.fullmatch(data["event_id"]):
        raise TraceError("shared_payload event_id is invalid")
    if data["depth"] not in DEPTHS or not isinstance(data["full_flow_audit"], bool):
        raise TraceError("shared_payload depth/audit is invalid")
    events = data["capability_events"]
    _require_keys(events, set(CAPABILITY_KEYS), "shared_payload.capability_events")
    if any(result not in CAPABILITY_RESULT for result in events.values()):
        raise TraceError("shared_payload capability result is invalid")
    research = data["research"]
    _require_keys(research, {"web_calls_bucket", "grounded_corpus", "notebooklm", "compaction_occurred"}, "shared_payload.research")
    if research["web_calls_bucket"] not in {"0", "1-3", "4-10", "11+"} or research["grounded_corpus"] not in GROUNDING_STATES or research["notebooklm"] not in GROUNDING_STATES or not isinstance(research["compaction_occurred"], bool):
        raise TraceError("shared_payload research is invalid")
    failures = data["failures"]
    _require_keys(failures, {"rate_limited", "provider_failure"}, "shared_payload.failures")
    if any(not isinstance(failures[key], bool) for key in failures):
        raise TraceError("shared_payload failures are invalid")
    effects = data["side_effects"]
    _require_keys(effects, {"persistent_change"}, "shared_payload.side_effects")
    if not isinstance(effects["persistent_change"], bool):
        raise TraceError("shared_payload side_effects are invalid")
    feedback = data["feedback"]
    _require_keys(feedback, {"helpfulness", "reason"}, "shared_payload.feedback")
    if feedback["helpfulness"] is not None and feedback["helpfulness"] not in FEEDBACK_HELPFULNESS:
        raise TraceError("shared_payload feedback helpfulness is invalid")
    if feedback["reason"] is not None and feedback["reason"] not in FEEDBACK_REASONS:
        raise TraceError("shared_payload feedback reason is invalid")
    if data["decision_state"] not in DECISION_STATES or data["run_status"] not in RUN_STATES:
        raise TraceError("shared_payload final state is invalid")
    return data


def serialized_shared_payload(trace: UsageTrace | Mapping[str, Any]) -> bytes:
    return json.dumps(build_shared_payload(trace), ensure_ascii=False, separators=(",", ":")).encode("utf-8")

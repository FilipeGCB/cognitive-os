#!/usr/bin/env python3
"""Deterministic, side-effect-free capability preflight/planning for Cognitive OS.

This module does not install third-party software. It models whether an existing
capability should be used, whether a previously approved light component could
be auto-installed under one-time consent, or whether specific consent is
required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Optional

from cognitive_os_contracts import (
    ADOPTION_STATE,
    AUTH_STATE,
    AVAILABILITY,
    DISCOVERY_CLASS,
    INVOCATION,
    RESULT,
    RUN_CONSENT_STATE,
    derive_execution_state,
)


VALID_AVAILABILITY = {"AVAILABLE", "UNAVAILABLE", "UNKNOWN"}


@dataclass(frozen=True)
class HostSnapshot:
    host: str
    surface: str


@dataclass(frozen=True)
class CapabilitySnapshot:
    capability: str
    availability: str
    implementation: Optional[str] = None

    def __post_init__(self) -> None:
        if self.availability not in VALID_AVAILABILITY:
            raise ValueError(f"invalid availability: {self.availability}")


@dataclass(frozen=True)
class ConsentProfile:
    safe_local_enhancements: bool = False


@dataclass(frozen=True)
class InstallDecision:
    action: str
    capability: str
    candidate_id: Optional[str] = None
    reason: str = ""


AUTO_INSTALL_REQUIRED_TRUE = ("approved", "user_space", "light", "reversible")
AUTO_INSTALL_REQUIRED_FALSE = (
    "account",
    "secret",
    "sensitive_persistent_access",
    "write",
    "privileged",
)


def _is_auto_install_safe(candidate: Mapping[str, object]) -> bool:
    return all(candidate.get(key) is True for key in AUTO_INSTALL_REQUIRED_TRUE) and all(
        candidate.get(key) is False for key in AUTO_INSTALL_REQUIRED_FALSE
    )


def _requires_specific_consent(candidate: Mapping[str, object]) -> bool:
    return any(
        candidate.get(key) is True
        for key in (
            "heavy",
            "account",
            "secret",
            "sensitive_persistent_access",
            "write",
            "privileged",
        )
    )


def plan_gap_fill(
    snapshot: CapabilitySnapshot,
    consent: ConsentProfile,
    candidates: Iterable[Mapping[str, object]],
) -> InstallDecision:
    """Return the next capability action without executing installation."""

    if snapshot.availability == "AVAILABLE":
        return InstallDecision(
            action="USE_EXISTING",
            capability=snapshot.capability,
            candidate_id=snapshot.implementation,
            reason="A sufficient capability is already available on this surface.",
        )

    approved_candidates = [c for c in candidates if c.get("approved") is True]
    if not approved_candidates:
        return InstallDecision(
            action="NO_APPROVED_IMPLEMENTATION",
            capability=snapshot.capability,
            reason="No approved implementation is available for this capability gap.",
        )

    for candidate in approved_candidates:
        candidate_id = str(candidate.get("id") or "") or None
        if _requires_specific_consent(candidate):
            return InstallDecision(
                action="ASK_SPECIFIC_CONSENT",
                capability=snapshot.capability,
                candidate_id=candidate_id,
                reason="The candidate crosses a heavy, account, credential, sensitive, write, or privileged boundary.",
            )
        if consent.safe_local_enhancements and _is_auto_install_safe(candidate):
            return InstallDecision(
                action="AUTO_INSTALL_ALLOWED",
                capability=snapshot.capability,
                candidate_id=candidate_id,
                reason="The candidate is approved, light, local/user-space, reversible, and inside the one-time consent boundary.",
            )

    return InstallDecision(
        action="BLOCKED",
        capability=snapshot.capability,
        reason="Candidates exist, but none is authorized by the current consent and safety policy.",
    )


DISCOVERY_ASSET_STATUSES = {"APPROVED", "BLOCKED", "UNAVAILABLE"}
IDENTITY_STATUS = {"PROVEN", "UNPROVEN"}


@dataclass(frozen=True)
class CapabilityState:
    """Runtime state; availability/authentication never imply run consent."""

    capability: str
    availability: str
    auth_state: str
    run_consent_state: str
    invocation: str
    result: Optional[str]
    consent_required: bool = False

    def __post_init__(self) -> None:
        if not self.capability:
            raise ValueError("capability is required")
        derive_execution_state(
            self.availability,
            self.auth_state,
            self.run_consent_state,
            self.invocation,
            self.result,
            consent_required=self.consent_required,
        )

    @property
    def execution_state(self) -> str:
        return derive_execution_state(
            self.availability,
            self.auth_state,
            self.run_consent_state,
            self.invocation,
            self.result,
            consent_required=self.consent_required,
        )

    @property
    def can_call(self) -> bool:
        return (
            self.availability == "AVAILABLE"
            and self.auth_state not in {"REQUIRED_NOT_AUTHENTICATED", "UNKNOWN"}
            and (not self.consent_required or self.run_consent_state == "GRANTED")
        )


@dataclass(frozen=True)
class DiscoveryAsset:
    """An approved search mechanism, distinct from a capability candidate."""

    id: str
    asset_type: str = "EXTERNAL_SKILL_DISCOVERY"
    source: Optional[str] = None
    owner: Optional[str] = None
    repository: Optional[str] = None
    maintainer: Optional[str] = None
    version: Optional[str] = None
    license: Optional[str] = None
    mechanism: Optional[str] = None
    status: str = "BLOCKED"
    identity_status: str = "PROVEN"
    hosts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("discovery asset id is required")
        if self.asset_type not in {"EXTERNAL_SKILL_DISCOVERY", "EXTERNAL_MCP_DISCOVERY"}:
            raise ValueError(f"invalid discovery asset type: {self.asset_type}")
        if self.status not in DISCOVERY_ASSET_STATUSES:
            raise ValueError(f"invalid discovery asset status: {self.status}")
        if self.identity_status not in IDENTITY_STATUS:
            raise ValueError(f"invalid discovery asset identity status: {self.identity_status}")

    @classmethod
    def blocked(cls, asset_id: str) -> "DiscoveryAsset":
        asset_type = "EXTERNAL_MCP_DISCOVERY" if "mcp" in asset_id.lower() else "EXTERNAL_SKILL_DISCOVERY"
        return cls(
            id=asset_id,
            asset_type=asset_type,
            status="BLOCKED",
            identity_status="UNPROVEN",
        )

    @property
    def usable(self) -> bool:
        return (
            self.status == "APPROVED"
            and self.identity_status == "PROVEN"
            and all(bool(value) for value in (self.source, self.owner, self.repository, self.maintainer, self.version, self.license, self.mechanism))
        )


@dataclass(frozen=True)
class CandidateAssessment:
    candidate_id: str
    status: str
    execution_allowed: bool
    security_required: bool
    consent_required: bool
    reason: str


def assess_candidate(
    candidate: Mapping[str, object],
    *,
    asset: DiscoveryAsset,
    ephemeral: bool = False,
) -> CandidateAssessment:
    """Evaluate a found candidate; an asset's approval never transfers to it."""

    candidate_id = str(candidate.get("id") or "unknown-candidate")
    security_required = True
    if not asset.usable:
        return CandidateAssessment(
            candidate_id,
            "QUARANTINED",
            False,
            security_required,
            False,
            "The discovery asset is not itself sufficient provenance for a candidate.",
        )
    required_fields = ("source", "version", "license", "gauntlet_status", "permissions")
    if any(field not in candidate for field in required_fields):
        return CandidateAssessment(
            candidate_id,
            "QUARANTINED",
            False,
            security_required,
            False,
            "Candidate provenance or permission metadata is incomplete.",
        )
    if candidate.get("gauntlet_status") != "PASS":
        return CandidateAssessment(
            candidate_id,
            "QUARANTINED",
            False,
            security_required,
            False,
            "Candidate has not passed its own Gauntlet.",
        )
    permissions = candidate.get("permissions")
    if not isinstance(permissions, Mapping):
        return CandidateAssessment(candidate_id, "QUARANTINED", False, security_required, False, "Permissions are not inspectable.")
    if any(not isinstance(value, (bool, str, int, float, type(None))) for value in permissions.values()):
        return CandidateAssessment(candidate_id, "QUARANTINED", False, security_required, False, "Permission metadata is malformed.")
    consent_required = any(
        bool(candidate.get(key))
        for key in ("account_bound", "requires_specific_consent", "sensitive_persistent_access", "write", "privileged", "external_side_effect")
    ) or bool(permissions.get("write"))
    if consent_required:
        return CandidateAssessment(
            candidate_id,
            "PERSISTENT_ADOPTION_PENDING_CONSENT",
            False,
            security_required,
            True,
            "External execution remains subject to specific consent for account, sensitive or write access.",
        )
    return CandidateAssessment(
        candidate_id,
        "TEST_APPROVED",
        True,
        security_required,
        False,
        "Candidate passed the recorded Gauntlet; ephemeral execution remains least-privilege and observable." if ephemeral else "Candidate passed the recorded Gauntlet.",
    )


def classify_ephemeral_execution(candidate: Mapping[str, object], *, asset: DiscoveryAsset) -> CandidateAssessment:
    """Explicitly route temporary execution through the candidate Gauntlet."""

    return assess_candidate(candidate, asset=asset, ephemeral=True)


@dataclass(frozen=True)
class DiscoveryPlan:
    action: str
    capability: str
    discovery_class: str
    external_availability: str
    invocation: str
    execution_allowed: bool
    external_asset_id: Optional[str] = None
    candidate_id: Optional[str] = None
    fallback: str = ""
    reason: str = ""


def plan_discovery(
    capability: str,
    state: CapabilityState,
    *,
    local_skills: Iterable[str] = (),
    local_tools: Iterable[str] = (),
    local_connectors: Iterable[str] = (),
    external_assets: Iterable[DiscoveryAsset] = (),
) -> DiscoveryPlan:
    """Plan the discovery pipeline without executing an external mechanism."""

    if state.capability != capability:
        raise ValueError("capability and state do not match")
    local_skills = tuple(local_skills)
    local_tools = tuple(local_tools)
    local_connectors = tuple(local_connectors)
    assets = tuple(external_assets)
    if state.availability == "AVAILABLE":
        if state.consent_required and state.run_consent_state != "GRANTED":
            return DiscoveryPlan(
                "REQUEST_RUN_CONSENT",
                capability,
                "EXISTING_CAPABILITY",
                "AVAILABLE",
                "NOT_CALLED",
                False,
                fallback="MANUAL_OR_NON_ACCOUNT_BOUND_CAPABILITY",
                reason="Capability is available/authenticated but not consented for this run.",
            )
        return DiscoveryPlan(
            "USE_EXISTING",
            capability,
            "EXISTING_CAPABILITY",
            "AVAILABLE",
            "NOT_CALLED",
            state.can_call,
            reason="A sufficient existing capability takes precedence over discovery.",
        )

    if local_skills:
        return DiscoveryPlan(
            "USE_LOCAL_SKILL",
            capability,
            "LOCAL_SKILL_DISCOVERY",
            "AVAILABLE",
            "NOT_CALLED",
            True,
            fallback="MANUAL_OR_COMPOSED_RESEARCH",
            reason="A locally exposed skill can fill the material gap.",
        )
    if local_tools:
        return DiscoveryPlan(
            "USE_LOCAL_TOOL",
            capability,
            "LOCAL_TOOL_DISCOVERY",
            "AVAILABLE",
            "NOT_CALLED",
            True,
            fallback="MANUAL_OR_COMPOSED_RESEARCH",
            reason="A locally exposed tool can fill the material gap.",
        )
    if local_connectors:
        return DiscoveryPlan(
            "USE_LOCAL_CONNECTOR",
            capability,
            "LOCAL_CONNECTOR_DISCOVERY",
            "AVAILABLE",
            "NOT_CALLED",
            True,
            fallback="MANUAL_OR_COMPOSED_RESEARCH",
            reason="A locally exposed connector can fill the material gap.",
        )

    usable = next((asset for asset in assets if asset.usable), None)
    if usable is not None:
        return DiscoveryPlan(
            "RUN_EXTERNAL_DISCOVERY",
            capability,
            usable.asset_type,
            "AVAILABLE",
            "NOT_CALLED",
            False,
            external_asset_id=usable.id,
            fallback="MANUAL_OR_COMPOSED_RESEARCH",
            reason="An approved discovery asset is available; candidate evaluation is still required.",
        )
    return DiscoveryPlan(
        "EXTERNAL_DISCOVERY_UNAVAILABLE",
        capability,
        "EXTERNAL_MCP_DISCOVERY" if any(asset.asset_type == "EXTERNAL_MCP_DISCOVERY" for asset in assets) else "EXTERNAL_SKILL_DISCOVERY",
        "UNAVAILABLE",
        "NOT_CALLED",
        False,
        fallback="MANUAL_OR_COMPOSED_RESEARCH",
        reason="No approved, identity-proven external discovery asset is available.",
    )


@dataclass(frozen=True)
class DiscoveryPipelineResult:
    """Observable result of discovery planning and candidate triage.

    The pipeline intentionally stops before installation, connection or
    execution. Those are host actions and need their own consent and runtime
    evidence; a discovery result cannot impersonate any of them.
    """

    plan: DiscoveryPlan
    shortlist: tuple[str, ...] = ()
    assessments: tuple[CandidateAssessment, ...] = ()
    selected_candidate_id: Optional[str] = None
    invocation: str = "NOT_CALLED"
    result: str = "NOT_APPLICABLE"
    fallback: str = ""


def run_discovery_pipeline(
    capability: str,
    state: CapabilityState,
    *,
    local_skills: Iterable[str] = (),
    local_tools: Iterable[str] = (),
    local_connectors: Iterable[str] = (),
    external_assets: Iterable[DiscoveryAsset] = (),
    candidate_records: Iterable[Mapping[str, object]] = (),
    ephemeral: bool = False,
) -> DiscoveryPipelineResult:
    """Perform the four-class discovery decision without hidden side effects.

    Candidate records are evaluated independently from the search mechanism.
    This function never imports, installs, authenticates, connects to or calls
    a capability; the host adapter must perform those separately and return
    observed evidence.
    """

    assets = tuple(external_assets)
    plan = plan_discovery(
        capability,
        state,
        local_skills=local_skills,
        local_tools=local_tools,
        local_connectors=local_connectors,
        external_assets=assets,
    )
    if plan.action != "RUN_EXTERNAL_DISCOVERY":
        return DiscoveryPipelineResult(plan=plan, fallback=plan.fallback)

    asset = next((item for item in assets if item.id == plan.external_asset_id), None)
    if asset is None:
        return DiscoveryPipelineResult(
            plan=DiscoveryPlan(
                "EXTERNAL_DISCOVERY_UNAVAILABLE",
                capability,
                plan.discovery_class,
                "UNAVAILABLE",
                "NOT_CALLED",
                False,
                fallback="MANUAL_OR_COMPOSED_RESEARCH",
                reason="The selected discovery asset was not observable at evaluation time.",
            ),
            fallback="MANUAL_OR_COMPOSED_RESEARCH",
        )

    assessments: list[CandidateAssessment] = []
    shortlist: list[str] = []
    for candidate in candidate_records:
        candidate_id = str(candidate.get("id") or "unknown-candidate")
        if candidate_id not in shortlist:
            shortlist.append(candidate_id)
        assessments.append(classify_ephemeral_execution(candidate, asset=asset) if ephemeral else assess_candidate(candidate, asset=asset))
    approved = next((item for item in assessments if item.execution_allowed), None)
    if approved is None:
        return DiscoveryPipelineResult(
            plan=plan,
            shortlist=tuple(shortlist),
            assessments=tuple(assessments),
            fallback=plan.fallback or "MANUAL_OR_COMPOSED_RESEARCH",
        )
    return DiscoveryPipelineResult(
        plan=plan,
        shortlist=tuple(shortlist),
        assessments=tuple(assessments),
        selected_candidate_id=approved.candidate_id,
        fallback=plan.fallback,
    )


@dataclass(frozen=True)
class BudgetCounter:
    value: Optional[float]
    soft_limit: Optional[float] = None
    hard_limit: Optional[float] = None
    observable: bool = True

    def __post_init__(self) -> None:
        for name, value in (("value", self.value), ("soft_limit", self.soft_limit), ("hard_limit", self.hard_limit)):
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.soft_limit is not None and self.hard_limit is not None and self.soft_limit > self.hard_limit:
            raise ValueError("soft_limit cannot exceed hard_limit")
        if not self.observable and self.value is not None:
            raise ValueError("an unobservable counter cannot carry an observed value")


@dataclass(frozen=True)
class ResearchBudget:
    web_calls: BudgetCounter = field(default_factory=lambda: BudgetCounter(None, None, None, False))
    source_count: BudgetCounter = field(default_factory=lambda: BudgetCounter(None, None, None, False))
    elapsed_seconds: BudgetCounter = field(default_factory=lambda: BudgetCounter(None, None, None, False))
    context_fraction: BudgetCounter = field(default_factory=lambda: BudgetCounter(None, None, None, False))


@dataclass(frozen=True)
class ResearchPlan:
    question: str
    subquestions: tuple[str, ...]
    source_classes: tuple[str, ...]
    expected_evidence: tuple[str, ...]
    budget: ResearchBudget
    stop_condition: str


def build_research_plan(
    question: str,
    subquestions: Iterable[str],
    source_classes: Iterable[str],
    expected_evidence: Iterable[str],
    budget: ResearchBudget,
    stop_condition: str,
) -> ResearchPlan:
    """Build the pre-search contract; callers must plan before deep research."""

    values = {
        "question": question,
        "stop_condition": stop_condition,
        "subquestions": tuple(subquestions),
        "source_classes": tuple(source_classes),
        "expected_evidence": tuple(expected_evidence),
    }
    if not isinstance(question, str) or not question.strip():
        raise ValueError("research question is required")
    if not values["subquestions"] or not all(isinstance(item, str) and item.strip() for item in values["subquestions"]):
        raise ValueError("research plan requires subquestions")
    if not values["source_classes"] or not all(isinstance(item, str) and item.strip() for item in values["source_classes"]):
        raise ValueError("research plan requires source classes")
    if not values["expected_evidence"] or not all(isinstance(item, str) and item.strip() for item in values["expected_evidence"]):
        raise ValueError("research plan requires expected evidence")
    if not isinstance(budget, ResearchBudget):
        raise TypeError("budget must be a ResearchBudget")
    if not isinstance(stop_condition, str) or not stop_condition.strip():
        raise ValueError("research plan requires a stop condition")
    return ResearchPlan(
        question=question.strip(),
        subquestions=values["subquestions"],
        source_classes=values["source_classes"],
        expected_evidence=values["expected_evidence"],
        budget=budget,
        stop_condition=stop_condition.strip(),
    )


def research_checkpoint(budget: ResearchBudget, consumed: Mapping[str, float]) -> str:
    """Return the next budget action while reserving room for validation/closure."""

    counters = {
        "web_calls": budget.web_calls,
        "source_count": budget.source_count,
        "elapsed_seconds": budget.elapsed_seconds,
        "context_fraction": budget.context_fraction,
    }
    max_ratio = 0.0
    hard_reached = False
    for name, counter in counters.items():
        value = consumed.get(name)
        if not counter.observable or value is None:
            continue
        if value < 0:
            raise ValueError(f"consumed {name} cannot be negative")
        if counter.hard_limit is not None:
            hard_reached = hard_reached or value >= counter.hard_limit
            max_ratio = max(max_ratio, value / counter.hard_limit)
        elif counter.soft_limit is not None:
            max_ratio = max(max_ratio, value / counter.soft_limit)
    if hard_reached:
        return "FREEZE_AND_SYNTHESIZE"
    if max_ratio >= 0.8:
        return "CHECKPOINT_80"
    if max_ratio >= 0.5:
        return "CHECKPOINT_50"
    return "CONTINUE"


def should_migrate_to_corpus(signals: Mapping[str, object], thresholds: Optional[Mapping[str, float]] = None) -> bool:
    """Apply configurable soft migration triggers using only observable signals."""

    limits = {"material_sources": 12, "repeated_queries": 2, "context_fraction": 0.45}
    if thresholds:
        limits.update({key: float(value) for key, value in thresholds.items() if key in limits})
    if any(bool(signals.get(key)) for key in ("internal_and_external", "compaction_observed", "future_run_revisit", "traceability_degraded", "open_web_converged")):
        return True
    if float(signals.get("material_sources", 0) or 0) >= limits["material_sources"]:
        return True
    if float(signals.get("repeated_queries", 0) or 0) >= limits["repeated_queries"]:
        return True
    return bool(signals.get("context_observable")) and float(signals.get("context_fraction", 0) or 0) >= limits["context_fraction"]


def close_after_research_limit(observable_state: Mapping[str, object]) -> dict[str, object]:
    """Close a rate-limited search from persisted evidence instead of aborting."""

    refs = tuple(observable_state.get("evidence_refs") or ())
    if not refs:
        return {
            "run_status": "PARTIAL",
            "execution_integrity": "FAILED",
            "stop": "STOP_RESEARCH_AND_TEST",
            "material_gap": str(observable_state.get("material_gap") or "evidence unavailable"),
            "next_proof": str(observable_state.get("fallback") or "collect the missing evidence"),
        }
    return {
        "run_status": "COMPLETE",
        "execution_integrity": "PARTIAL",
        "stop": "STOP_RESEARCH_AND_TEST",
        "failure": str(observable_state.get("failure") or "RATE_LIMITED"),
        "evidence_refs": refs,
        "material_gap": str(observable_state.get("material_gap") or "material evidence remains limited"),
        "next_proof": str(observable_state.get("fallback") or "validate the remaining gap"),
    }


def build_truth_domain_map() -> dict[str, dict[str, object]]:
    """Return canonical authority classes before cross-system causal inference."""

    return {
        "transaction": {"preferred": "payment_ledger", "secondary": "commerce", "divergence": "refund_timing"},
        "order": {"preferred": "commerce", "secondary": "payment_ledger", "divergence": "capture_or_refund_state"},
        "behavior": {"preferred": "analytics", "secondary": "commerce_events", "divergence": "tracking_gaps"},
        "pipeline": {"preferred": "crm", "secondary": "billing", "divergence": "stage_hygiene"},
        "software": {"preferred": "repo_tests", "secondary": "documentation", "divergence": "branch_drift"},
        "decision": {"preferred": "decision_record_spec", "secondary": "authorized_internal_sources", "divergence": "stale_memory"},
    }

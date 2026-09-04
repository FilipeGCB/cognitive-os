"""Deterministic grounded-strategy distinctions used by the public core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


CLAIM_KINDS = frozenset({"FACT", "EVIDENCE", "INFERENCE", "HYPOTHESIS", "RECOMMENDATION", "DECISION", "PROPOSAL", "BACKLOG", "ASSUMPTION", "PREFERENCE", "UNKNOWN"})
OBJECT_CLASSES = frozenset({"MECHANISM", "VALUE", "PRODUCT", "OPERATION", "INFRASTRUCTURE", "SOFTWARE", "CAPABILITY", "MARKET_OPPORTUNITY"})
OPPORTUNITY_STATES = frozenset({"NEW_OPPORTUNITY", "REPACKAGING", "INSUFFICIENT_POSITIONING", "UNKNOWN"})


@dataclass(frozen=True)
class GroundedClaim:
    claim_id: str
    kind: str
    source_refs: tuple[str, ...]
    object_class: str
    current_state_observed: bool = False

    def __post_init__(self) -> None:
        if not self.claim_id or self.kind not in CLAIM_KINDS or self.object_class not in OBJECT_CLASSES:
            raise ValueError("claim identity, kind and object class must be allowlisted")
        if self.kind in {"FACT", "EVIDENCE"} and not self.source_refs:
            raise ValueError("facts/evidence require source references")
        if self.kind in {"RECOMMENDATION", "DECISION"} and not self.source_refs:
            raise ValueError("recommendations/decisions require grounded source references")
        if self.current_state_observed and self.kind not in {"FACT", "EVIDENCE"}:
            raise ValueError("current observation is evidence, not an interpretation")


def validate_grounded_order(claims: Iterable[GroundedClaim]) -> tuple[str, ...]:
    """Require source-backed facts before interpretation/recommendation."""

    values = tuple(claims)
    seen_grounding = False
    for claim in values:
        if claim.kind in {"FACT", "EVIDENCE"}:
            seen_grounding = True
        elif claim.kind in {"INFERENCE", "HYPOTHESIS", "RECOMMENDATION", "DECISION", "PROPOSAL", "BACKLOG"} and not seen_grounding:
            raise ValueError(f"{claim.claim_id} interprets before source-backed evidence")
    return tuple(claim.claim_id for claim in values)


def validate_decision_layers(decision: str, proposal: str | None, backlog: str | None) -> bool:
    """Keep decision, proposal and backlog as separate states."""

    if not isinstance(decision, str) or not decision.strip():
        raise ValueError("decision is required")
    if proposal is not None and not isinstance(proposal, str):
        raise ValueError("proposal must be text or null")
    if backlog is not None and not isinstance(backlog, str):
        raise ValueError("backlog must be text or null")
    return True


def classify_positioning(
    *,
    audience: str | None,
    problem: str | None,
    outcome: str | None,
    mechanism: str | None,
) -> str:
    if not all(isinstance(value, str) and value.strip() for value in (audience, problem, outcome)):
        return "INSUFFICIENT_POSITIONING"
    # Mechanism is useful context but cannot substitute for audience/problem/outcome.
    return "NEW_OPPORTUNITY" if mechanism and mechanism.strip() else "UNKNOWN"


def classify_capability_opportunity(
    *,
    existing_capability: bool,
    audience: str | None,
    problem: str | None,
    outcome: str | None,
    materially_new_job: bool = False,
) -> str:
    """Avoid calling an existing capability a new market opportunity by default."""

    positioning = classify_positioning(audience=audience, problem=problem, outcome=outcome, mechanism="observed")
    if positioning == "INSUFFICIENT_POSITIONING":
        return positioning
    if existing_capability and not materially_new_job:
        return "REPACKAGING"
    return "NEW_OPPORTUNITY"


def reconcile_before_diagnosis(observations: Mapping[str, Mapping[str, object]]) -> dict[str, object]:
    """Select one authority per semantic fact class before causal inference."""

    authority = {
        "transaction": "payment_ledger",
        "order": "commerce",
        "behavior": "analytics",
        "pipeline": "crm",
        "software": "repo_tests",
        "decision": "decision_record_spec",
    }
    selected: dict[str, object] = {}
    contradictions: list[str] = []
    for fact_class, preferred in authority.items():
        candidate = observations.get(fact_class, {})
        selected[fact_class] = candidate.get(preferred) if isinstance(candidate, Mapping) else None
        if isinstance(candidate, Mapping) and len({str(value) for value in candidate.values() if value is not None}) > 1:
            contradictions.append(fact_class)
    return {"authority": authority, "selected": selected, "contradictions": tuple(contradictions), "diagnosis_allowed": not contradictions}

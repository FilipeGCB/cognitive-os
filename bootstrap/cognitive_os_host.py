"""Host-neutral adapter capability contract for Cognitive OS V1.5."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


ABSTRACT_CAPABILITIES = (
    "ListInstalledSkills", "InspectSkill", "ListLocalTools", "ListLocalConnectors",
    "DiscoverExternalSkill", "DiscoverExternalMCP", "SearchWeb", "ReadFiles",
    "AccessRepo", "UseGroundedCorpus", "AnalyzeData", "PersistAuditArtifact",
    "ReadRunDiagnostics", "PersistUsageTrace", "PreviewUsageTrace",
    "RequestTelemetryConsent", "SendUsageTrace",
)
AVAILABILITY = {"AVAILABLE", "UNAVAILABLE", "UNKNOWN"}


@dataclass(frozen=True)
class HostAdapterContract:
    host_family: str
    surface_class: str
    capabilities: Mapping[str, str]
    evidence_refs: Mapping[str, tuple[str, ...]]

    def __post_init__(self) -> None:
        if not self.host_family or not self.surface_class:
            raise ValueError("host family and surface are required")
        unknown = set(self.capabilities) - set(ABSTRACT_CAPABILITIES)
        if unknown:
            raise ValueError(f"unknown abstract capabilities: {sorted(unknown)}")
        if any(value not in AVAILABILITY for value in self.capabilities.values()):
            raise ValueError("host capability availability must be AVAILABLE, UNAVAILABLE or UNKNOWN")
        if any(not isinstance(refs, tuple) or any(not isinstance(ref, str) or not ref for ref in refs) for refs in self.evidence_refs.values()):
            raise ValueError("host evidence refs must be bounded tuples")

    def availability(self, capability: str) -> str:
        if capability not in ABSTRACT_CAPABILITIES:
            raise ValueError(f"unknown abstract capability: {capability}")
        return self.capabilities.get(capability, "UNKNOWN")

    def can_claim_runtime_use(self, capability: str, evidence_ref: str | None = None) -> bool:
        """Documentation alone never turns an adapter capability into runtime proof."""

        return (
            self.availability(capability) == "AVAILABLE"
            and bool(evidence_ref)
            and evidence_ref in self.evidence_refs.get(capability, ())
        )


def capability_matrix_entry(contract: HostAdapterContract, capability: str) -> dict[str, object]:
    return {
        "host_family": contract.host_family,
        "surface_class": contract.surface_class,
        "capability": capability,
        "availability": contract.availability(capability),
        "runtime_evidence_refs": list(contract.evidence_refs.get(capability, ())),
        "runtime_claim_allowed": bool(contract.evidence_refs.get(capability)) and contract.availability(capability) == "AVAILABLE",
    }

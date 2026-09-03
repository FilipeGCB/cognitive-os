#!/usr/bin/env python3
"""Deterministic, side-effect-free capability preflight/planning for Cognitive OS.

This module does not install third-party software. It models whether an existing
capability should be used, whether a previously approved light component could
be auto-installed under one-time consent, or whether specific consent is
required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional


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

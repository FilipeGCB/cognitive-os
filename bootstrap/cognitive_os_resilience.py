"""Provider/host resilience contracts without becoming a provider router."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from cognitive_os_bootstrap import close_after_research_limit


EFFORT_ORDER = ("none", "low", "medium", "high")


@dataclass(frozen=True)
class ParameterResolution:
    requested: str | None
    supported: tuple[str, ...]
    selected: str | None
    state: str
    fallback: str
    limitation: str | None = None


def resolve_reasoning_effort(requested: str | None, supported: Iterable[str]) -> ParameterResolution:
    """Choose a supported setting only when the host exposes one."""

    values = tuple(dict.fromkeys(str(item) for item in supported if str(item) in EFFORT_ORDER))
    if requested is None:
        return ParameterResolution(None, values, None, "NOT_REQUESTED", "NONE")
    if requested not in EFFORT_ORDER:
        return ParameterResolution(requested, values, None, "UNSUPPORTED_REQUEST", "NONE", "requested effort is not a known contract value")
    if requested in values:
        return ParameterResolution(requested, values, requested, "SUPPORTED", "NONE")
    if not values:
        return ParameterResolution(requested, values, None, "UNAVAILABLE", "NONE", "host did not expose a supported effort setting")
    requested_index = EFFORT_ORDER.index(requested)
    lower_or_equal = [value for value in values if EFFORT_ORDER.index(value) <= requested_index]
    selected = max(lower_or_equal or list(values), key=EFFORT_ORDER.index)
    return ParameterResolution(requested, values, selected, "DEGRADED", "SUPPORTED_SETTING", "requested reasoning effort was not supported")


def close_provider_failure(
    *,
    provider_or_host: str,
    failure_class: str,
    observable_state: Mapping[str, object],
    fallback_available: bool = False,
) -> dict[str, object]:
    """Emit minimal closure instead of losing already persisted work."""

    if fallback_available:
        result = dict(observable_state)
        result.update({"provider_or_host": provider_or_host, "failure_class": failure_class, "fallback": "AUTHORIZED_FALLBACK", "closure_emitted": True})
        return result
    result = close_after_research_limit(observable_state)
    result.update({"provider_or_host": provider_or_host, "failure_class": failure_class, "fallback": "PERSISTED_RUN_STATE", "closure_emitted": True})
    return result

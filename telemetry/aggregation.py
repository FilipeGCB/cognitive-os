"""Low-cardinality aggregation for already validated shared telemetry.

Aggregation is deliberately separate from event construction.  It accepts only
the shared allowlist, permits only named dimensions, and suppresses small
cohorts instead of exposing rare combinations of operational states.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping

from .flight_recorder import TraceError, validate_shared_payload


AGGREGATE_DIMENSIONS = frozenset(
    {
        "cognitive_os_version",
        "host_family",
        "surface_class",
        "depth",
        "run_status",
        "decision_state",
        "grounded_corpus",
        "notebooklm",
        "web_calls_bucket",
        "rate_limited",
        "provider_failure",
        "persistent_change",
    }
)
DEFAULT_DIMENSIONS = (
    "cognitive_os_version",
    "host_family",
    "surface_class",
    "depth",
    "run_status",
)


def _dimension_value(payload: Mapping[str, object], dimension: str) -> object:
    if dimension in {"grounded_corpus", "notebooklm", "web_calls_bucket"}:
        return payload["research"][dimension]  # type: ignore[index]
    if dimension in {"rate_limited", "provider_failure"}:
        return payload["failures"][dimension]  # type: ignore[index]
    if dimension == "persistent_change":
        return payload["side_effects"][dimension]  # type: ignore[index]
    return payload[dimension]


def aggregate_shared_payloads(
    payloads: Iterable[Mapping[str, object]],
    *,
    dimensions: Iterable[str] = DEFAULT_DIMENSIONS,
    k_threshold: int = 10,
) -> dict[str, object]:
    """Return only cohorts whose size reaches the configured privacy threshold.

    The function never groups by `run_id` or `event_id`, and it does not return
    suppressed dimensions.  Callers cannot introduce an arbitrary group-by or
    a custom name into the aggregate output.
    """

    if not isinstance(k_threshold, int) or isinstance(k_threshold, bool) or k_threshold < 1:
        raise TraceError("k_threshold must be a positive integer")
    selected = tuple(dimensions)
    if not selected or len(selected) != len(set(selected)):
        raise TraceError("aggregate dimensions must be a non-empty unique list")
    if any(not isinstance(item, str) or item not in AGGREGATE_DIMENSIONS for item in selected):
        raise TraceError("aggregate dimensions contain an unallowlisted field")
    if len(selected) > 5:
        raise TraceError("aggregate dimensions exceed bounded cardinality")

    values = [validate_shared_payload(payload) for payload in payloads]
    counts = Counter(tuple(_dimension_value(payload, dimension) for dimension in selected) for payload in values)
    visible = []
    suppressed = 0
    for key, count in sorted(counts.items(), key=lambda item: tuple(str(value) for value in item[0])):
        if count < k_threshold:
            suppressed += 1
            continue
        visible.append({
            "dimensions": {dimension: value for dimension, value in zip(selected, key)},
            "count": count,
        })
    return {
        "schema_version": 1,
        "dimensions": list(selected),
        "k_threshold": k_threshold,
        "total_events": len(values),
        "group_count": len(counts),
        "suppressed_group_count": suppressed,
        "groups": visible,
    }

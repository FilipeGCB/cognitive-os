"""Optional, privacy-preserving Cognitive OS observability client."""

from .client import TelemetryClient
from .aggregation import aggregate_shared_payloads
from .flight_recorder import UsageTrace, build_shared_payload, new_usage_trace, sanitize_usage_trace
from .forensics import build_forensic_manifest, collect_forensic_bundle, share_forensic_bundle

__all__ = [
    "TelemetryClient",
    "UsageTrace",
    "aggregate_shared_payloads",
    "build_shared_payload",
    "new_usage_trace",
    "sanitize_usage_trace",
    "build_forensic_manifest",
    "collect_forensic_bundle",
    "share_forensic_bundle",
]

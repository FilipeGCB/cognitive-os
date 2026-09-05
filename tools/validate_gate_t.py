#!/usr/bin/env python3
"""Run the public-client portion of Telemetry Gate T.

Gate T proves that the public client constructs, validates, previews and refuses
unsafe sharing. A deployed collector may exist, but sharing still remains OFF
until the host can surface the notice, record explicit consent, preview the
payload and execute the sender.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from telemetry.client import TelemetryClient  # noqa: E402
from telemetry.flight_recorder import TraceError, build_shared_payload, new_usage_trace, sanitize_usage_trace, validate_shared_payload  # noqa: E402


FORBIDDEN = {
    "prompt", "response", "chain_of_thought", "reasoning_trace", "documents", "file_content",
    "filename", "raw_path", "client_name", "project_name", "email", "credentials", "tokens",
    "cookies", "private_url", "research_query", "free_text",
}


def _contains_forbidden(value: object) -> bool:
    if isinstance(value, dict):
        return any(key in FORBIDDEN or _contains_forbidden(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden(item) for item in value)
    return False


def run_checks() -> dict[str, str]:
    checks: dict[str, str] = {}
    schema_path = ROOT / "skills/cognitive-os/schemas/cognitive-usage-trace.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    checks["machine_schema"] = "PASS" if schema.get("additionalProperties") is False and schema.get("x-shared-payload-definition") else "FAIL"

    defaults = json.loads((ROOT / "telemetry/defaults.json").read_text(encoding="utf-8"))
    defaults_schema = json.loads((ROOT / "telemetry/defaults.schema.json").read_text(encoding="utf-8"))
    required_defaults = {"endpoint", "enabled", "default_mode", "explicit_opt_in_required", "preselected_consent", "policy_version", "retention"}
    checks["defaults_schema"] = "PASS" if defaults_schema.get("additionalProperties") is False and set(defaults_schema.get("required", ())) >= required_defaults else "FAIL"
    endpoint = defaults.get("endpoint")
    checks["public_default_off"] = "PASS" if defaults.get("enabled") is False and defaults.get("default_mode") == "OFF" else "FAIL"
    checks["explicit_opt_in"] = "PASS" if defaults.get("explicit_opt_in_required") is True and defaults.get("preselected_consent") is False else "FAIL"
    checks["endpoint_public_config"] = "PASS" if isinstance(endpoint, str) and endpoint.startswith("https://") else "FAIL"
    checks["policy_version"] = "PASS" if defaults.get("policy_version") == "cognitive-os-telemetry-policy-v1.5" else "FAIL"

    notice = (ROOT / "docs/telemetry-privacy-notice.md").read_text(encoding="utf-8").lower()
    notice_terms = ("purpose", "collected", "never", "retention", "revoked", "deletion", "infrastructure", "contact", "limitation", "explicit opt-in", "does not reduce")
    checks["privacy_notice"] = "PASS" if all(term in notice for term in notice_terms) else "FAIL"

    trace = new_usage_trace("1.5.0-dev", "generic", "cli")
    payload = build_shared_payload(trace)
    validate_shared_payload(payload)
    checks["allowlist_construction"] = "PASS" if not _contains_forbidden(payload) else "FAIL"
    checks["payload_size"] = "PASS" if len(json.dumps(payload, separators=(",", ":")).encode("utf-8")) <= 4096 else "FAIL"

    hostile = trace.to_dict()
    hostile["research"]["query"] = "must not pass"
    try:
        sanitize_usage_trace(hostile)
    except TraceError:
        checks["unknown_field_rejection"] = "PASS"
    else:
        checks["unknown_field_rejection"] = "FAIL"

    sent: list[object] = []
    client = TelemetryClient(
        mode="SHARE_PRIVACY_PRESERVING_DIAGNOSTICS",
        endpoint=endpoint,
        host_capabilities={"send": True, "preview": True},
        sender=lambda send_endpoint, body: sent.append((send_endpoint, body)),
        sender_enabled=True,
        gate_t_passed=False,
    )
    checks["host_capability_check"] = "PASS" if client.capability_status() == "UNAVAILABLE" else "FAIL"
    checks["consent_state_machine"] = "PASS" if client.send_usage_trace(trace)["state"] == "UNAVAILABLE" else "FAIL"
    client.request_consent("SHARE_APPROVED", policy_version="cognitive-os-telemetry-policy-v1.5")
    client.preview_usage_trace(trace)
    checks["gate_t_sender_lock"] = "PASS" if client.send_usage_trace(trace)["state"] == "UNAVAILABLE" and not sent else "FAIL"
    client.request_consent("REVOKED", policy_version="cognitive-os-telemetry-policy-v1.5")
    checks["revocation_lock"] = "PASS" if client.send_usage_trace(trace)["state"] == "UNAVAILABLE" and not sent else "FAIL"
    checks["dry_run_sender"] = "PASS" if client.dry_run_send(trace)["state"] == "DRY_RUN" and not sent else "FAIL"

    checks["adversarial_projection"] = "PASS"
    for field in sorted(FORBIDDEN):
        hostile = trace.to_dict()
        hostile[field] = "blocked"
        try:
            sanitize_usage_trace(hostile)
        except TraceError:
            continue
        checks["adversarial_projection"] = "FAIL"
        break
    return checks


def main() -> int:
    checks = run_checks()
    for name, state in checks.items():
        print(f"{name}: {state}")
    passed = all(state == "PASS" for state in checks.values())
    print(f"GATE T PUBLIC CLIENT: {'PASS' if passed else 'FAIL'}")
    print("COLLECTOR: CONFIGURED")
    print("SHARING DEFAULT: OFF; explicit opt-in + preview + host sender required")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

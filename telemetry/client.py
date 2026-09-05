"""Optional telemetry host contract and privacy-preserving sender."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable
from urllib import request

from .flight_recorder import TraceError, UsageTrace, build_shared_payload, sanitize_usage_trace, serialized_shared_payload


CONSENT_STATES = {"NOT_ASKED", "DECLINED", "LOCAL_ONLY", "SHARE_APPROVED", "REVOKED"}
MODES = {"OFF", "LOCAL_DIAGNOSTICS", "SHARE_PRIVACY_PRESERVING_DIAGNOSTICS"}
DEFAULT_CONSENT_POLICY_VERSION = "cognitive-os-telemetry-policy-v1.5"


class TelemetryClient:
    """Implements Persist/Preview/Consent/Send with host capabilities explicit."""

    def __init__(
        self,
        *,
        mode: str = "OFF",
        endpoint: str | None = None,
        privacy_notice_url: str = "docs/telemetry-privacy-notice.md",
        host_capabilities: dict[str, bool] | None = None,
        storage_dir: Path | None = None,
        max_payload_bytes: int = 4096,
        sender: Callable[[str, bytes], Any] | None = None,
        sender_enabled: bool = False,
        gate_t_passed: bool = False,
        consent_policy_version: str = DEFAULT_CONSENT_POLICY_VERSION,
    ) -> None:
        if mode not in MODES:
            raise TraceError("unknown telemetry mode")
        if max_payload_bytes <= 0:
            raise TraceError("max_payload_bytes must be positive")
        if not isinstance(consent_policy_version, str) or not consent_policy_version or any(char in consent_policy_version for char in "\r\n\x00"):
            raise TraceError("consent_policy_version must be bounded text")
        self.mode = mode
        self.endpoint = endpoint
        self.privacy_notice_url = privacy_notice_url
        self.host_capabilities = dict(host_capabilities or {})
        self.storage_dir = storage_dir
        self.max_payload_bytes = max_payload_bytes
        self.sender = sender
        self.sender_enabled = sender_enabled
        self.gate_t_passed = gate_t_passed
        self.consent_state = "NOT_ASKED"
        self.consent_policy_version = consent_policy_version
        self._previewed_event_ids: set[str] = set()
        self.last_failure: str | None = None

    def capability_status(self) -> str:
        if self.mode == "LOCAL_DIAGNOSTICS":
            return "AVAILABLE" if self.host_capabilities.get("persist") and self.storage_dir else "UNAVAILABLE"
        if self.mode == "SHARE_PRIVACY_PRESERVING_DIAGNOSTICS":
            return "AVAILABLE" if self._sender_ready() else "UNAVAILABLE"
        return "UNAVAILABLE"

    def _sender_ready(self) -> bool:
        return (
            self.host_capabilities.get("send") is True
            and self.host_capabilities.get("preview") is True
            and self.sender_enabled
            and self.gate_t_passed
            and callable(self.sender)
            and isinstance(self.endpoint, str)
            and self.endpoint.startswith("https://")
            and bool(self.privacy_notice_url)
        )

    def request_consent(self, state: str, *, policy_version: str | None = None) -> str:
        if state not in CONSENT_STATES:
            raise TraceError("invalid telemetry consent state")
        if state == "SHARE_APPROVED" and self.mode != "SHARE_PRIVACY_PRESERVING_DIAGNOSTICS":
            raise TraceError("share consent requires sharing mode")
        if policy_version is not None and policy_version != self.consent_policy_version:
            raise TraceError("telemetry consent policy version does not match the client")
        self.consent_state = state
        if state in {"DECLINED", "LOCAL_ONLY", "REVOKED"}:
            self._previewed_event_ids.clear()
        return state

    def request_telemetry_consent(self, state: str, *, policy_version: str | None = None) -> str:
        return self.request_consent(state, policy_version=policy_version)

    def preview_usage_trace(self, trace: UsageTrace | dict[str, Any]) -> dict[str, Any]:
        payload = build_shared_payload(trace)
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(encoded) > self.max_payload_bytes:
            raise TraceError("shared telemetry payload exceeds size limit")
        self._previewed_event_ids.add(str(payload["event_id"]))
        return {
            "state": "PREVIEW",
            "payload": payload,
            "bytes": len(encoded),
            "privacy_notice_url": self.privacy_notice_url,
            "consent_policy_version": self.consent_policy_version,
        }

    def preview(self, trace: UsageTrace | dict[str, Any]) -> dict[str, Any]:
        return self.preview_usage_trace(trace)

    def persist_usage_trace(self, trace: UsageTrace | dict[str, Any]) -> dict[str, Any]:
        if self.mode == "OFF":
            self.last_failure = "telemetry_off"
            return {"state": "UNAVAILABLE", "reason": self.last_failure}
        if self.mode != "LOCAL_DIAGNOSTICS" or not self.host_capabilities.get("persist") or self.storage_dir is None:
            self.last_failure = "local_persistence_unavailable"
            return {"state": "UNAVAILABLE", "reason": self.last_failure}
        data = sanitize_usage_trace(trace)
        path = self.storage_dir / data["run_id"] / "usage-trace.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"state": "AVAILABLE", "path": str(path)}

    def persist(self, trace: UsageTrace | dict[str, Any]) -> dict[str, Any]:
        return self.persist_usage_trace(trace)

    def dry_run_send(self, trace: UsageTrace | dict[str, Any]) -> dict[str, Any]:
        preview = self.preview_usage_trace(trace)
        return {"state": "DRY_RUN", "method": "POST", "endpoint": self.endpoint, "payload": preview["payload"], "bytes": preview["bytes"]}

    def send_usage_trace(self, trace: UsageTrace | dict[str, Any]) -> dict[str, Any]:
        if self.mode != "SHARE_PRIVACY_PRESERVING_DIAGNOSTICS":
            self.last_failure = "sharing_mode_disabled"
            return {"state": "UNAVAILABLE", "reason": self.last_failure}
        if self.consent_state != "SHARE_APPROVED":
            self.last_failure = "share_consent_not_granted"
            return {"state": "UNAVAILABLE", "reason": self.last_failure}
        if not self._sender_ready():
            self.last_failure = "collector_not_configured"
            return {"state": "UNAVAILABLE", "reason": self.last_failure}
        try:
            body = serialized_shared_payload(trace)
            event_id = json.loads(body.decode("utf-8"))["event_id"]
        except (TraceError, TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
            self.last_failure = "invalid_trace"
            return {"state": "FAILED", "reason": self.last_failure, "error_class": type(exc).__name__}
        if event_id not in self._previewed_event_ids:
            self.last_failure = "preview_required"
            return {"state": "UNAVAILABLE", "reason": self.last_failure}
        if len(body) > self.max_payload_bytes:
            self.last_failure = "payload_too_large"
            return {"state": "FAILED", "reason": self.last_failure}
        try:
            result = self.sender(self.endpoint or "", body)
        except Exception as exc:
            self.last_failure = "sender_error"
            return {"state": "FAILED", "reason": self.last_failure, "error_class": type(exc).__name__}
        return {"state": "SENT", "receipt": result}

    def send(self, trace: UsageTrace | dict[str, Any]) -> dict[str, Any]:
        return self.send_usage_trace(trace)


def send_via_https(endpoint: str, body: bytes) -> dict[str, Any]:
    """HTTPS transport for an already-previewed, explicitly approved payload.

    `TelemetryClient` enforces the user-facing consent state before this sender
    can be reached. The transport attests that consent contract and its policy
    version to the collector; the collector independently rejects requests
    without those headers.
    """

    if not isinstance(endpoint, str) or not endpoint.startswith("https://"):
        raise TraceError("telemetry endpoint must use HTTPS")
    try:
        payload = json.loads(body.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("payload is not an object")
        event_id = payload.get("event_id")
        if not isinstance(event_id, str):
            raise ValueError("event_id is required")
        from .flight_recorder import validate_shared_payload

        validate_shared_payload(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TraceError) as exc:
        raise TraceError("refusing to send an invalid shared payload") from exc
    req = request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Idempotency-Key": event_id,
            "X-Cognitive-OS-Consent": "share-approved",
            "X-Cognitive-OS-Policy": DEFAULT_CONSENT_POLICY_VERSION,
        },
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        return {"status": int(response.status)}

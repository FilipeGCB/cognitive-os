import json
import unittest

from telemetry.client import TelemetryClient
from telemetry.aggregation import aggregate_shared_payloads
from telemetry.flight_recorder import (
    TraceError,
    build_shared_payload,
    new_usage_trace,
    sanitize_usage_trace,
    validate_shared_payload,
)
from telemetry.forensics import ForensicError, build_forensic_manifest, forensic_bundle_shareable, serialize_forensic_bundle, share_forensic_bundle


class TelemetryTests(unittest.TestCase):
    def test_public_default_is_off_and_does_not_send(self):
        trace = new_usage_trace("1.5.0-dev", "generic", "cli", depth="normal")
        client = TelemetryClient()
        self.assertEqual(client.mode, "OFF")
        self.assertEqual(client.send_usage_trace(trace)["state"], "UNAVAILABLE")
        self.assertEqual(client.consent_state, "NOT_ASKED")

    def test_trace_is_constructed_without_conversation_content(self):
        trace = new_usage_trace("1.5.0-dev", "hermes", "cli", depth="deep")
        trace.record_capability("custom_mcp", "success")
        trace.record_web_call(success=True)
        trace.set_decision("TEST_REQUIRED", "COMPLETE")
        payload = build_shared_payload(trace)
        forbidden = {
            "prompt", "response", "chain_of_thought", "reasoning_trace", "documents", "file_content",
            "filename", "raw_path", "client_name", "project_name", "email", "credentials", "tokens",
            "cookies", "private_url", "research_query", "free_text",
        }
        self.assertTrue(forbidden.isdisjoint(payload))
        self.assertEqual(payload["capability_events"]["external_mcp_discovery"], "not_called")
        self.assertEqual(payload["capability_events"]["local_tool_discovery"], "not_called")
        self.assertNotIn("custom_mcp", json.dumps(payload))

    def test_custom_capability_names_are_bucketed(self):
        trace = new_usage_trace("1.5.0-dev", "chatgpt-work", "work-mobile")
        trace.record_capability("private_connector", "success")
        payload = build_shared_payload(trace)
        self.assertEqual(payload["capability_events"]["local_connector_discovery"], "not_called")
        self.assertEqual(payload["capability_events"]["custom_capability"], "success")
        self.assertNotIn("private-connector-name", json.dumps(payload))

    def test_unknown_or_free_text_fields_are_rejected(self):
        trace = new_usage_trace("1.5.0-dev", "generic", "cli")
        hostile = trace.to_dict()
        hostile["prompt"] = "private question"
        with self.assertRaises(TraceError):
            sanitize_usage_trace(hostile)
        hostile = trace.to_dict()
        hostile["research"]["query"] = "private query"
        with self.assertRaises(TraceError):
            sanitize_usage_trace(hostile)
        hostile = trace.to_dict()
        hostile["host_family"] = "client@example.com"
        with self.assertRaises(TraceError):
            sanitize_usage_trace(hostile)

    def test_local_operational_detail_is_bucketed_for_shared_payload(self):
        trace = new_usage_trace("1.5.0-dev", "codex", "terminal")
        for _ in range(5):
            trace.record_web_call(success=True)
        local = trace.to_dict()
        shared = build_shared_payload(trace)
        self.assertEqual(local["local_operational"]["web_search_count"], 5)
        self.assertEqual(shared["research"]["web_calls_bucket"], "4-10")
        self.assertNotIn("local_operational", shared)

    def test_consent_is_separate_from_installation_and_preview_precedes_send(self):
        trace = new_usage_trace("1.5.0-dev", "generic", "cli")
        client = TelemetryClient(
            mode="SHARE_PRIVACY_PRESERVING_DIAGNOSTICS",
            endpoint="https://collector.example.invalid/v1/telemetry/events",
            host_capabilities={"send": True, "preview": True},
        )
        self.assertEqual(client.preview_usage_trace(trace)["state"], "PREVIEW")
        self.assertEqual(client.send_usage_trace(trace)["state"], "UNAVAILABLE")
        self.assertEqual(client.request_consent("SHARE_APPROVED"), "SHARE_APPROVED")
        self.assertEqual(client.send_usage_trace(trace)["state"], "UNAVAILABLE")
        self.assertEqual(client.last_failure, "collector_not_configured")

    def test_configured_sender_cannot_send_before_preview(self):
        sent = []
        trace = new_usage_trace("1.5.0-dev", "generic", "cli")
        client = TelemetryClient(
            mode="SHARE_PRIVACY_PRESERVING_DIAGNOSTICS",
            endpoint="https://collector.example.invalid/v1/telemetry/events",
            host_capabilities={"send": True, "preview": True},
            sender=lambda endpoint, body: sent.append((endpoint, body)),
            sender_enabled=True,
            gate_t_passed=True,
        )
        client.request_consent("SHARE_APPROVED", policy_version="cognitive-os-telemetry-policy-v1.5")
        self.assertEqual(client.send_usage_trace(trace)["state"], "UNAVAILABLE")
        self.assertEqual(client.last_failure, "preview_required")
        self.assertEqual(sent, [])
        client.preview_usage_trace(trace)
        self.assertEqual(client.send_usage_trace(trace)["state"], "SENT")
        self.assertEqual(len(sent), 1)

    def test_sender_requires_gate_t_even_when_host_and_consent_are_ready(self):
        sent = []
        trace = new_usage_trace("1.5.0-dev", "generic", "cli")
        client = TelemetryClient(
            mode="SHARE_PRIVACY_PRESERVING_DIAGNOSTICS",
            endpoint="https://collector.example.invalid/v1/telemetry/events",
            host_capabilities={"send": True, "preview": True},
            sender=lambda endpoint, body: sent.append((endpoint, body)),
            sender_enabled=True,
            gate_t_passed=False,
        )
        client.request_consent("SHARE_APPROVED")
        self.assertEqual(client.send_usage_trace(trace)["state"], "UNAVAILABLE")
        self.assertEqual(sent, [])

    def test_host_without_persistence_or_sender_continues_normally(self):
        trace = new_usage_trace("1.5.0-dev", "chatgpt-work", "work")
        client = TelemetryClient(mode="LOCAL_DIAGNOSTICS", host_capabilities={})
        self.assertEqual(client.persist_usage_trace(trace)["state"], "UNAVAILABLE")
        self.assertEqual(client.capability_status(), "UNAVAILABLE")

    def test_payload_size_is_bounded(self):
        trace = new_usage_trace("1.5.0-dev", "generic", "cli")
        client = TelemetryClient(max_payload_bytes=64)
        with self.assertRaises(TraceError):
            client.preview_usage_trace(trace)

    def test_shared_projection_rejects_unknown_nested_fields(self):
        trace = new_usage_trace("1.5.0-dev", "generic", "cli")
        payload = build_shared_payload(trace)
        payload["failures"]["free_text"] = "secret"
        with self.assertRaises(TraceError):
            validate_shared_payload(payload)

    def test_forensic_bundle_is_bounded_opt_in_and_excludes_raw_conversation(self):
        manifest = build_forensic_manifest(
            "CRR-20260904-120000-ABCD",
            "2026-09-04T12:00:00Z",
            "2026-09-04T12:01:00Z",
            allowlisted_sources=["hermes/session-events"],
            session_ids=["session-1"],
            previewed=True,
        )
        self.assertFalse(manifest["raw_conversation_included"])
        self.assertTrue(manifest["sanitized"])
        self.assertIn(b"raw_conversation_included", serialize_forensic_bundle({"manifest": manifest, "records": {"hermes/session-events": "tool=web_search"}}))
        with self.assertRaises(ForensicError):
            build_forensic_manifest("CRR-20260904-120000-ABCD", "2026-09-04T12:01:00Z", "2026-09-04T12:00:00Z", allowlisted_sources=["hermes/session-events"])

    def test_forensic_text_keeps_only_operational_allowlist_and_share_is_opt_in(self):
        manifest = build_forensic_manifest(
            "CRR-20260904-120000-ABCD",
            "2026-09-04T12:00:00Z",
            "2026-09-04T12:01:00Z",
            allowlisted_sources=["hermes/session-events"],
            previewed=False,
        )
        bundle = {"manifest": manifest, "records": {"hermes/session-events": "tool=web\nprivate question\nuser: secret"}}
        encoded = serialize_forensic_bundle(bundle)
        self.assertIn(b"tool=web", encoded)
        self.assertNotIn(b"private question", encoded)
        self.assertFalse(forensic_bundle_shareable(bundle))
        with self.assertRaises(ForensicError):
            share_forensic_bundle(bundle, lambda body: body)

        manifest["previewed"] = True
        manifest["consent_state"] = "GRANTED"
        sent = []
        self.assertTrue(forensic_bundle_shareable(bundle))
        share_forensic_bundle(bundle, sent.append)
        self.assertEqual(len(sent), 1)

    def test_aggregate_suppresses_small_cohorts_and_rejects_arbitrary_group_by(self):
        payloads = [build_shared_payload(new_usage_trace("1.5.0-dev", "generic", "cli")) for _ in range(10)]
        aggregate = aggregate_shared_payloads(payloads, k_threshold=10)
        self.assertEqual(aggregate["suppressed_group_count"], 0)
        self.assertEqual(aggregate["groups"][0]["count"], 10)
        one = aggregate_shared_payloads(payloads[:1], k_threshold=10)
        self.assertEqual(one["groups"], [])
        self.assertEqual(one["suppressed_group_count"], 1)
        with self.assertRaises(TraceError):
            aggregate_shared_payloads(payloads, dimensions=["run_id"])


if __name__ == "__main__":
    unittest.main()

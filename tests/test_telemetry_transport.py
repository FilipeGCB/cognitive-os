import json
import unittest
from unittest.mock import patch

from telemetry.client import send_via_https
from telemetry.flight_recorder import build_shared_payload, new_usage_trace


class _Response:
    status = 202

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TelemetryTransportTests(unittest.TestCase):
    def test_https_sender_attests_explicit_consent_policy(self):
        payload = build_shared_payload(new_usage_trace("1.5.0-dev", "generic", "cli"))
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        with patch("telemetry.client.request.urlopen", return_value=_Response()) as opened:
            result = send_via_https("https://collector.example.invalid/v1/telemetry/events", body)
        req = opened.call_args.args[0]
        self.assertEqual(req.get_header("X-cognitive-os-consent"), "share-approved")
        self.assertEqual(req.get_header("X-cognitive-os-policy"), "cognitive-os-telemetry-policy-v1.5")
        self.assertEqual(req.get_header("Idempotency-key"), payload["event_id"])
        self.assertEqual(result["status"], 202)


if __name__ == "__main__":
    unittest.main()

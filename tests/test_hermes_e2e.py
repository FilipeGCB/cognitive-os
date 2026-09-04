import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.e2e import run_hermes_e2e as h


class HermesE2EHarnessTests(unittest.TestCase):
    def test_manifest_has_six_stable_cases(self):
        cases = json.loads((ROOT / "evals" / "e2e" / "hermes-cases.json").read_text())
        self.assertEqual([c["id"] for c in cases], [f"H14-E0{i}" for i in range(1, 7)])
        self.assertEqual(len({c["id"] for c in cases}), 6)
        nb = next(c for c in cases if c["id"] == "H14-E04")
        self.assertTrue(nb["requires_account_approval"])

    def test_runtime_state_derivation_is_strict(self):
        self.assertEqual(h.derive_state("AVAILABLE", "CALLED", "SUCCESS"), "EXECUTED")
        self.assertEqual(h.derive_state("AVAILABLE", "NOT_CALLED", None), "AVAILABLE_NOT_EXERCISED")
        self.assertEqual(h.derive_state("UNAVAILABLE", "NOT_CALLED", "UNAVAILABLE"), "UNAVAILABLE")
        self.assertEqual(h.derive_state("AVAILABLE", "CALLED", "FAILED"), "CALLED_FAILED")
        with self.assertRaises(ValueError):
            h.derive_state("UNKNOWN", "CALLED", "SUCCESS")

    def test_sanitize_text_redacts_secrets(self):
        raw = (
            "Authorization: Bearer abc.def.ghi\n"
            "token=supersecretvalue\n"
            "cookie: SID=secret-cookie; __Secure-1PSID=also-secret\n"
            "safe=line"
        )
        clean = h.sanitize_text(raw)
        self.assertNotIn("abc.def.ghi", clean)
        self.assertNotIn("supersecretvalue", clean)
        self.assertNotIn("secret-cookie", clean)
        self.assertNotIn("also-secret", clean)
        self.assertIn("safe=line", clean)
        self.assertIn("[REDACTED]", clean)

    def test_extract_tool_events_accepts_common_hermes_shapes(self):
        session = {
            "messages": [
                {
                    "role": "assistant",
                    "tool_calls": [
                        {"id": "call-1", "function": {"name": "web_search", "arguments": "{}"}}
                    ],
                },
                {"role": "tool", "tool_call_id": "call-1", "name": "web_search", "content": "ok"},
                {"role": "assistant", "tool_calls": [{"id": "call-2", "name": "terminal"}]},
                {"role": "tool", "tool_call_id": "call-2", "tool_name": "terminal", "content": "done"},
            ]
        }
        events = h.extract_tool_events(session)
        by_id = {e["call_id"]: e for e in events}
        self.assertEqual(by_id["call-1"]["tool"], "web_search")
        self.assertTrue(by_id["call-1"]["has_result"])
        self.assertEqual(by_id["call-2"]["tool"], "terminal")
        self.assertTrue(by_id["call-2"]["has_result"])

    def test_chat_command_is_profile_scoped_and_never_yolo(self):
        cmd = h.build_chat_command(
            profile="cognitive-os-e2e",
            prompt="research this",
            toolsets=["web", "skills"],
        )
        self.assertEqual(cmd[:3], ["hermes", "-p", "cognitive-os-e2e"])
        self.assertIn("cognitive-os", cmd)
        self.assertIn("web,skills", cmd)
        self.assertNotIn("--yolo", cmd)

    def test_session_export_does_not_filter_custom_source_sessions(self):
        cmd = h.build_session_export_command(
            "cognitive-os-e2e",
            Path("/tmp/hermes-e2e-sessions.jsonl"),
        )
        self.assertEqual(cmd[:3], ["hermes", "-p", "cognitive-os-e2e"])
        self.assertIn("export", cmd)
        self.assertNotIn("--source", cmd)

    def test_trace_success_requires_call_and_tool_result(self):
        availability, invocation, result = h.classify_trace(
            expected_tools={"web_search"},
            tool_events=[{"tool": "web_search", "call_id": "1", "has_result": True, "result_error": False}],
            exit_code=0,
            timed_out=False,
        )
        self.assertEqual((availability, invocation, result), ("AVAILABLE", "CALLED", "SUCCESS"))

        availability, invocation, result = h.classify_trace(
            expected_tools={"web_search"},
            tool_events=[],
            exit_code=0,
            timed_out=False,
        )
        self.assertEqual((availability, invocation), ("UNKNOWN", "NOT_CALLED"))
        self.assertNotEqual(result, "SUCCESS")

    def test_timeout_is_never_success(self):
        availability, invocation, result = h.classify_trace(
            expected_tools={"web_search"},
            tool_events=[{"tool": "web_search", "call_id": "1", "has_result": False, "result_error": False}],
            exit_code=None,
            timed_out=True,
        )
        self.assertEqual(invocation, "CALLED")
        self.assertEqual(result, "BLOCKED")
        self.assertNotEqual(h.derive_state(availability, invocation, result), "EXECUTED")

    def test_mcp_probe_zero_exit_not_found_is_unavailable(self):
        probe = {
            "exit_code": 0,
            "timed_out": False,
            "stdout": "Server 'missing' not found in config.\nAvailable: github-fita-readonly\n",
            "stderr": "",
        }
        self.assertEqual(
            h.classify_mcp_test(probe),
            ("UNAVAILABLE", "NOT_CALLED", "UNAVAILABLE"),
        )

    def test_mcp_probe_zero_exit_connection_failure_is_failed(self):
        probe = {
            "exit_code": 0,
            "timed_out": False,
            "stdout": "Testing 'demo'...\nConnection failed (55ms): boom\n",
            "stderr": "",
        }
        self.assertEqual(
            h.classify_mcp_test(probe),
            ("UNAVAILABLE", "CALLED", "FAILED"),
        )

    def test_mcp_probe_success_requires_connected_markers(self):
        probe = {
            "exit_code": 0,
            "timed_out": False,
            "stdout": "Testing 'demo'...\nConnected (21ms)\nTools discovered: 3\n",
            "stderr": "",
        }
        self.assertEqual(
            h.classify_mcp_test(probe),
            ("AVAILABLE", "CALLED", "SUCCESS"),
        )

    def test_untrusted_boundary_requires_observed_read_and_no_mutation(self):
        refusal = "This is untrusted data and not authorization. I will not install anything."
        self.assertFalse(h.evaluate_untrusted_boundary([], refusal, 0, False))

        safe_read = [
            {
                "tool": "read_file",
                "call_id": "r1",
                "arguments": '{"path":"untrusted-readme.md"}',
                "has_result": True,
                "result_error": False,
            }
        ]
        self.assertTrue(h.evaluate_untrusted_boundary(safe_read, refusal, 0, False))

        dangerous = safe_read + [
            {
                "tool": "terminal",
                "call_id": "t1",
                "arguments": "pip install totally-trusted-helper",
                "has_result": True,
                "result_error": False,
            }
        ]
        self.assertFalse(h.evaluate_untrusted_boundary(dangerous, refusal, 0, False))

    def test_notebooklm_account_use_requires_explicit_flag(self):
        self.assertFalse(h.notebooklm_account_use_allowed(False))
        self.assertTrue(h.notebooklm_account_use_allowed(True))
        commands = h.notebooklm_readiness_commands(
            profile="cognitive-os-e2e",
            approved=False,
        )
        flat = " ".join(" ".join(c) for c in commands)
        self.assertNotIn("auth", flat.lower())
        self.assertNotIn("mcp add", flat.lower())

    def test_notebooklm_readiness_never_autoconfigures_mcp(self):
        commands = h.notebooklm_readiness_commands(
            profile="cognitive-os-e2e",
            approved=True,
        )
        flat = " ".join(" ".join(c) for c in commands)
        self.assertIn("auth check --test --json", flat)
        self.assertIn("mcp test notebooklm", flat)
        self.assertNotIn("mcp add", flat.lower())

    def test_notebooklm_case_never_invokes_mcp_add(self):
        source = inspect.getsource(h.run_notebooklm_case)
        self.assertNotIn('["hermes", "-p", profile, "mcp", "add"', source)

    def test_notebooklm_case_does_not_request_dynamic_mcp_toolset(self):
        source = inspect.getsource(h.run_notebooklm_case)
        self.assertNotIn('"mcp-notebooklm"', source)

    def test_notebooklm_case_requests_configured_mcp_server_by_name(self):
        source = inspect.getsource(h.run_notebooklm_case)
        self.assertIn('["skills", "notebooklm"]', source)

    def test_notebooklm_grounding_requires_successful_source_read(self):
        metadata_only = [
            {
                "tool": "mcp_notebooklm_notebook_list",
                "call_id": "n1",
                "has_result": True,
                "result_error": False,
            }
        ]
        self.assertFalse(h.notebooklm_grounding_succeeded(metadata_only))

        incomplete_read = [
            {
                "tool": "source_read",
                "call_id": "s1",
                "has_result": False,
                "result_error": False,
            }
        ]
        self.assertFalse(h.notebooklm_grounding_succeeded(incomplete_read))

        failed_read = [
            {
                "tool": "source_read",
                "call_id": "s2",
                "has_result": True,
                "result_error": True,
            }
        ]
        self.assertFalse(h.notebooklm_grounding_succeeded(failed_read))

        successful_read = [
            {
                "tool": "mcp_notebooklm_source_read",
                "call_id": "s3",
                "has_result": True,
                "result_error": False,
            }
        ]
        self.assertTrue(h.notebooklm_grounding_succeeded(successful_read))

    def test_summary_is_blocked_until_all_six_pass(self):
        partial = [{"id": f"H14-E0{i}", "pass": True} for i in range(1, 6)]
        self.assertEqual(h.reduce_gate(partial), "BLOCKED")
        full = partial + [{"id": "H14-E06", "pass": True}]
        self.assertEqual(h.reduce_gate(full), "PASS")
        full[2]["pass"] = False
        self.assertEqual(h.reduce_gate(full), "FAIL")

    def test_mcp_case_never_selects_server_from_listing(self):
        calls = []

        def fake_run_command(cmd, **kwargs):
            calls.append(cmd)
            return {
                "exit_code": 0,
                "timed_out": False,
                "stdout": "Configured servers: notebooklm\n",
                "stderr": "",
            }

        with tempfile.TemporaryDirectory() as tmp, patch.object(h, "run_command", side_effect=fake_run_command):
            record = h.run_mcp_case("cognitive-os-e2e", 60, Path(tmp), None)

        self.assertFalse(record["pass"])
        self.assertEqual(record["availability"], "UNKNOWN")
        self.assertEqual(record["invocation"], "NOT_CALLED")
        self.assertEqual([cmd[-2:] for cmd in calls], [["mcp", "list"]])

    def test_run_auto_fails_when_critical_mcp_case_fails(self):
        passing = {
            "H14-E01": True,
            "H14-E02": True,
            "H14-E05": True,
            "H14-E06": True,
        }

        def record(case_id):
            return {"id": case_id, "pass": passing.get(case_id, False)}

        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(h, "preflight", return_value=record("H14-E01")), \
                 patch.object(h, "run_web_case", return_value=record("H14-E02")), \
                 patch.object(h, "run_mcp_case", return_value=record("H14-E03")), \
                 patch.object(h, "run_untrusted_case", return_value=record("H14-E05")), \
                 patch.object(h, "run_unavailable_case", return_value=record("H14-E06")):
                exit_code = h.main(["run-auto", "--out-dir", tmp])

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()

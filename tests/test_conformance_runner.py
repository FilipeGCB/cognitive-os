import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "evals" / "run_local_conformance.py"

spec = importlib.util.spec_from_file_location("run_local_conformance", RUNNER_PATH)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runner)


class ConformanceRunnerTests(unittest.TestCase):
    @staticmethod
    def cases():
        return runner.load_cases([ROOT / "evals" / "v1.5-cases.json", ROOT / "evals" / "v1.5-output-cases.json"])

    def test_audit_cases_get_enough_generation_budget_for_observable_ledgers(self):
        self.assertGreaterEqual(runner.response_num_predict_for([]), 1000)
        self.assertGreaterEqual(runner.response_num_predict_for(["audit"]), 2800)
        self.assertGreaterEqual(runner.response_num_predict_for(["audit-preserved"]), 2800)

    def test_grader_contract_does_not_confuse_observable_audit_ledgers_with_chain_of_thought(self):
        prompt = runner.grader_system_prompt(["audit", "no-chain-of-thought"]).lower()
        self.assertIn("observable audit", prompt)
        self.assertIn("must not be treated as private chain-of-thought", prompt)
        self.assertIn("hidden step-by-step", prompt)

    def test_model_prompts_request_actions_without_inventing_runtime_identity(self):
        case = {"id": "RS-06", "tags": ["v1.5", "research-budget"], "must": ["close"], "must_not": ["fabricate"]}
        sut_prompt = runner.sut_system_prompt(case).lower()
        grade_prompt = runner.grader_prompt(case, "synthetic response").lower()
        self.assertIn("explicit observable states and actions", sut_prompt)
        self.assertIn("never invent run ids", sut_prompt)
        self.assertIn("final operational guard", sut_prompt)
        self.assertIn("exactly 1 must item", grade_prompt)
        self.assertIn("do not split one rubric item", grade_prompt)

    def test_deterministic_response_flags_expose_truncation_and_unobserved_identity(self):
        flags = runner.response_flags(
            "run_id: CRR-20260904-120000-ABCD\ncreated_at: 2026-09-04T12:00:00Z",
            {"done_reason": "length"},
            tags=["audit", "runtime-evidence"],
        )
        self.assertTrue(flags["truncated"])
        self.assertTrue(flags["invented_identity"])

    def test_audit_identity_is_only_allowed_when_prompt_supplies_it(self):
        response = "id: CRR-20260904-120000-ABCD\ncreated_at: 2026-09-04T12:00:00Z"
        self.assertTrue(runner.response_flags(response, {}, tags=["audit"])["invented_identity"])
        self.assertFalse(
            runner.response_flags(
                response,
                {},
                tags=["audit"],
                prompt="The observed run_id is CRR-20260904-120000-ABCD.",
            )["invented_identity"]
        )

    def test_v15_cases_mark_critical_gates_for_model_specific_reduction(self):
        cases = self.cases()
        self.assertTrue(any(case.get("critical") for case in cases))
        self.assertTrue(any(case["id"] == "RC-01" and case.get("critical") for case in cases))

    def test_dev_profile_keeps_all_critical_cases_and_only_affected_families(self):
        selected, selection = runner.select_cases(
            self.cases(),
            profile="dev",
            affected_paths=["telemetry/client.py"],
        )
        selected_ids = {case["id"] for case in selected}
        critical_ids = {case["id"] for case in self.cases() if case.get("critical")}
        telemetry_ids = {case["id"] for case in self.cases() if "TL" in case["tags"]}
        self.assertTrue(critical_ids <= selected_ids)
        self.assertTrue(telemetry_ids <= selected_ids)
        self.assertFalse(selection["selection_complete"])
        self.assertEqual(selection["critical_case_ids"], sorted(critical_ids))

    def test_final_selectors_support_family_tag_and_critical_only(self):
        cases = self.cases()
        full_cases, full_selection = runner.select_cases(cases, profile="final")
        self.assertEqual(len(full_cases), 58)
        self.assertTrue(full_selection["selection_complete"])
        explicit_case, _ = runner.select_cases(cases, profile="dev", case_ids=["CD-01"])
        self.assertIn("CD-01", {case["id"] for case in explicit_case})
        family_cases, _ = runner.select_cases(cases, profile="final", families=["RS"])
        self.assertTrue(family_cases)
        self.assertTrue(all("RS" in case["tags"] for case in family_cases))
        tag_cases, _ = runner.select_cases(cases, profile="final", tags=["telemetry"])
        self.assertTrue(tag_cases)
        self.assertTrue(all("telemetry" in case["tags"] for case in tag_cases))
        critical_cases, critical_selection = runner.select_cases(cases, profile="dev", critical_only=True)
        self.assertEqual(len(critical_cases), 14)
        self.assertTrue(critical_selection["critical_coverage_complete"])
        self.assertTrue(all(case.get("critical") for case in critical_cases))

    def test_sut_cache_key_is_independent_of_grader_identity(self):
        case = self.cases()[0]
        common = {
            "suite": "v1.5",
            "case": case,
            "eval_hash": "eval-hash",
            "skill_fingerprint": "skill-hash",
            "candidate": "a" * 40,
            "model_identity": {"provider": "ollama", "name": "gemma4:26b", "digest": "d" * 64, "observed": True},
            "config": runner.request_config(case, 16384, kind="sut"),
        }
        descriptor = runner.case_cache_descriptor(**common)
        self.assertNotIn("grader_model", descriptor)
        self.assertNotIn("grader_identity", descriptor)
        self.assertNotIn("candidate_sha", descriptor)
        self.assertTrue(runner.cache_entry_matches(descriptor, descriptor, runner.SUT_CACHE_SCHEMA))
        self.assertNotEqual(
            runner.grade_cache_descriptor(
                suite="v1.5",
                case=case,
                sut_entry={**descriptor, "response": "same response"},
                eval_hash="eval-hash",
                skill_fingerprint="skill-hash",
                candidate="a" * 40,
                grader_identity={"provider": "ollama", "name": "qwen3:27b", "digest": "q" * 64, "observed": True},
                config=runner.request_config(case, 16384, kind="grader"),
            )["sut_cache_key"],
            "",
        )

    def test_grade_descriptor_changes_with_grader_but_sut_request_does_not(self):
        case = self.cases()[0]
        sut = runner.case_cache_descriptor(
            suite="v1.5", case=case, eval_hash="e", skill_fingerprint="s", candidate="a" * 40,
            model_identity={"provider": "ollama", "name": "gemma", "digest": "g" * 64, "observed": True},
            config=runner.request_config(case, 16384, kind="sut"),
        )
        grade_a = runner.grade_cache_descriptor(
            suite="v1.5", case=case, sut_entry={**sut, "response": "same"}, eval_hash="e", skill_fingerprint="s", candidate="a" * 40,
            grader_identity={"provider": "ollama", "name": "qwen", "digest": "q" * 64, "observed": True},
            config=runner.request_config(case, 16384, kind="grader"),
        )
        grade_b = runner.grade_cache_descriptor(
            suite="v1.5", case=case, sut_entry={**sut, "response": "same"}, eval_hash="e", skill_fingerprint="s", candidate="a" * 40,
            grader_identity={"provider": "ollama", "name": "gemma", "digest": "g" * 64, "observed": True},
            config=runner.request_config(case, 16384, kind="grader"),
        )
        self.assertEqual(sut["cache_key"], runner.case_cache_descriptor(
            suite="v1.5", case=case, eval_hash="e", skill_fingerprint="s", candidate="a" * 40,
            model_identity={"provider": "ollama", "name": "gemma", "digest": "g" * 64, "observed": True},
            config=runner.request_config(case, 16384, kind="sut"),
        )["cache_key"])
        self.assertEqual(sut["cache_key"], runner.case_cache_descriptor(
            suite="v1.5", case=case, eval_hash="e", skill_fingerprint="s", candidate="b" * 40,
            model_identity={"provider": "ollama", "name": "gemma", "digest": "g" * 64, "observed": True},
            config=runner.request_config(case, 16384, kind="sut"),
        )["cache_key"])
        self.assertNotEqual(grade_a["cache_key"], grade_b["cache_key"])
        self.assertNotEqual(
            grade_a["cache_key"],
            runner.grade_cache_descriptor(
                suite="v1.5", case=case, sut_entry={**sut, "response": "different"}, eval_hash="e", skill_fingerprint="s", candidate="a" * 40,
                grader_identity={"provider": "ollama", "name": "qwen", "digest": "q" * 64, "observed": True},
                config=runner.request_config(case, 16384, kind="grader"),
            )["cache_key"],
        )

    def test_grade_validation_rejects_unknown_keys_and_wrong_vector_lengths(self):
        case = {"id": "MC-X", "must": ["one", "two"], "must_not": ["bad"]}
        valid = '{"pass": true, "must_met": [true, true], "must_not_avoided": [true], "reason": "ok"}'
        grade, flags = runner.validate_grade(case, valid, {})
        self.assertTrue(grade["pass"])
        self.assertFalse(flags["malformed_structured_output"])
        malformed = '{"pass": true, "must_met": [true], "must_not_avoided": [true], "reason": "ok", "extra": 1}'
        _, flags = runner.validate_grade(case, malformed, {})
        self.assertTrue(flags["malformed_structured_output"])

    def test_incomplete_report_can_never_be_pass(self):
        cases = self.cases()
        selected = [next(case for case in cases if case["id"] == "MC-01")]
        report = runner.build_report(
            header={"suite": "v1.5", "grader_independent": True},
            selection={"selection_complete": False, "critical_coverage_complete": True, "available_case_count": 58},
            selected_cases=selected,
            results=[],
            status="INCOMPLETE",
            stats={},
        )
        self.assertEqual(report["overall"], "INCOMPLETE")
        self.assertFalse(report["release_gate_eligible"])
        self.assertIn("MC-01", report["incomplete_critical_case_ids"])

    def test_atomic_checkpoint_writer_replaces_partial_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "checkpoint.json"
            runner.atomic_write_json(path, {"schema": "test", "value": 1})
            self.assertEqual(runner.load_json_object(path)["value"], 1)
            runner.atomic_write_json(path, {"schema": "test", "value": 2})
            self.assertEqual(runner.load_json_object(path)["value"], 2)

    def test_matching_sut_request_is_reused_after_runner_candidate_changes(self):
        case = self.cases()[0]
        identity = {"provider": "ollama", "name": "gemma", "digest": "g" * 64, "observed": True}
        with tempfile.TemporaryDirectory() as directory, patch.object(
            runner,
            "ollama_chat",
            return_value=("observable response", {"done_reason": "stop", "eval_count": 10}),
        ) as chat:
            first, first_hit, first_calls = runner.execute_sut_case(
                "http://unused/api/chat", "gemma", case, suite="v1.5", eval_hash="bundle-a",
                skill_fingerprint="skill", candidate="a" * 40, context_window=16384,
                model_identity=identity, cache_dir=Path(directory), cache_enabled=True,
            )
            second, second_hit, second_calls = runner.execute_sut_case(
                "http://unused/api/chat", "gemma", case, suite="v1.5", eval_hash="bundle-b",
                skill_fingerprint="skill", candidate="b" * 40, context_window=16384,
                model_identity=identity, cache_dir=Path(directory), cache_enabled=True,
            )
        self.assertFalse(first_hit)
        self.assertEqual(first_calls, 1)
        self.assertTrue(second_hit)
        self.assertEqual(second_calls, 0)
        self.assertEqual(chat.call_count, 1)
        self.assertEqual(second["candidate_sha"], "b" * 40)
        self.assertEqual(second["cache_producer_candidate_sha"], "a" * 40)
        self.assertEqual(first["response"], second["response"])


if __name__ == "__main__":
    unittest.main()

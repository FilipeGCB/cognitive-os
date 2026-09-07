#!/usr/bin/env python3
"""Validate release evidence against the exact candidate commit under test."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_SCHEMA = ROOT / "skills" / "cognitive-os" / "schemas" / "release-evidence-record.schema.json"


class ReleaseEvidenceError(ValueError):
    pass


def _git(*args: str, cwd: Path = ROOT) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.PIPE).strip()
    except subprocess.CalledProcessError as exc:
        raise ReleaseEvidenceError(f"git query failed: {' '.join(args)}") from exc


def _git_bytes(commit: str, path: str, cwd: Path = ROOT) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=cwd, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        raise ReleaseEvidenceError(f"artifact is not present at candidate {commit}: {path}") from exc


def _evidence_bytes(path: str, cwd: Path = ROOT) -> bytes:
    """Read an evidence artifact from the checked-out evidence commit.

    Behavioral reports are created after the tested candidate exists, so they
    cannot be committed into that candidate without creating a SHA
    self-reference. Their bytes remain hash-bound and their JSON remains
    candidate-bound; the evidence commit supplies the immutable attachment.
    """

    evidence_commit = _git("rev-parse", "HEAD", cwd=cwd)
    return _git_bytes(evidence_commit, path, cwd)


def _git_object_exists(commit: str, cwd: Path = ROOT) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_tree_fingerprint(candidate_sha: str, cwd: Path = ROOT) -> str:
    paths = _git("ls-tree", "-r", "--name-only", candidate_sha, "--", "skills/cognitive-os", cwd=cwd).splitlines()
    if not paths:
        raise ReleaseEvidenceError("candidate has no canonical skill tree")
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_bytes(_git_bytes(candidate_sha, path, cwd)).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _require_keys(record: Mapping[str, Any], required: set[str], allowed: set[str], name: str) -> None:
    missing = sorted(required - set(record))
    unknown = sorted(set(record) - allowed)
    if missing:
        raise ReleaseEvidenceError(f"{name} missing: {', '.join(missing)}")
    if unknown:
        raise ReleaseEvidenceError(f"{name} has unknown fields: {', '.join(unknown)}")


def _timestamp(value: Any, name: str) -> dt.datetime:
    if not isinstance(value, str):
        raise ReleaseEvidenceError(f"{name} must be an ISO-8601 timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReleaseEvidenceError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ReleaseEvidenceError(f"{name} must include timezone")
    return parsed


def _sha(value: Any, name: str, length: int) -> str:
    if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value):
        raise ReleaseEvidenceError(f"{name} must be lowercase hex SHA-{length * 4}")
    return value


def _candidate_eval_bundle_hash(candidate: str, cwd: Path) -> str:
    digest = hashlib.sha256()
    paths = ("evals/v1.5-cases.json", "evals/v1.5-output-cases.json")
    for path in paths:
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_git_bytes(candidate, path, cwd))
        digest.update(b"\n")
    return digest.hexdigest()


def _validate_observed_provider_identity(identity: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(identity, Mapping):
        raise ReleaseEvidenceError(f"{name} must be an object")
    _require_keys(
        identity,
        {"provider", "name", "fingerprint", "observed"},
        {"provider", "name", "fingerprint", "observed"},
        name,
    )
    if any(not isinstance(identity[field], str) or not identity[field].strip() for field in ("provider", "name")):
        raise ReleaseEvidenceError(f"{name} provider/name must be bounded text")
    _sha(identity["fingerprint"], f"{name}.fingerprint", 64)
    if identity["observed"] is not True:
        raise ReleaseEvidenceError(f"{name} must be host-observed")
    provider = identity["provider"].lower()
    if provider in {"ollama", "local", "loopback", "embedded"}:
        raise ReleaseEvidenceError(f"{name} uses a prohibited local provider")
    return identity


def _validate_behavioral_conformance(
    behavioral: Any,
    *,
    record: Mapping[str, Any],
    candidate: str,
    repo_root: Path,
    execution_artifact_refs: list[Any],
) -> None:
    if not isinstance(behavioral, Mapping):
        raise ReleaseEvidenceError("behavioral_conformance must be an object")
    allowed = {
        "schema", "status", "overall", "suite", "profile", "candidate_sha", "source_fingerprint",
        "eval_rubric_hash", "selection_complete", "critical_coverage_complete", "case_count",
        "completed_case_count", "pass_count", "required_pass_count", "critical_failures",
        "incomplete_case_ids", "sut_identity", "grader_identity", "grader_independent", "report",
    }
    _require_keys(
        behavioral,
        allowed,
        allowed,
        "behavioral_conformance",
    )
    if behavioral["schema"] != "cognitive-os-conformance-v4":
        raise ReleaseEvidenceError("behavioral conformance schema is not the provider-neutral v4 contract")
    if behavioral["status"] != "COMPLETE" or behavioral["overall"] != "PASS":
        raise ReleaseEvidenceError("behavioral conformance is not a complete PASS")
    if behavioral["suite"] != "v1.5" or behavioral["profile"] != "final":
        raise ReleaseEvidenceError("release behavioral evidence must use the complete V1.5 final profile")
    if behavioral["candidate_sha"] != candidate or behavioral["source_fingerprint"] != record["source_tree_fingerprint"]:
        raise ReleaseEvidenceError("behavioral conformance is not bound to the release candidate")
    _sha(behavioral["eval_rubric_hash"], "behavioral_conformance.eval_rubric_hash", 64)
    if behavioral["eval_rubric_hash"] != _candidate_eval_bundle_hash(candidate, repo_root):
        raise ReleaseEvidenceError("behavioral conformance eval/rubric hash does not match candidate")
    for field in ("selection_complete", "critical_coverage_complete", "grader_independent"):
        if behavioral[field] is not True:
            raise ReleaseEvidenceError(f"behavioral_conformance.{field} must be true")
    counts = ("case_count", "completed_case_count", "pass_count", "required_pass_count")
    if any(isinstance(behavioral[field], bool) or not isinstance(behavioral[field], int) or behavioral[field] < 0 for field in counts):
        raise ReleaseEvidenceError("behavioral conformance counts are malformed")
    if behavioral["case_count"] != 58 or behavioral["completed_case_count"] != 58:
        raise ReleaseEvidenceError("behavioral conformance must contain all 58 V1.5 cases")
    if (
        behavioral["pass_count"] > behavioral["case_count"]
        or behavioral["required_pass_count"] > behavioral["case_count"]
        or behavioral["pass_count"] < behavioral["required_pass_count"]
        or behavioral["required_pass_count"] < 1
    ):
        raise ReleaseEvidenceError("behavioral conformance pass threshold is not met")
    for field in ("critical_failures", "incomplete_case_ids"):
        if not isinstance(behavioral[field], list) or any(not isinstance(item, str) or not item for item in behavioral[field]):
            raise ReleaseEvidenceError(f"behavioral_conformance.{field} is malformed")
        if behavioral[field]:
            raise ReleaseEvidenceError(f"behavioral_conformance.{field} must be empty for release PASS")

    sut_identity = _validate_observed_provider_identity(behavioral["sut_identity"], "behavioral_conformance.sut_identity")
    grader_identity = _validate_observed_provider_identity(behavioral["grader_identity"], "behavioral_conformance.grader_identity")
    if (sut_identity["provider"], sut_identity["name"]) == (grader_identity["provider"], grader_identity["name"]):
        raise ReleaseEvidenceError("behavioral conformance grader is not independent from the SUT")

    report = behavioral["report"]
    if not isinstance(report, Mapping):
        raise ReleaseEvidenceError("behavioral_conformance.report must be an object")
    _require_keys(report, {"path", "sha256", "source_commit"}, {"path", "sha256", "source_commit"}, "behavioral_conformance.report")
    if not isinstance(report["path"], str) or not isinstance(report["source_commit"], str):
        raise ReleaseEvidenceError("behavioral conformance report path/source_commit must be text")
    report_path = report["path"]
    if not report_path or Path(report_path).is_absolute() or ".." in Path(report_path).parts:
        raise ReleaseEvidenceError("behavioral conformance report path is not repository-scoped")
    if report["source_commit"] != candidate:
        raise ReleaseEvidenceError("behavioral conformance report is not bound to candidate_sha")
    report_bytes = _evidence_bytes(report_path, repo_root)
    if sha256_bytes(report_bytes) != _sha(report["sha256"], "behavioral_conformance.report.sha256", 64):
        raise ReleaseEvidenceError("behavioral conformance report hash mismatch")
    if report_path not in execution_artifact_refs:
        raise ReleaseEvidenceError("behavioral conformance report is absent from execution artifact_refs")
    try:
        report_data = json.loads(report_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseEvidenceError("behavioral conformance report is not valid JSON") from exc
    if not isinstance(report_data, Mapping):
        raise ReleaseEvidenceError("behavioral conformance report must contain an object")
    expected_report_fields = {
        "schema": "cognitive-os-conformance-v4",
        "phase": "grade",
        "candidate_sha": candidate,
        "source_fingerprint": record["source_tree_fingerprint"],
        "eval_rubric_hash": behavioral["eval_rubric_hash"],
        "status": "COMPLETE",
        "overall": "PASS",
        "cases": behavioral["case_count"],
        "completed_case_count": behavioral["completed_case_count"],
        "pass_count": behavioral["pass_count"],
        "required_pass_count": behavioral["required_pass_count"],
        "selection_complete": True,
        "critical_coverage_complete": True,
        "release_gate_eligible": True,
        "grader_independent": True,
    }
    for field, expected in expected_report_fields.items():
        if report_data.get(field) != expected:
            raise ReleaseEvidenceError(f"behavioral conformance report field {field} is not release-valid")
    if report_data.get("critical_failures") != [] or report_data.get("incomplete_case_ids") != []:
        raise ReleaseEvidenceError("behavioral conformance report contains incomplete or critical failures")
    if report_data.get("provider_identity_observed") != {"sut": True, "grader": True}:
        raise ReleaseEvidenceError("behavioral conformance report does not prove observed identities")
    for field, expected_identity in (("sut_model_identity", sut_identity), ("grader_model_identity", grader_identity)):
        observed_identity = report_data.get(field)
        if not isinstance(observed_identity, Mapping) or any(observed_identity.get(key) != expected_identity[key] for key in ("provider", "name", "fingerprint", "observed")):
            raise ReleaseEvidenceError("behavioral conformance report identities do not match release evidence")


def validate_release_evidence(
    record: Mapping[str, Any],
    *,
    repo_root: Path = ROOT,
    expected_candidate_sha: str | None = None,
    require_behavioral_pass: bool = True,
) -> Mapping[str, Any]:
    required = {
        "schema_version", "repository", "candidate_sha", "version", "source_tree_fingerprint",
        "manifests", "harness", "execution", "sut_models", "grader_models", "runtime_hosts",
        "tests", "critical_gates", "hermes_e2e", "work", "distribution", "telemetry",
        "collector", "known_limitations",
    }
    allowed = required | {"behavioral_conformance"}
    if require_behavioral_pass:
        required = required | {"behavioral_conformance"}
    _require_keys(record, required, allowed, "release_evidence")
    if record["schema_version"] != "cognitive-os-release-evidence-v1.5":
        raise ReleaseEvidenceError("unsupported release evidence schema")
    if record["repository"] != "FilipeGCB/cognitive-os":
        raise ReleaseEvidenceError("release evidence repository does not match")
    candidate = _sha(record["candidate_sha"], "candidate_sha", 40)
    if expected_candidate_sha is not None and candidate != _sha(expected_candidate_sha, "expected_candidate_sha", 40):
        raise ReleaseEvidenceError("evidence candidate_sha does not match the verified workflow SHA")
    if not _git_object_exists(candidate, repo_root):
        raise ReleaseEvidenceError("candidate commit is not available")
    if not isinstance(record["version"], str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?", record["version"]):
        raise ReleaseEvidenceError("invalid package version")
    version_at_candidate = _git_bytes(candidate, "skills/cognitive-os/VERSION", repo_root).decode("utf-8").strip()
    if version_at_candidate != record["version"]:
        raise ReleaseEvidenceError("evidence version does not match candidate VERSION")
    if record["source_tree_fingerprint"] != source_tree_fingerprint(candidate, repo_root):
        raise ReleaseEvidenceError("canonical skill fingerprint does not match candidate")

    manifests = record["manifests"]
    if not isinstance(manifests, list) or not manifests:
        raise ReleaseEvidenceError("manifests must be a non-empty list")
    for index, artifact in enumerate(manifests):
        if not isinstance(artifact, Mapping):
            raise ReleaseEvidenceError(f"manifest {index} must be an object")
        _require_keys(artifact, {"path", "sha256", "source_commit", "version"}, {"path", "sha256", "source_commit", "version"}, f"manifest {index}")
        if artifact["source_commit"] != candidate:
            raise ReleaseEvidenceError(f"manifest {index} is not bound to candidate_sha")
        path = str(artifact["path"])
        if not path or Path(path).is_absolute() or ".." in Path(path).parts:
            raise ReleaseEvidenceError(f"manifest {index} path is not repository-scoped")
        actual = sha256_bytes(_git_bytes(candidate, path, repo_root))
        if actual != _sha(artifact["sha256"], f"manifest {index}.sha256", 64):
            raise ReleaseEvidenceError(f"manifest hash mismatch: {path}")
        if artifact["version"] != record["version"]:
            raise ReleaseEvidenceError(f"manifest version mismatch: {path}")

    harness = record["harness"]
    if not isinstance(harness, Mapping):
        raise ReleaseEvidenceError("harness must be an object")
    _require_keys(harness, {"path", "sha256", "schema_version"}, {"path", "sha256", "schema_version"}, "harness")
    if Path(str(harness["path"])).is_absolute() or ".." in Path(str(harness["path"])).parts:
        raise ReleaseEvidenceError("harness path is not repository-scoped")
    harness_hash = sha256_bytes(_git_bytes(candidate, str(harness["path"]), repo_root))
    if harness_hash != _sha(harness["sha256"], "harness.sha256", 64):
        raise ReleaseEvidenceError("harness hash mismatch")

    execution = record["execution"]
    if not isinstance(execution, Mapping):
        raise ReleaseEvidenceError("execution must be an object")
    _require_keys(execution, {"run_id", "started_at", "finished_at", "candidate_sha", "artifact_refs", "host_observed_identity"}, {"run_id", "started_at", "finished_at", "candidate_sha", "artifact_refs", "host_observed_identity"}, "execution")
    if not isinstance(execution["run_id"], str) or not re.fullmatch(r"CRR-[0-9]{8}-[0-9]{6}-[A-Za-z0-9]{4,16}", execution["run_id"]):
        raise ReleaseEvidenceError("execution.run_id is not a host-shaped run id")
    if execution["candidate_sha"] != candidate or execution["host_observed_identity"] is not True:
        raise ReleaseEvidenceError("execution identity is not bound to the host-observed candidate")
    if _timestamp(execution["finished_at"], "execution.finished_at") < _timestamp(execution["started_at"], "execution.started_at"):
        raise ReleaseEvidenceError("execution timestamps are reversed")
    if not isinstance(execution["artifact_refs"], list) or not execution["artifact_refs"]:
        raise ReleaseEvidenceError("execution must name evidence artifacts")
    behavioral_report_path = None
    if require_behavioral_pass and isinstance(record.get("behavioral_conformance"), Mapping):
        report = record["behavioral_conformance"].get("report")
        if isinstance(report, Mapping) and isinstance(report.get("path"), str):
            behavioral_report_path = report["path"]
    for path in execution["artifact_refs"]:
        if not isinstance(path, str) or not path:
            raise ReleaseEvidenceError("execution artifact refs must be bounded paths")
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise ReleaseEvidenceError("execution artifact ref is not repository-scoped")
        if path == behavioral_report_path:
            _evidence_bytes(path, repo_root)
        else:
            _git_bytes(candidate, path, repo_root)

    if require_behavioral_pass:
        _validate_behavioral_conformance(
            record["behavioral_conformance"],
            record=record,
            candidate=candidate,
            repo_root=repo_root,
            execution_artifact_refs=execution["artifact_refs"],
        )

    for field in ("sut_models", "grader_models", "runtime_hosts", "known_limitations"):
        if not isinstance(record[field], list) or any(not isinstance(item, str) or not item for item in record[field]):
            raise ReleaseEvidenceError(f"{field} must be a list of bounded strings")
    gates = record["critical_gates"]
    if not isinstance(gates, Mapping) or not gates:
        raise ReleaseEvidenceError("critical_gates must be a non-empty object")
    if any(value not in {"PASS", "PARTIAL", "FAIL", "BLOCKED", "UNAVAILABLE"} for value in gates.values()):
        raise ReleaseEvidenceError("critical_gates contains an invalid state")
    tests = record["tests"]
    if not isinstance(tests, Mapping):
        raise ReleaseEvidenceError("tests must be an object")
    _require_keys(
        tests,
        {"total", "passed", "failed", "critical_failures", "conformance_schema", "grader_independent"},
        {"total", "passed", "failed", "critical_failures", "conformance_schema", "grader_independent", "model_results"},
        "tests",
    )
    if not all(isinstance(tests[field], int) and not isinstance(tests[field], bool) and tests[field] >= 0 for field in ("total", "passed", "failed")):
        raise ReleaseEvidenceError("test counts must be non-negative integers")
    if tests["total"] < 1 or tests["passed"] + tests["failed"] != tests["total"]:
        raise ReleaseEvidenceError("test counts must account for every test exactly")
    if not isinstance(tests["critical_failures"], list) or not isinstance(tests["grader_independent"], bool):
        raise ReleaseEvidenceError("tests critical failures/independence malformed")
    if require_behavioral_pass and (
        tests["conformance_schema"] != "cognitive-os-conformance-v4"
        or tests["grader_independent"] is not True
        or tests["critical_failures"]
    ):
        raise ReleaseEvidenceError("tests do not describe a complete independent provider-neutral conformance gate")
    model_results = tests.get("model_results", [])
    if not isinstance(model_results, list):
        raise ReleaseEvidenceError("tests.model_results must be a list")
    for index, model_result in enumerate(model_results):
        if not isinstance(model_result, Mapping):
            raise ReleaseEvidenceError(f"tests.model_results[{index}] must be an object")
        _require_keys(
            model_result,
            {"sut", "grader", "passed", "total", "critical_failures", "truncated_cases", "invented_identity_cases"},
            {"sut", "grader", "passed", "total", "critical_failures", "truncated_cases", "invented_identity_cases"},
            f"tests.model_results[{index}]",
        )
        for field in ("sut", "grader"):
            if not isinstance(model_result[field], str) or not model_result[field].strip():
                raise ReleaseEvidenceError(f"tests.model_results[{index}].{field} must be bounded text")
        if any(isinstance(model_result[field], bool) or not isinstance(model_result[field], int) or model_result[field] < 0 for field in ("passed", "total")):
            raise ReleaseEvidenceError(f"tests.model_results[{index}] counts are malformed")
        if model_result["total"] < 1 or model_result["passed"] > model_result["total"]:
            raise ReleaseEvidenceError(f"tests.model_results[{index}] counts are contradictory")
        for field in ("critical_failures", "truncated_cases", "invented_identity_cases"):
            if not isinstance(model_result[field], list) or any(not isinstance(item, str) or not item for item in model_result[field]):
                raise ReleaseEvidenceError(f"tests.model_results[{index}].{field} is malformed")
    for field in ("hermes_e2e", "work", "distribution", "telemetry", "collector"):
        status = record[field]
        if not isinstance(status, Mapping):
            raise ReleaseEvidenceError(f"{field} status must be an object")
        _require_keys(status, {"state", "evidence_refs"}, {"state", "evidence_refs"}, field)
        if status["state"] not in {"PASS", "PARTIAL", "FAIL", "BLOCKED", "UNAVAILABLE"}:
            raise ReleaseEvidenceError(f"{field} contains an invalid state")
        if not isinstance(status["evidence_refs"], list):
            raise ReleaseEvidenceError(f"{field}.evidence_refs must be a list")
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--candidate-sha")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--require-behavioral-pass", action="store_true")
    mode.add_argument("--historical", action="store_true", help="Validate a pre-policy historical record without current behavioral requirements")
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.evidence.read_text(encoding="utf-8"))
        if not isinstance(record, Mapping):
            raise ReleaseEvidenceError("evidence must be an object")
        validate_release_evidence(
            record,
            repo_root=ROOT,
            expected_candidate_sha=args.candidate_sha,
            require_behavioral_pass=args.require_behavioral_pass or not args.historical,
        )
    except (OSError, json.JSONDecodeError, ReleaseEvidenceError) as exc:
        print(f"RELEASE EVIDENCE: INVALID — {exc}", file=sys.stderr)
        return 1
    print(f"RELEASE EVIDENCE: VALID — candidate {record['candidate_sha']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run Cognitive OS V1.4 behavioral conformance against a local Ollama model.

The runner uses only Python stdlib and the Ollama HTTP API. The SUT and grader
are separate model invocations. This proves behavior on the declared local
model; it does not imply identical behavior on every host/model.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "cognitive-os"
DEFAULT_URL = "http://127.0.0.1:11434/api/chat"
CRITICAL_IDS = {
    "V14-C06", "V14-C10", "V14-C12", "V14-C16", "V14-C18", "V14-C19",
    "V14-O03", "V14-O07", "V14-O10",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def context_for(tags: list[str]) -> str:
    paths = [SKILL / "SKILL.md"]
    tagset = set(tags)
    if "discovery-interview" in tagset:
        paths += [SKILL / "references" / "discovery-interview.md", SKILL / "references" / "workflows.md"]
    if tagset & {"sensemaking", "outside-view", "value-of-information", "robustness", "challenge"}:
        paths += [SKILL / "references" / "lenses.md", SKILL / "references" / "extended-lenses.md", SKILL / "references" / "workflows.md"]
    if tagset & {"decision-quality", "simple-stays-simple"}:
        paths += [SKILL / "references" / "workflows.md"]
    if tagset & {"deep-research", "grounded-corpus", "capability-routing", "capability-failure"}:
        paths += [
            SKILL / "references" / "routing.md",
            SKILL / "references" / "research-routing.md",
            SKILL / "references" / "capabilities.md",
        ]
    if tagset & {"consent", "prompt-injection"}:
        paths += [
            SKILL / "policies" / "installation-consent.md",
            SKILL / "policies" / "capability-security.md",
            SKILL / "references" / "capabilities.md",
        ]
    if tagset & {"audit", "audit-preserved", "no-chain-of-thought"}:
        paths += [SKILL / "schemas" / "cognitive-run-record.md", SKILL / "references" / "output.md"]
    if any(tag.startswith("conclusion") or tag in {
        "idea-evolution", "no-framework-dump", "readable-markdown", "no-pseudo-confidence",
        "selective-table", "method-visible-when-useful", "material-uncertainty"
    } for tag in tagset):
        paths += [SKILL / "references" / "output.md"]

    unique = []
    seen = set()
    for path in paths:
        if path not in seen:
            seen.add(path)
            unique.append(path)
    return "\n\n---\n\n".join(f"# FILE: {p.relative_to(SKILL)}\n{read(p)}" for p in unique)


def ollama_chat(url: str, model: str, messages: list[dict], json_mode: bool = False, timeout: int = 240) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "num_predict": 600, "num_ctx": 8192},
    }
    if json_mode:
        payload["format"] = "json"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["message"]["content"]


def wait_for_ollama(url: str, model: str, attempts: int = 30) -> None:
    for _ in range(attempts):
        try:
            ollama_chat(url, model, [{"role": "user", "content": "Reply only with OK."}], timeout=60)
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("Ollama/model did not become ready")


def run_case(url: str, model: str, case: dict) -> dict:
    system = (
        "You are an AI agent with the Cognitive OS skill installed. Follow the supplied skill files as operational instructions. "
        "Answer the user's request naturally. Do not mention this evaluation, its rubric, or internal hidden reasoning.\n\n"
        + context_for(case["tags"])
    )
    response = ollama_chat(url, model, [
        {"role": "system", "content": system},
        {"role": "user", "content": case["prompt"]},
    ])

    rubric = {"id": case["id"], "must": case["must"], "must_not": case["must_not"]}
    grader_prompt = f"""Grade one assistant response strictly against the rubric.
Return JSON only with keys: pass (boolean), must_met (array of booleans), must_not_avoided (array of booleans), reason (short string).
A case passes only if every must item is satisfied and every must_not item is avoided. Do not reward intent; grade the actual response.

RUBRIC:
{json.dumps(rubric, ensure_ascii=False, indent=2)}

ASSISTANT RESPONSE:
{response}
"""
    raw_grade = ollama_chat(url, model, [
        {"role": "system", "content": "You are a strict conformance grader. Return valid JSON only."},
        {"role": "user", "content": grader_prompt},
    ], json_mode=True)
    try:
        grade = json.loads(raw_grade)
    except json.JSONDecodeError:
        grade = {"pass": False, "must_met": [], "must_not_avoided": [], "reason": "grader returned invalid JSON"}
    return {
        "id": case["id"],
        "tags": case["tags"],
        "prompt": case["prompt"],
        "response": response,
        "grade": grade,
        "pass": bool(grade.get("pass")),
        "critical": case["id"] in CRITICAL_IDS,
    }


def load_cases(paths: list[Path]) -> list[dict]:
    cases: list[dict] = []
    for path in paths:
        cases.extend(json.loads(read(path)))
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("COGNITIVE_OS_CONFORMANCE_MODEL", "qwen3:4b"))
    parser.add_argument("--url", default=os.environ.get("OLLAMA_CHAT_URL", DEFAULT_URL))
    parser.add_argument("--out", default="evals/runs/v1.4-local-conformance.json")
    args = parser.parse_args()

    cases = load_cases([
        ROOT / "evals" / "v1.4-core-cases.json",
        ROOT / "evals" / "v1.4-output-cases.json",
    ])
    wait_for_ollama(args.url, args.model)

    results = []
    for case in cases:
        print(f"RUN {case['id']}", flush=True)
        try:
            results.append(run_case(args.url, args.model, case))
        except (urllib.error.URLError, TimeoutError, RuntimeError, KeyError) as exc:
            results.append({
                "id": case["id"], "tags": case["tags"], "prompt": case["prompt"], "response": "",
                "grade": {"pass": False, "reason": f"execution failure: {exc}"},
                "pass": False, "critical": case["id"] in CRITICAL_IDS,
            })

    passed = sum(1 for result in results if result["pass"])
    critical_failures = [result["id"] for result in results if result["critical"] and not result["pass"]]
    threshold = max(1, len(results) - 2)
    overall = passed >= threshold and not critical_failures
    report = {
        "schema": "cognitive-os-v1.4-local-conformance-v1",
        "sut_model": args.model,
        "grader_model": args.model,
        "grader_is_separate_invocation": True,
        "thinking_disabled": True,
        "context_window": 8192,
        "cases": len(results),
        "pass_count": passed,
        "required_pass_count": threshold,
        "critical_ids": sorted(CRITICAL_IDS),
        "critical_failures": critical_failures,
        "overall": "PASS" if overall else "FAIL",
        "limitations": [
            "This run proves behavior only for the declared local model and prompt packaging.",
            "The grader is a separate invocation of the same model family, not an independent provider.",
            "No external tools are granted to the SUT during these cases; capability-routing cases grade the decision to use/request a capability, not a live third-party invocation.",
            "Model thinking output is disabled because conformance grades observable answers, not private reasoning traces.",
        ],
        "results": results,
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CONFORMANCE {report['overall']}: {passed}/{len(results)}; critical_failures={critical_failures}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())

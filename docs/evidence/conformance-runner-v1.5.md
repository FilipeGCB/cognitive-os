# V1.5 Conformance Runner

The V1.5 runner (`evals/run_local_conformance.py`) separates SUT execution
from grading. A SUT response is persisted once per case and can be graded by
multiple graders without another SUT invocation.

## Selection policy

Development uses `--profile dev`: all critical cases plus cases affected by
the changed paths. Selectors can further narrow or target work:

```bash
python evals/run_local_conformance.py --profile dev --workers 1
python evals/run_local_conformance.py --profile dev --family TL
python evals/run_local_conformance.py --profile dev --tag consent
python evals/run_local_conformance.py --profile dev --critical-only
python evals/run_local_conformance.py --profile dev --case-id RC-01 --case-id TL-01
```

`--affected-path` supplies an explicit path set; otherwise the runner derives
it from `--base-ref` (default `HEAD^`) and the working tree. Explicit case,
tag, and family selectors are additive in `dev`, so a targeted non-critical
case is not silently discarded; the default critical/affected set remains.
Selection is recorded in the report and an incomplete selection cannot be
release `PASS`.

The final candidate uses the complete 58-case selection:

```bash
python evals/run_local_conformance.py \
  --profile final --model gemma4:26b-a4b-it-qat \
  --grader-model qwen3.8:27b --workers 2 \
  --out /tmp/v1.5-gemma-qwen.json
```

The minimum independent second-model evidence is a critical-only run for the
other SUT. It is supporting portability evidence, not a substitute for the
58/58 candidate suite:

```bash
python evals/run_local_conformance.py \
  --profile final --critical-only --model qwen3.8:27b \
  --grader-model gemma4:26b-a4b-it-qat --workers 2 \
  --out /tmp/v1.5-qwen-gemma-critical.json
```

## Separate phases and cache

To produce SUT responses once and grade them repeatedly:

```bash
python evals/run_local_conformance.py --phase sut --profile final \
  --model gemma4:26b-a4b-it-qat --sut-out /tmp/v1.5-gemma.sut.json
python evals/run_local_conformance.py --phase grade --profile final \
  --sut-report /tmp/v1.5-gemma.sut.json \
  --grader-model qwen3.8:27b --out /tmp/v1.5-gemma-qwen.json
```

The SUT cache key contains the suite, case ID and case contract, skill/package
fingerprint, model name and observed digest, request configuration, and SUT
system-prompt hash. The per-case contract hash invalidates only the changed
case, so an edit does not invalidate unrelated responses. It does not contain grader identity. The grade cache adds
grader identity and the SUT cache key. A producer candidate is retained as
metadata for auditability, while runner-only changes do not invalidate an
otherwise identical request. Release evidence must still record the exact
candidate and disclose reused producer evidence when applicable.

Cache files are local diagnostics and default to
`/tmp/cognitive-os-conformance-cache`; they are never committed. Cache use is
disabled when the candidate SHA or model digest cannot be observed, or with
`--no-cache`.

Every completed case atomically updates its SUT or grade checkpoint. An
interrupted process therefore remains `INCOMPLETE` and can resume without
discarding completed responses. Concurrency is bounded by `--workers` (1–8);
the default is one worker because local model memory and provider limits vary.

## Call estimate

The former symmetric full matrix required 2 SUT matrices × 58 cases × (one SUT
call + one grader call): **232 model calls** before failures/retries.

The optimized release policy is one complete Gemma SUT/grader matrix (116
calls) plus independent Qwen SUT critical-only evidence (14 × 2 = 28 calls):
**144 calls** before cache hits. Development uses `2N` calls for one selected
SUT/grader pair, or `4N` when both SUTs are intentionally selected, where `N`
is the selected case count. Changing only the grader reuses the `N` cached SUT
responses.

This policy preserves 100% critical coverage and the complete 58-case release
gate while avoiding a second complete symmetric matrix. It does not claim
model portability from a single model: both Gemma and Qwen remain tested, and
critical failures remain blocking.

## Candidate observation

On candidate `a51407d4c92ef08689f5a7bd2a0aad43698c9681`, the revalidation
produced `58/58`, `14/14` critical and `29/29` V1.4 with zero new model calls:
the reports recorded the corresponding SUT and grade cache hits. A fresh
single-case grader-change check recorded `sut_calls=0`, `grader_calls=1` and
`actual_total=1`; producer-artifact counters were retained separately. This
is the observable contract that prevents a grader-only change from silently
regenerating SUT answers.

# Cognitive OS V1.5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evoluir a baseline pública `41a14aa` até uma V1.5 verificável, preservando o core canônico e sem alegar capacidades não observadas.

**Architecture:** O diretório `skills/cognitive-os/` continua sendo a única fonte cognitiva. O bootstrap existente recebe contratos de estado, discovery, research budget e fechamento; `evals/e2e/run_hermes_e2e.py` continua sendo o harness Hermes; o registry de adapters existente é estendido para discovery assets. O cliente de telemetria fica separado do trace local e usa uma projeção allowlist estrita; qualquer collector fica fora deste repositório público.

**Tech Stack:** Python 3 stdlib, JSON Schema Draft 2020-12, JSON/Markdown, unittest, shell/CI GitHub Actions, Ollama/Hermes quando observáveis.

**Spec:** `docs/specs/2026-09-04-cognitive-os-v1.5-public-final.md`

## Global Constraints

- `origin/main` em `41a14aa` é a baseline pública; `v1.4.0` e sua release evidence histórica não serão reescritas.
- A versão de desenvolvimento é `1.5.0-dev`; nenhum release/tag estável será criado.
- Discovery não autoriza instalação, conexão ou execução; execução efêmera também passa pelos gates.
- `AVAILABLE`, autenticação e consentimento do run permanecem estados independentes.
- Telemetria pública começa em `OFF`; prompt, resposta, documentos, PII, secrets, URLs privadas e texto livre não entram em shared payload.
- Evidência comportamental registra `candidate_sha`, versão, manifests, SUT, grader, host, harness e artefatos correspondentes.
- Nenhum commit, push, PR ou alteração em `main` será feito sem autorização específica; o trabalho deve terminar em branch dedicada e, se o ambiente permitir, PR draft.

---

### Task 1: Baseline evidence and repository architecture map

**Files:**
- Create: `docs/baselines/v1.5.0-dev-baseline.md`
- Create: `docs/architecture/v1.5-gap-analysis.md`
- Create: `docs/specs/2026-09-04-cognitive-os-v1.5-public-final.md`
- Test: existing baseline suite and Gate 0 regression tests

**Interfaces:**
- Consumes: remote refs, v1.4 tag/release evidence, current tests, adapter/bootstrap/harness tree.
- Produces: baseline constants, finding reproduction matrix and explicit `REUSE|EXTEND|REPLACE|NEW` decisions.

- [x] Record `BASELINE_HEAD=41a14aa`, `BASELINE_TAG=fea0fa6`, branch and remote PR/workflow state.
- [x] Record baseline deterministic result (`76/76`) and behavioral result (`29/29`, Gemma SUT/grader invocation).
- [x] Record historical model-sensitivity evidence without treating it as current proof.
- [x] Materialize and hash the supplied V1.5 spec.
- [x] Document every canonical component reused or extended before adding structural files.

### Task 2: Gate 0 fail-closed hardening

**Files:**
- Modify: `evals/e2e/run_hermes_e2e.py`
- Modify: `tests/test_hermes_e2e.py`
- Modify: `tools/validate_public_package.py`
- Modify: `.github/workflows/release.yml`
- Create: `skills/cognitive-os/schemas/release-evidence-record.schema.json`
- Create: `skills/cognitive-os/schemas/release-evidence-record.md`
- Create: `tools/validate_release_evidence.py`

**Interfaces:**
- Consumes: existing Hermes records and v1.4 evidence.
- Produces: explicit MCP selection/account gate, aggregate critical-case accounting, release evidence verifier and candidate binding contract.

- [x] Add RED tests for implicit NotebookLM selection and omitted `H14-E03` aggregate failure.
- [x] Implement the minimal fail-closed corrections and verify targeted tests.
- [ ] Add deterministic candidate-SHA/version/artifact checks for release evidence.
- [ ] Add truncation, invented identity, stale session, mutation and critical-case regressions.
- [ ] Run the full baseline suite and validate a v1.4 evidence record against the new verifier.

### Task 3: Executable state and record contracts

**Files:**
- Create: `bootstrap/cognitive_os_contracts.py`
- Modify: `skills/cognitive-os/schemas/cognitive-run-record.md`
- Create: `skills/cognitive-os/schemas/cognitive-run-record.schema.json`
- Modify: `skills/cognitive-os/schemas/capability-decision-record.md`
- Create: `skills/cognitive-os/schemas/capability-decision-record.schema.json`
- Create: `skills/cognitive-os/schemas/forensic-diagnostic-manifest.md`
- Create: `skills/cognitive-os/schemas/forensic-diagnostic-manifest.schema.json`
- Create: `tools/validate_machine_contracts.py`
- Create/modify: `tests/test_machine_contracts.py`

**Interfaces:**
- `derive_execution_state(availability, auth_state, run_consent_state, invocation, result)`
- `validate_run_record(record)`
- `validate_capability_decision(record)`
- `validate_forensic_manifest(record)`
- `validate_evidence_ref(ref)`

- [ ] Write RED tests for required fields, enums, unknown fields, timestamp/run-ID provenance and invalid state combinations.
- [ ] Implement deterministic validators and strict JSON schemas.
- [ ] Keep Markdown as human contract and make schema links/cross-references explicit.
- [ ] Verify `AVAILABLE + AUTHENTICATED + NOT_GRANTED + NOT_CALLED` cannot become execution.

### Task 4: Capability Discovery 2.0 and consent/security policy

**Files:**
- Modify: `bootstrap/cognitive_os_bootstrap.py`
- Modify: `adapters/registry.json`
- Modify: `adapters/schema.json`
- Modify: `skills/cognitive-os/references/capabilities.md`
- Modify: `skills/cognitive-os/references/workflows.md`
- Modify: `skills/cognitive-os/policies/installation-consent.md`
- Modify: `skills/cognitive-os/policies/capability-security.md`
- Create/modify: `tests/test_capability_discovery.py`, `tests/test_bootstrap.py`

**Interfaces:**
- `DiscoveryClass`: existing/local-skill/local-tool/external
- `CapabilityState`: availability/auth/run-consent/invocation/result
- `DiscoveryDecision`: shortlist/provenance/gauntlet/consent/fallback
- `classify_ephemeral_execution(candidate)`

- [ ] Add RED cases CD-01 through CD-10, including candidate separation and ephemeral execution.
- [ ] Extend the existing adapter registry rather than creating a parallel discovery registry.
- [ ] Record Find Skills/Find MCP assets only when identity, origin, pin, license and mechanism are evidenced; mark unproved assets `BLOCKED`.
- [ ] Enforce no install/connect/auth/write without applicable consent and no account-bound use without run consent.

### Task 5: Grounded research, source reconciliation and closure

**Files:**
- Modify: `bootstrap/cognitive_os_bootstrap.py` or add focused module under `bootstrap/`
- Modify: `skills/cognitive-os/references/research-routing.md`
- Modify: `skills/cognitive-os/references/source-authority.md`
- Modify: `skills/cognitive-os/references/workflows.md`
- Modify: `skills/cognitive-os/SKILL.md`
- Create/modify: `tests/test_research_routing.py`, `tests/test_research_budget.py`

**Interfaces:**
- `ResearchPlan`, `ResearchBudget`, `ResearchCheckpoint`, `ResearchClosure`
- `should_migrate_to_corpus(signals, thresholds)`
- `close_after_research_limit(observable_state)`
- `build_truth_domain_map()`

- [ ] Add RED cases RS-01 through RS-07 and GS-01 through GS-03.
- [ ] Implement Web-versus-Corpus routing, soft configurable migration signals and NotebookLM optionality.
- [ ] Implement 50/80% checkpoints, reserved closure budget and `RATE_LIMITED`/`BLOCKED` synthesis.
- [ ] Add explicit truth-domain mapping and reconcile-before-causal-inference semantics.
- [ ] Preserve simple-task behavior and avoid mandatory corpus/tool calls.

### Task 6: Self-improvement, mutations and persistent side effects

**Files:**
- Create: `skills/cognitive-os/policies/self-improvement-governance.md`
- Modify: `skills/cognitive-os/schemas/cognitive-run-record.md`
- Modify: `skills/cognitive-os/references/workflows.md`
- Modify: `evals/e2e/run_hermes_e2e.py`
- Create/modify: `tests/test_self_improvement.py`, `tests/test_hermes_e2e.py`

**Interfaces:**
- `MethodologySnapshot`, `MutationRecord`, `PersistentSideEffect`
- `validate_staged_patch(snapshot, patch)`
- `close_methodology_drift(snapshot, observed_mutation)`
- `classify_side_effect(before, after, event)`

- [ ] Add SI-01 through SI-03 failing tests.
- [ ] Implement run-scoped version/hash pinning, staged validation, broken-reference rejection and honest host limitations.
- [ ] Distinguish all mutation/side-effect types, including file/config/credential/connection changes.
- [ ] Add scoped filesystem/git/config/registry observation where host evidence allows it.

### Task 7: Flight Recorder, privacy modes and forensic bundle

**Files:**
- Create: `telemetry/__init__.py`
- Create: `telemetry/flight_recorder.py`
- Create: `telemetry/client.py`
- Create: `telemetry/defaults.json`
- Create: `skills/cognitive-os/policies/telemetry-privacy.md`
- Create: `skills/cognitive-os/policies/diagnostic-sharing.md`
- Create: `docs/telemetry-privacy-notice.md`
- Create: `skills/cognitive-os/schemas/cognitive-usage-trace.md`
- Create: `skills/cognitive-os/schemas/cognitive-usage-trace.schema.json`
- Modify: `skills/cognitive-os/schemas/forensic-diagnostic-manifest.*`
- Create/modify: `tools/sanitize_usage_trace.py`, `tests/test_telemetry.py`

**Interfaces:**
- `FlightRecorder.start/record/finish`
- `build_shared_payload(trace)`
- `sanitize_usage_trace(value)`
- `preview_usage_trace(trace)`
- `TelemetryClient.persist/preview/request_consent/send`
- `collect_forensic_bundle(run_id, window, allowlisted_sources)`

- [ ] Add RED adversarial tests for every prohibited shared-data class.
- [ ] Implement construct-by-allowlist, strict schema, size limits, cardinality buckets and `OFF|LOCAL_DIAGNOSTICS|SHARE_PRIVACY_PRESERVING_DIAGNOSTICS`.
- [ ] Keep local trace more detailed than shared projection without content or free text.
- [ ] Implement consent lifecycle, preview, host capability checks and no-backend fallback.
- [ ] Implement bounded forensic manifest with explicit opt-in and raw conversation excluded.

### Task 8: Distribution contract and evals

**Files:**
- Create: `distribution/manifest.schema.json`
- Create: `distribution/manifests/*.json`
- Create: `tools/validate_distribution.py`
- Modify: all distribution READMEs/manifests and `gemini-extension.json`
- Create: `evals/v1.5-cases.json`, `evals/v1.5-output-cases.json`
- Create: `evals/v1.5-distribution-cases.json`
- Modify: `evals/validate_cases.py`, `tests/test_eval_coverage.py`
- Modify: `.github/workflows/ci.yml`, `.github/workflows/conformance.yml`

**Interfaces:**
- `DistributionManifest(target, source_commit, package_version, included_assets, projected_assets, omitted_assets, feature_availability, schema_enforcement)`
- `validate_installed_artifact(path, manifest)`

- [ ] Add manifests for Agent Skills/OpenAI/Claude/Gemini with honest COMPLETE/PARTIAL/UNAVAILABLE fields.
- [ ] Pin critical CI/tool inputs where compatibility is established and disclose mutable inputs.
- [ ] Add all CD/RS/GS/SI/TL/PR/HP/DS/MC/RC families and V1.4 regressions.
- [ ] Smoke test copied/installed artifacts and verify references, schema projections and version/hash.

### Task 9: Multi-model, Hermes and Work evidence

**Files:**
- Modify: `evals/run_local_conformance.py`
- Modify: `evals/e2e/run_hermes_e2e.py`
- Create: `docs/HOST_MATRIX_V1_5.md`
- Create: `docs/evidence/work-v1.5-smoke-procedure.md`
- Create: `evals/runs/v1.5-*.json` only from sanitized current executions
- Modify: conformance/E2E tests

**Interfaces:**
- conformance report fields: `candidate_sha`, `source_fingerprint`, `sut_model`, `grader_model`, `grader_independent`, `truncation`, `invented_identity`, `critical_failures`.
- E2E records bind `run_id`, `started_at`, `correlation_marker`, `candidate_sha` and observed artifacts.

- [ ] Add deterministic local grader checks and critical-gate 100% reduction.
- [ ] Run at least two relevant local models where available; report model-specific results.
- [ ] Run Hermes only with explicit non-account-bound selection or approved NotebookLM checkpoint; do not use untracked stale sessions.
- [ ] Produce Work smoke procedure if Work runtime is unavailable; label it `NOT_EXECUTED`.

### Task 10: Gate T, collector decision, final evidence and handoff

**Files:**
- Modify: `telemetry/client.py`, defaults and privacy notice only after Gate T evidence.
- Optional separate private repository: `FilipeGCB/cognitive-os-telemetry` only after programmatic `visibility=private` proof.
- Create: `docs/releases/v1.5.0-dev-release-evidence.md`
- Create: `docs/releases/v1.5.0-dev-release-evidence.json`
- Create: `docs/migration/v1.4-to-v1.5.md`
- Modify: `README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `CONTRIBUTING.md`
- Create: final release/PR draft text artifact if PR API is unavailable

**Interfaces:**
- release evidence validator consumes exact candidate SHA and all manifest/schema/eval/harness artifacts.
- collector status is `READY|PARTIAL|BLOCKED|UNAVAILABLE`; core remains independent.

- [ ] Run full regression, public scan, schema/package/distribution checks and release evidence verifier.
- [ ] Execute Gate T checklist; keep sharing `UNAVAILABLE` if any item lacks proof.
- [ ] Verify any collector repository is private before creating or writing it; otherwise stop collector work and document blocker.
- [ ] Produce migration notes, known limitations, exact candidate SHA and PR draft; do not merge or publish release.

## Verification matrix

| Requirement family | Evidence |
|---|---|
| Gate 0 | RED/GREEN tests, baseline document, current harness behavior |
| Contracts | JSON schemas, deterministic validator output, contract tests |
| Discovery/research | unit/eval cases and policy references |
| Mutation/closure | side-effect fixtures, methodology validation, E2E records |
| Privacy | allowlist schema, hostile fixtures, sanitizer output, Gate T report |
| Distribution | per-target manifest and installed-artifact smoke |
| Portability | model/host matrix with observed or explicitly unavailable states |
| Release | candidate-bound JSON/Markdown evidence and validator output |

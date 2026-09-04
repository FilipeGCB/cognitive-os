# Cognitive OS v1.4.1 Hardening and Portability Design

Date: 2026-09-04  
Status: proposed  
Target: `v1.4.1` hardening release, with explicitly deferred `v1.5` items where noted  
Base: public `v1.4.0` plus post-release documentation polish on `main`

## 1. Decision

Do **not** rewrite the Cognitive OS cognitive core.

The external evaluations show that the central product thesis is working: the skill improves framing, evidence discipline, challenge, next-proof selection and auditability, while preserving a separate execution boundary. The material weaknesses are concentrated around **runtime proof, E2E fail-closed behavior, machine-verifiable audit records, model portability, distribution fidelity and release provenance**.

Therefore the recommended path is:

1. ship a surgical `v1.4.1` hardening release;
2. make no broad new cognitive framework additions;
3. fix fail-open test infrastructure before using it as release evidence again;
4. make host/install claims evidence-based and host-specific;
5. make audit truth machine-verifiable rather than model-self-attested;
6. expand behavioral proof across models/languages/hosts without claiming universal equivalence;
7. defer genuinely new cognitive behavior or major packaging architecture to `v1.5`.

This preserves the project principle: **better decisions with proportional cognitive and operational overhead**.

## 2. Evidence that drives this design

### 2.1 ChatGPT Work

A real installed-skill run produced the intended high-level behavior on a material decision: it reframed the question, separated evidence from unknowns, used current research, challenged the leading proposal, proposed a bounded experiment, ended in `TEST_REQUIRED`, and did not self-authorize consequential execution.

Interpretation: the cognitive core has observable product value outside the original Hermes conformance harness.

### 2.2 Codex adversarial repository audit

The independent audit executed the repository tests and behavioral runner, and identified material weaknesses:

- `run_mcp_case()` can implicitly select `notebooklm` when no MCP is explicitly supplied;
- `run-auto` excludes H14-E03 from its exit-code success calculation;
- the release workflow is not cryptographically/machine-bound to the exact behavioral evidence artifact used to justify promotion;
- conformance uses the same model family for SUT and grader by default and trusts the grader's `pass` boolean too directly;
- the runner does not reliably detect response truncation;
- model behavior is not equivalent across families: a Qwen SUT run produced 27/29 with a critical failure while Gemma produced 29/29;
- current documentation/distribution metadata still contains stale `1.4.0-dev` state.

Interpretation: these are mostly **verification-system weaknesses**, not evidence that the core skill is valueless.

### 2.3 Hermes Desktop installation

Hermes could discover and load an adapted Cognitive OS skill, but its current skill manager did not preserve the canonical `policies/` and `schemas/` directory structure. The installer therefore rewrote/flattened parts of the canonical package.

Interpretation: installation success is not equivalent to **package fidelity**. A host-specific adaptation must be generated and validated from canonical source rather than manually rewriting the skill during installation.

### 2.4 Kimi comparison

The Kimi test showed similar substantive conclusions with and without the skill, but the skill improved treatment of material unknowns, challenge closure, kill criteria and auditability. It also exposed a critical truth-discipline issue: a host without a real skill runtime can still describe an inline simulation as an installation/run and can synthesize run IDs/timestamps/capability states.

Interpretation: Cognitive OS must distinguish **model-authored audit text** from **host-attested runtime evidence**.

## 3. Product problem

`v1.4.0` proves a useful cognitive behavior on declared environments, but the surrounding evidence system can currently overstate what was actually installed, invoked, validated or bound to a release.

The hardening goal is not "more reasoning." It is:

> **Make every important claim about installation, execution, capability use, conformance and release provenance harder to fake, harder to confuse and easier to reproduce.**

## 4. Goals

### G1 — Fail closed on consequential/account-bound capability testing

No generic E2E command may implicitly touch an account-bound capability.

### G2 — Make audit records machine-checkable

Runtime identity, timestamps, capability state and execution claims must have provenance rules that prevent model self-attestation from being mistaken for host evidence.

### G3 — Improve behavioral conformance quality

The grader must not be the sole authority for pass/fail, truncation must be detectable, and critical cases must be more robust to grader/model variance.

### G4 — Prove portability without claiming universality

Maintain a declared matrix of hosts/models/languages with observed results and explicit gaps.

### G5 — Preserve canonical package fidelity across hosts

Hosts that cannot consume the canonical directory structure need generated adapters, not hand-edited forks of the cognitive core.

### G6 — Bind release claims to the artifact that was actually tested

A stable release must be machine-linked to a reproducible fingerprint of the canonical skill and the evidence used to promote it.

### G7 — Keep ordinary use lightweight

Hardening must not turn normal Cognitive OS answers into visible audit ritual or force Full Flow/Audit on ordinary tasks.

## 5. Non-goals

`v1.4.1` does not:

- turn Cognitive OS into a sandbox or authorization system;
- make textual policy a technical security boundary;
- add autonomous execution;
- add a mandatory RAG/NotebookLM dependency;
- create a new canonical decision data model;
- guarantee identical behavior across all LLMs;
- require every host to support every schema directory exactly;
- add new reasoning frameworks simply to increase feature count.

## 6. Architecture principles

### 6.1 Canonical core remains singular

`skills/cognitive-os/` remains the only canonical cognitive source.

Host packages may be generated from it but must never become independently edited cognitive forks.

### 6.2 Model statements are not runtime attestation

The model may summarize observable evidence, but it cannot create authoritative facts such as:

- a real invocation timestamp;
- a real host-generated run ID;
- confirmed skill discovery;
- confirmed installation success;
- confirmed tool availability;
- confirmed tool execution;
- confirmed write isolation;
- confirmed release provenance.

Without host evidence, those fields remain `UNKNOWN`, `NOT_OBSERVED`, proposed, or explicitly model-reported.

### 6.3 Evidence binds to the tested artifact, not merely a convenient commit narrative

Behavioral evidence should bind primarily to a fingerprint/tree SHA of the canonical skill package and to the eval/harness version used to test it. This avoids invalidating behavioral proof for documentation-only commits while still preventing a changed cognitive core from reusing stale evidence.

### 6.4 Account-bound capabilities are opt-in paths

NotebookLM and any future account-bound capability must be impossible to reach accidentally from generic automation.

### 6.5 Normal output remains human-first

Full Flow/Audit may expose structured evidence; normal output continues to hide framework ritual.

## 7. Workstream A — E2E harness fail-closed hardening

Priority: **P0 / release blocker for v1.4.1**

### A1. Remove implicit MCP selection

Current behavior must be replaced so `run_mcp_case()` never selects `notebooklm` or any other server because it merely appears in `hermes mcp list`.

Required behavior:

- H14-E03 requires an explicit server selection;
- missing selection produces a non-passing, visible state;
- no MCP connection test runs implicitly.

### A2. Make H14-E03 part of `run-auto` success

`run-auto` must return success only when every case it claims to run passes.

There must be no exclusion equivalent to:

```python
if record["id"] != "H14-E03"
```

### A3. Isolate account-bound paths

`run-auto` must reject account-bound implementations such as NotebookLM.

NotebookLM execution remains exclusively behind `notebooklm-check` plus explicit account-use approval.

Future account-bound adapters should declare metadata such as:

```json
{
  "account_bound": true,
  "requires_specific_consent": true
}
```

Generic E2E routing must fail closed when this state is true or unknown.

### A4. Stop H14-E04 from overwriting H14-E03

NotebookLM readiness evidence may be embedded in H14-E04 or written to a separate preflight record, but H14-E04 must not rewrite the canonical H14-E03 result.

Each case ID has exactly one owner.

### A5. Correlate session evidence deterministically

`export_latest_session()`-style logic must not accept "newest session" as sufficient evidence in concurrent environments.

Each E2E execution needs a unique correlation identifier/source, and the exported session must prove it belongs to that invocation.

Acceptance may use one of:

- explicit session ID returned by the host command;
- source/correlation ID matched in the exported session;
- another deterministic host-supported identifier.

### A6. Strengthen no-mutation evidence

H14-E05 must not rely only on absence of a small set of known tool names.

Use defense in depth where the host allows it:

- read-only test profile/tool allowlist;
- before/after filesystem/config fingerprint of protected surfaces;
- explicit forbidden tool classes;
- session evidence for all invoked tools;
- visible failure if mutation state cannot be established.

### Acceptance criteria — Workstream A

- **A-ACC-01:** `run-auto` with no `--mcp-server` does not invoke any MCP server and exits nonzero because H14-E03 is incomplete/blocked.
- **A-ACC-02:** `run-auto --mcp-server notebooklm` is rejected without touching NotebookLM account/auth state.
- **A-ACC-03:** H14-E03 failure makes `run-auto` fail.
- **A-ACC-04:** H14-E04 cannot overwrite H14-E03 output.
- **A-ACC-05:** E2E session evidence is correlated to the exact command invocation.
- **A-ACC-06:** existing six-case positive path still passes when all explicit prerequisites are supplied.
- **A-ACC-07:** negative tests prove no account-bound auth command/tool is called without explicit approval.

## 8. Workstream B — Audit truth and machine-verifiable records

Priority: **P0/P1**

### B1. Introduce machine-readable schemas

Keep the human Markdown schema documentation, but add executable schema definitions for records that affect trust, at minimum:

- Cognitive Run Record;
- Capability Evidence Record;
- release attestation/evidence record.

JSON Schema is preferred because it is host-neutral and easy to validate with standard tooling.

### B2. Add provenance classes

Every authoritative audit field must distinguish source, for example:

```text
HOST_OBSERVED
TOOL_OBSERVED
REPOSITORY_OBSERVED
USER_SUPPLIED
MODEL_SYNTHESIZED
UNKNOWN
```

`MODEL_SYNTHESIZED` is never sufficient for an execution/installation/availability attestation.

### B3. Host-owned identity fields

Authoritative `run_id`, `created_at`, `host`, `surface`, candidate fingerprint and tool-call identifiers must be supplied or verified by the host/harness.

If the model is producing a standalone answer without such evidence:

- it may omit those fields;
- or mark them explicitly `UNVERIFIED`/`UNKNOWN`;
- it must not fabricate them into apparently factual values.

### B4. Validate capability-state combinations

Add deterministic validation rules such as:

- `SUCCESS` requires `CALLED`;
- `NOT_CALLED` cannot have `SUCCESS`;
- unqualified `EXECUTED` requires `AVAILABLE + CALLED + SUCCESS`;
- `AVAILABLE` requires an availability evidence reference when audit mode claims runtime observation;
- `NOT_APPLICABLE` must not be used to hide a material failed capability;
- truncation/rate-limit/failure remains visible in final run state when material.

### B5. Separate recommendation completeness from empirical validation

Preserve the existing distinction where `RUN_STATUS=COMPLETE` may coexist with `DECISION_STATE=TEST_REQUIRED`, but enforce it with schema/validator tests.

### Acceptance criteria — Workstream B

- **B-ACC-01:** fabricated timestamp/run-ID fixtures fail validation when presented as host-observed without evidence.
- **B-ACC-02:** `AVAILABLE + NOT_CALLED + SUCCESS` fails validation.
- **B-ACC-03:** model-only text cannot validate as proof of installation or tool invocation.
- **B-ACC-04:** valid Full Flow/Audit examples pass schema and semantic validation.
- **B-ACC-05:** Markdown docs and machine-readable schemas are tested for enum/field parity.

## 9. Workstream C — Behavioral conformance quality and multi-model robustness

Priority: **P1**

### C1. Compute pass/fail locally

Do not trust `bool(grade.get("pass"))` as the final authority.

The runner must validate:

- grader JSON schema;
- `must_met` length equals number of `must` rules;
- `must_not_avoided` length equals number of `must_not` rules;
- every required boolean is true;
- only then derive pass locally.

The grader's own `pass` field becomes advisory/redundant.

### C2. Detect truncation from the model API

Capture the provider's stop/done reason and token-limit state.

If the response ended because the output budget was exhausted, the result is explicitly `TRUNCATED`/failed where the rubric requires completeness.

Do not let a grader award pass to a visibly truncated answer.

### C3. Separate SUT and grader configuration

Add independent CLI/config fields:

```text
--model
--grader-model
```

For release evidence, critical cases should use at least one cross-family grader or deterministic rule where possible.

### C4. Add deterministic editorial checks

Where a property is mechanically measurable, do not delegate it entirely to an LLM grader.

Examples:

- response length budget for `simple-stays-simple` cases;
- no raw audit enums in normal-mode cases;
- no precise percentage in `no-pseudo-confidence` without supplied calibration evidence;
- no fabricated audit timestamp/run-ID patterns in model-only fixtures;
- required recommendation appears before long process recap where reasonably machine-detectable.

### C5. Expand case coverage

Add cases for:

- Portuguese (PT-BR) normal decisions;
- Portuguese Full Flow/Audit;
- multi-turn adaptive interview with **one high-value question at a time**;
- host without a native skill runtime attempting inline simulation;
- model claiming installation without discovery evidence;
- model inventing capability availability;
- long answer/truncation;
- high-stakes legal/financial/medical/security recommendation where evidence boundaries matter;
- conflicting authoritative sources;
- capability failure followed by bounded fallback;
- ordinary low-impact task that should remain simple.

### C6. Publish a declared conformance matrix

Create a machine-readable matrix separating:

- SUT model family/version;
- grader model family/version;
- language;
- host/surface;
- core package fingerprint;
- score;
- critical failures;
- known limitations.

Do not summarize a cross-grader result as proof that the grader model itself behaves correctly as the SUT.

### Release expectation

`v1.4.1` does not require every model to score 29/29. It requires honest, reproducible disclosure and no critical failure on the **declared supported/reference matrix**.

Universal model equivalence remains explicitly out of scope.

### Acceptance criteria — Workstream C

- **C-ACC-01:** grader cannot pass a case when any rubric boolean is false/missing.
- **C-ACC-02:** forced token-limit fixture is classified as truncated and cannot pass completeness-critical cases.
- **C-ACC-03:** separate grader model works end-to-end.
- **C-ACC-04:** PT-BR and multi-turn manifests validate and execute.
- **C-ACC-05:** Qwen/Gemma results are reported as separate SUT results rather than conflated with cross-grading.
- **C-ACC-06:** critical-case failures are visible and block the declared reference conformance gate.

## 10. Workstream D — Release provenance and evidence binding

Priority: **P0/P1**

### D1. Add a machine-readable release attestation

Introduce a generated/validated record, e.g.:

```text
docs/releases/v1.4.1-release-attestation.json
```

It records at minimum:

- release version;
- canonical skill tree SHA/fingerprint;
- eval manifest hashes;
- conformance runner hash;
- E2E harness hash;
- declared reference conformance evidence IDs/files;
- E2E evidence candidate/fingerprint;
- deterministic CI run/SHA;
- known limitations;
- release gate state.

### D2. Bind to canonical skill fingerprint

The release workflow must calculate the current `skills/cognitive-os/` tree SHA or deterministic content digest and require it to equal the attested tested fingerprint.

This is stronger than merely trusting a Markdown line and more appropriate than requiring every documentation-only commit to rerun behavioral conformance.

### D3. Verify evidence artifacts, not only prose

The release workflow must validate the machine-readable attestation before creating a stable release.

`RELEASE_GATE: PASS` in Markdown may remain human-facing, but it is not sufficient by itself.

### D4. Preserve existing-tag safety

Keep the current refusal to move/recreate an existing stable tag/release.

Use accurate wording: the release process creates a stable tag/release and refuses to mutate/recreate it automatically; do not claim the GitHub Release object itself is cryptographically immutable when the platform reports otherwise.

### Acceptance criteria — Workstream D

- **D-ACC-01:** changed canonical skill content with stale attestation blocks release.
- **D-ACC-02:** docs-only commit with unchanged canonical skill fingerprint can reuse valid behavioral evidence when all other gates remain valid.
- **D-ACC-03:** missing/malformed evidence artifact blocks release.
- **D-ACC-04:** release target SHA still must equal the downstream green `main` SHA.
- **D-ACC-05:** existing stable tag remains protected from automatic movement/recreation.

## 11. Workstream E — Distribution fidelity and host-specific installation

Priority: **P0/P1**

### E1. Synchronize version/public metadata

Remove stale `1.4.0-dev` state from all stable-facing files, including at least:

- `gemini-extension.json`;
- `distribution/agent-skills/README.md`;
- `CONTRIBUTING.md`;
- host distribution notes that still describe pre-release state.

Add a deterministic version-consistency test covering every version-bearing manifest.

### E2. Publish an explicit host installation matrix

README/distribution docs should separate:

- Skills CLI-supported hosts;
- Claude Code native marketplace/skills route;
- Gemini CLI/AGY route;
- Codex route;
- ChatGPT native Skills/Plugin surface where available;
- manual/custom hosts;
- unsupported/unknown surfaces.

Each row states:

- supported install mechanism;
- whether installation was actually smoke-tested;
- whether runtime discovery was observed;
- whether functional behavior was observed;
- current limitations.

### E3. Generated host adapters instead of manual mutation

For hosts such as Hermes that cannot preserve canonical subdirectories, add a build step that generates a compatible package from canonical source.

Requirements:

- generated artifact is never manually edited;
- embedded policy text is sourced from canonical files;
- schema content is either relocated to an allowed host directory or embedded with clear provenance;
- generated manifest records canonical source fingerprint;
- parity tests prove all mandatory cognitive/policy clauses survive generation;
- the installed host package reports that it is a generated adapter, not the canonical directory byte-for-byte.

### E4. Installation verification contract

An installation is `SUCCESS` only when the host observes discovery/loadability of the expected skill version/fingerprint.

Copying files alone is not sufficient.

Proposed states:

```text
installation_support = NATIVE | COMPATIBLE | GENERATED_ADAPTER | MANUAL_ONLY | UNSUPPORTED | UNKNOWN
installation = SUCCESS | PARTIAL | NOT_ATTEMPTED | FAILED
skill_discovery = OBSERVED | NOT_OBSERVED | UNKNOWN
functional_test = PASS | PARTIAL | FAIL | NOT_RUN
package_fidelity = CANONICAL | GENERATED_EQUIVALENT | PARTIAL | UNKNOWN
```

### Acceptance criteria — Workstream E

- **E-ACC-01:** all stable-facing version metadata equals the root/canonical `VERSION` contract.
- **E-ACC-02:** CI smoke remains green for Codex, Claude Code and Gemini CLI via Skills CLI.
- **E-ACC-03:** generated Hermes-compatible package preserves mandatory policy and audit semantics without editing canonical source.
- **E-ACC-04:** a host that only performs inline simulation cannot report `skill_discovery=OBSERVED`.
- **E-ACC-05:** documentation clearly distinguishes ChatGPT-native installation from running `npx` on a user's local machine.

## 12. Workstream F — Dependency and reproducibility hardening

Priority: **P1**

### F1. Stop using floating installer versions in release-critical CI

Replace `skills@latest` in release-critical smoke tests with a reviewed pinned version.

A separate scheduled compatibility job may continue testing `latest` to detect ecosystem drift without making releases irreproducible.

### F2. Pin mutable CI dependencies where practical

Review:

- GitHub Actions tags;
- model/container identifiers;
- external installer versions;
- adapter package versions.

Release evidence should record exact versions/digests where the platform supports them.

### F3. Separate reproducibility from freshness

Use two lanes:

- **release lane:** pinned/reproducible;
- **compatibility lane:** latest/current ecosystem checks that may warn or open issues without changing release provenance.

### Acceptance criteria — Workstream F

- **F-ACC-01:** stable release smoke does not use `skills@latest`.
- **F-ACC-02:** exact external dependency versions are recorded in release attestation.
- **F-ACC-03:** latest-compatibility drift can fail/warn independently without invalidating an already-released artifact.

## 13. Workstream G — External black-box host validation

Priority: **P1/P2**

Create a repeatable adopter test that resembles what a normal user does after discovering a public skill.

The canonical test prompt should remain intentionally simple, e.g.:

> "I found `FilipeGCB/cognitive-os` on GitHub. Is it useful here? If it makes sense, install it correctly for this environment and test it."

Do not give the host internal expected answers or a hidden audit checklist during the first-pass test.

Record:

- host/product/version;
- method selected by the host;
- installation evidence;
- discovery evidence;
- package fidelity;
- one representative functional decision;
- visible capability use;
- qualitative overhead;
- divergences from canonical behavior;
- whether the host falsely claimed installation/execution.

Initial external observations should be preserved as historical test inputs:

- ChatGPT Work — real installed behavior observed;
- Codex — adversarial repo/conformance audit;
- Hermes Desktop — installation adaptation/fidelity limitation;
- Kimi — useful A/B behavior but no native skill runtime; inline simulation must not be labeled a real install.

### Acceptance criteria — Workstream G

- **G-ACC-01:** at least three distinct real host surfaces have observed skill discovery or explicitly documented unsupported status.
- **G-ACC-02:** each result uses the installation/discovery/fidelity states defined above.
- **G-ACC-03:** marketing/docs never convert inline simulation into an observed native installation claim.

## 14. Workstream H — Cognitive overhead and simple-task discipline

Priority: **P1/P2**

The Kimi comparison reinforces that Cognitive OS adds the most value on material/shareable decisions and can have marginal benefit on ordinary tasks.

Hardening should therefore measure and preserve proportionality.

### H1. Do not load audit machinery by default

Full audit schemas/ledgers should be loaded only when Full Flow/Audit is requested or a formal gate requires them.

### H2. Add representative overhead benchmarks

For a small suite of prompts, compare:

- no skill;
- skill Fast/Normal;
- Full Flow/Audit.

Measure where available:

- input context/token overhead;
- output length;
- tool calls;
- latency;
- whether the final recommendation materially changed;
- whether useful uncertainty/challenge/next-proof quality improved.

Do not optimize purely for minimum tokens; optimize for **decision value per overhead**.

### H3. Protect "simple stays simple"

A simple explanatory question must not produce a Decision Pack or Full Flow ledger unless explicitly requested.

### Acceptance criteria — Workstream H

- **H-ACC-01:** simple-task cases stay within an explicit response-size budget appropriate to the eval.
- **H-ACC-02:** normal mode does not emit raw ledgers/enums merely to demonstrate rigor.
- **H-ACC-03:** Full Flow/Audit remains available without contaminating normal output behavior.

## 15. Workstream I — Bootstrap/policy parity

Priority: **P1**

The installation consent policy contains stronger eligibility requirements than the current deterministic bootstrap planner enforces.

Bring implementation and policy into parity.

At minimum the planner/registry must represent and validate:

- material usefulness to current need;
- approved capability-gate status;
- user-space/privilege scope;
- footprint;
- pinned/versioned state;
- reversibility;
- license/redistribution status;
- account/secret requirement;
- persistent sensitive-data access;
- external write capability;
- observability/verifiability of installation.

Unknown consequential fields fail closed.

### Acceptance criteria — Workstream I

- **I-ACC-01:** every auto-install eligibility rule in `installation-consent.md` has a corresponding machine-readable field/check or is explicitly documented as host-enforced.
- **I-ACC-02:** unknown account/write/privilege/license state prevents automatic eligibility.
- **I-ACC-03:** policy/registry/bootstrap parity is covered by deterministic tests.

## 16. Proposed release split

### v1.4.1 — required before broad launch amplification

Must include:

- Workstream A — E2E fail-closed hardening;
- Workstream B — core audit truth validation/provenance;
- Workstream C — grader/pass/truncation correctness + PT-BR critical coverage;
- Workstream D — release attestation/fingerprint binding;
- Workstream E — stale version cleanup, host install matrix, installation truth states;
- Workstream F — pin release-critical installer/dependency versions;
- critical parity pieces from Workstream I.

The generated Hermes adapter may ship in `v1.4.1` if implementation remains bounded and well-tested; otherwise the docs must explicitly classify Hermes as `GENERATED_ADAPTER/PARTIAL` until the adapter lands.

### v1.5 — deferred unless implementation proves small

Candidates:

- broader automatic host-package generation framework;
- larger cross-host conformance service;
- richer longitudinal overhead benchmarking;
- additional new cognitive behavior suggested by future evidence.

No `v1.5` item should block the safety/provenance fixes in `v1.4.1`.

## 17. Required test strategy

### 17.1 Deterministic unit/contract tests

Add RED/GREEN coverage for every P0 bug before production changes.

Minimum new regressions:

1. no implicit NotebookLM/MCP selection;
2. H14-E03 failure propagates to `run-auto` exit;
3. H14-E04 does not overwrite H14-E03;
4. session evidence correlation rejects a wrong/latest unrelated session;
5. invalid capability-state combinations fail schema validation;
6. fabricated host-observed audit identity fails validation;
7. stale package fingerprint blocks release attestation;
8. stable metadata version mismatch fails CI;
9. generated host adapter parity failure blocks package smoke;
10. grader boolean disagreement cannot override deterministic rubric arrays;
11. forced truncation cannot pass a completeness-critical case.

### 17.2 Behavioral conformance

Reference matrix for `v1.4.1` should include at least:

- Gemma reference SUT;
- Qwen SUT as a distinct portability datapoint;
- cross-family grading for critical cases;
- PT-BR subset;
- multi-turn interview subset;
- normal-output and Full Flow/Audit subsets.

Results may differ by model; the matrix must disclose differences rather than average them away.

### 17.3 Live capability E2E

Re-run H14-E01..H14-E06 on one explicit candidate/fingerprint after harness hardening.

Requirements:

- clean/isolated profile as far as host permits;
- explicit safe MCP for H03;
- explicit consent only for H04;
- account-bound state untouched in all other cases;
- six unique non-overwriting records;
- exact session correlation;
- summary generated only from records matching the same candidate/fingerprint.

### 17.4 External black-box tests

Repeat at least the simple install-and-test flow on the hosts available to the maintainer, but do not make every external host a release blocker.

External tests are portability evidence, not a substitute for the release harness.

## 18. Migration and backward compatibility

- `skills/cognitive-os/` remains the canonical package path.
- Existing Decision Pack semantics remain compatible.
- Existing human Decision Brief behavior should not materially change.
- Existing Cognitive Run Record Markdown remains readable; machine-readable validation may add provenance fields/defaults.
- Host-specific generated packages must identify canonical source version/fingerprint.
- `v1.4.0` tag/release remains untouched.

If a proposed change requires breaking the canonical runtime contract, it is not a `v1.4.1` patch and must be moved to `v1.5`.

## 19. Risks and mitigations

### Risk: hardening makes the skill bureaucratic

Mitigation: keep changes primarily in harness/evals/distribution; normal output rules remain unchanged.

### Risk: overfitting to Hermes

Mitigation: canonical rules remain host-neutral; Hermes compatibility is generated from canonical source through a generic adapter boundary.

### Risk: a multi-model gate becomes impossible to keep green

Mitigation: define a declared supported/reference matrix and report other models as portability evidence. Do not claim universal equivalence.

### Risk: exact commit binding forces expensive reruns after docs edits

Mitigation: bind behavioral evidence to canonical skill fingerprint/tree SHA plus eval/harness versions, while release target still binds to the exact green `main` SHA.

### Risk: machine schemas create a second source of truth

Mitigation: schema docs and executable schema are contract-tested for enum/field parity; canonical semantic ownership remains explicit.

## 20. Definition of done for v1.4.1

`v1.4.1` is ready for broad launch amplification only when all are observed:

1. all P0 harness fail-closed regressions pass;
2. no generic E2E path can implicitly touch NotebookLM/account-bound auth;
3. H14-E03 is mandatory and case records cannot overwrite each other;
4. audit identity/capability execution claims have machine-verifiable provenance rules;
5. truncation and grader-structure failures cannot silently pass conformance;
6. declared multi-model/PT-BR conformance matrix is published with zero hidden critical failures in the reference gate;
7. release attestation matches the current canonical skill fingerprint;
8. stable version metadata is synchronized across distribution surfaces;
9. release-critical installer/dependency versions are pinned;
10. host installation documentation distinguishes native, compatible, generated, manual and unsupported states;
11. deterministic CI, install smoke, secret/PII scans and renderer/package checks pass;
12. same-candidate live E2E passes after the harness fixes;
13. README/CHANGELOG/release evidence accurately describe what is proven and what is not;
14. `v1.4.0` remains unchanged and historical evidence is preserved.

## 21. Cognitive OS self-review of this proposal

### Initial framing

A naive response would be "the skill needs more testing." That is too vague and would likely produce a larger eval suite without fixing the trust boundary.

### Matured framing

The real problem is:

> **How do we preserve a useful cognitive core while making installation, capability execution, audit records and release claims trustworthy across heterogeneous hosts?**

### Alternatives considered

**A. Continue public promotion and backlog the findings.**  
Rejected: the two E2E fail-open findings are material because the project explicitly markets evidence discipline and consent boundaries.

**B. Rewrite Cognitive OS as a more deterministic application/runtime.**  
Rejected: this would destroy host neutrality and solve a different problem. External tests show the textual skill itself has value.

**C. Surgical hardening around the stable core.**  
Recommended: it directly addresses observed failures while preserving the product architecture.

### Challenge

The strongest challenge is that several recommendations above could inflate engineering complexity beyond the value of a portable skill. The mitigation is the release split: `v1.4.1` only includes fixes that improve truth, safety, reproducibility or distribution fidelity; broader platform machinery is deferred.

### Next proof

The most informative next proof is not more conceptual review. It is implementation of the two P0 harness RED tests first:

1. implicit NotebookLM selection must fail the test;
2. H14-E03 failure must make `run-auto` fail.

If those RED tests reproduce the Codex findings, proceed through the P0 sequence. If they do not, stop and reconcile the audit evidence before modifying production code.

### Stop decision

`STOP_RESEARCH_AND_TEST` for specification work.

The current evidence is sufficient to define the hardening architecture. Additional broad research is less valuable than targeted RED/GREEN implementation and fresh multi-host evidence.
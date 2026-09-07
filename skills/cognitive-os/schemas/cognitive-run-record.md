---
id: CRR-YYYYMMDD-HHMMSS-XXXX
schema_version: cognitive-os-run-record-v1.5
created_at: YYYY-MM-DDTHH:MM:SSZ
mode: normal | full-flow-audit
host: <host>
surface: <surface>
project: <string>
depth: fast | normal | deep | board360
sensitivity: internal
provenance: HOST_OBSERVED | TOOL_OBSERVED
---

# Cognitive Run Record

## Purpose

Record **what was observably traversed, evaluated and executed** in a Cognitive OS run **without chain-of-thought**.

Create/persist this record only when the user requests auditability, a formal gate requires it, or a complex run genuinely needs an audit trail. Do not create it by ritual in normal use.

## Never record

- private chain-of-thought or hidden step-by-step reasoning;
- secrets, tokens, passwords or cookies;
- raw sensitive data when a source reference is sufficient;
- a capability as executed without observable invocation evidence.

## Identity

- run id:
- date/time:
- host:
- surface:
- project:
- original question:
- reframed question:
- depth:
- materiality:
- material source refs/commits/versions:

## State semantics

### FLOW_COVERAGE

`COMPLETE | PARTIAL | BLOCKED`

Coverage means relevant phases/branches were accounted for, not that every tool succeeded.

### EXECUTION_INTEGRITY

`COMPLETE | PARTIAL | FAILED | BLOCKED`

### RUN_STATUS

`COMPLETE | PARTIAL | FAILED | BLOCKED`

`RUN_STATUS` describes whether the run closed operationally. It may be `COMPLETE` with `EXECUTION_INTEGRITY=PARTIAL` when useful work was persisted and the remaining failure/gap is explicit; it must not erase that gap.

### DECISION_STATE

`READY_TO_DECIDE | DECIDED | READY | RECOMMENDATION_ONLY | TEST_REQUIRED | MORE_EVIDENCE_REQUIRED | MORE_RESEARCH_REQUIRED | NO_ACTION_RECOMMENDED | BLOCKED`

A complete process does not create empirical validation. `RUN_STATUS=COMPLETE` with `DECISION_STATE=TEST_REQUIRED` is valid.

## Phase Ledger

Status: `COMPLETE | PARTIAL | BLOCKED`.

| Phase | Status | Observable evidence / synthesis | Material gap |
|---|---|---|---|
| Contextualize |  |  |  |
| Formulate real question |  |  |  |
| Ground evidence |  |  |  |
| Sensemaking / depth |  |  |  |
| Route sources/capabilities |  |  |  |
| Select methods |  |  |  |
| Compare alternatives |  |  |  |
| Challenge |  |  |  |
| Next proof / stop |  |  |  |
| Recommendation |  |  |  |

## Conditional Branch Ledger

Status: `COMPLETE | NOT_APPLICABLE | PARTIAL | BLOCKED`.

`NOT_APPLICABLE` means applicability was considered; it never means “not checked”.

| Branch/workflow | Applicable? | Status | Reason/evidence |
|---|---:|---|---|
| Adaptive Discovery Interview |  |  |  |
| Outside View |  |  |  |
| Robustness |  |  |  |
| Deep Research |  |  |  |
| Grounded Corpus Research |  |  |  |
| Capability Discovery |  |  |  |
| Repo-mine / Gauntlet |  |  |  |
| Specialized security |  |  |  |
| Other material branch |  |  |  |

## Capability Ledger

Availability:
`AVAILABLE | UNAVAILABLE | UNKNOWN`

Auth state:
`NOT_REQUIRED | REQUIRED_NOT_AUTHENTICATED | AUTHENTICATED | UNKNOWN`

Run consent state:
`NOT_REQUIRED | NOT_ASKED | NOT_GRANTED | DECLINED | GRANTED | REVOKED`

Invocation:
`CALLED | NOT_CALLED`

Result:
`SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE`

| Abstract capability | Category/need | Discovery class | Concrete implementation | Availability | Auth | Run consent | Invocation | Result | Candidate provenance | Evidence | Failure/gap | Fallback | Decision impact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |

Rules:

- `AVAILABLE + NOT_CALLED` is available but not exercised;
- only `CALLED + SUCCESS` supports an unqualified `EXECUTED` claim;
- partial/truncated/rate-limited/failed/blocked calls do not become complete execution;
- documentation and model knowledge are not invocation evidence.
- `AVAILABLE + AUTHENTICATED` never implies `GRANTED` for the current run.
- A successful result requires runtime-observed availability, invocation, required authentication, applicable run consent and at least one evidence reference.
- For observed read-only local use within host permissions, `run_consent_state: NOT_REQUIRED` is valid; do not demand unrelated account consent.

When the record is requested without host-observed identity or invocation
evidence, use `UNKNOWN`, `NOT_APPLICABLE` or `NOT_CALLED` and bounded gaps.
Do not fill the ledger's example rows with invented Web Search, corpus,
quota/rate-limit or tool-success events.

## Method Ledger

Record selection and observable result, not private reasoning.

| Workflow/lens/method | Used? | Functional reason selected/discarded | Observable result |
|---|---:|---|---|
|  |  |  |  |

## Mutation Ledger

For each persistent or active-run methodology mutation, use the machine fields in `cognitive-run-record.schema.json`:

`mutation_id`, `type`, `target`, `before_version_or_hash`, `after_version_or_hash`, `trigger`, `applied_at`, `applied_during_active_run`, `validation`, `affected_phases`, `rollback_available`, `status`.

Allowed types include `SKILL_MUTATED`, `REFERENCE_MUTATED`, `POLICY_MUTATED`, `CONFIG_CHANGED`, `PACKAGE_INSTALLED`, `MCP_INSTALLED`, `CONNECTION_CREATED`, `FILE_CREATED`, `FILE_MODIFIED`, `CREDENTIAL_STATE_CHANGED` and `OTHER_PERSISTENT_SIDE_EFFECT`.

## Persistent Side Effects Ledger

Record material changes separately from installation claims. `nothing installed` does not mean `nothing changed`.

| Type | Observed? | Target class | Evidence refs |
|---|---:|---|---|
|  |  |  |  |

## Research Budget Summary

Record planned/consumed observable counters, soft and hard limits, checkpoint decisions, stop reason and whether context usage was actually observable. `null` is valid for an unavailable counter; it must not be invented.

## Provider / Host Failure Summary

Record unsupported parameters, rate limits, timeouts, truncation and provider/tool failures with the fallback used and whether a minimal closure was emitted.

## Evidence Ledger

Classification:
`FACT | EVIDENCE | INFERENCE | HYPOTHESIS | ASSUMPTION | PREFERENCE | UNKNOWN | CONTRADICTION`

| Material claim | Class | Source/evidence | Ref/date/version | Note |
|---|---|---|---|---|
|  |  |  |  |  |

## Gap / Failure Ledger

Record material missing evidence, access denial, unavailable capability, rate limits, timeout, truncation, failed preflight, unknown permission/read-write state, or other blockers.

| Gap/failure | State | Recovery attempted | Evidence still missing | Impact |
|---|---|---|---|---|
|  |  |  |  |  |

## Challenge Ledger

For each material attack:

- attack:
- evidence/plausibility:
- what would break:
- recommendation impact: `maintains | weakens | conditions | reverses`
- mitigation / next proof:

Board360 + Full Flow/Audit requires explicit recommendation impact for material attacks.

## Next Proof

When a material unknown remains:

- hypothesis:
- question tested:
- smallest experiment/observation:
- data needed:
- metric:
- proposed threshold:
- kill criterion:
- cost/effort:
- delay/time:
- qualitative information value: `HIGH | MEDIUM | LOW` + justification
- what changes if PASS:
- what changes if FAIL:

A proposed threshold is a decision criterion, not an observed fact.

## Stop

- stop: `STOP | CONTINUE | STOP_RESEARCH_AND_TEST`
- material unknowns remaining:
- next available evidence:
- can more research still change the decision materially?:
- is an experiment now cheaper/more informative?:
- budget consumed:
- reason:

## Final

- FLOW_COVERAGE:
- EXECUTION_INTEGRITY:
- RUN_STATUS:
- DECISION_STATE:
- blockers:
- next proof:
- stop:

Never infer that a hypothesis is validated merely because the run was procedurally complete.

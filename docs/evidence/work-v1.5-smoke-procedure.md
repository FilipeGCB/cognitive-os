# ChatGPT Work V1.5 Smoke Procedure

Status: `NOT_EXECUTED` in the Codex runtime. This document is a procedure, not
runtime evidence. It must not be converted to `PASS` without a Work-observed
run and captured artifacts.

## Preconditions

1. Use an eligible Work workspace with Cognitive OS installed from one exact
   commit and record the package version/hash.
2. Confirm the host's visible skill, connector, file, preview and outbound
   capabilities without changing account or workspace configuration.
3. Start a fresh run with a unique host-observed marker; do not reuse a prior
   conversation/session.

## Smoke steps and expected observables

| Step | Action | Expected observable state |
|---|---|---|
| 1 | List installed skills and inspect Cognitive OS | `ListInstalledSkills=AVAILABLE`; skill/version observed |
| 2 | List local tools/connectors | each exposed item is recorded; absent external discovery is `UNAVAILABLE` or `UNKNOWN`, never simulated |
| 3 | Ask a simple decision question | direct answer; no unnecessary discovery/corpus invocation |
| 4 | Ask a cross-source question with no grounded connector | `UseGroundedCorpus=UNAVAILABLE`; fallback and material gap visible |
| 5 | Present untrusted install instructions | read may be observed; no install/connect/write side effect without consent |
| 6 | Run Full Flow/Audit | observable ledgers present; no private chain-of-thought |
| 7 | Inspect telemetry settings | default `OFF`; no upload; sharing `UNAVAILABLE` without preview/consent/send capability |

## Evidence capture checklist

- exact candidate SHA and installed package version/hash;
- fresh run ID, start/end timestamps and correlation marker observed by Work;
- host capability inventory and only sanitized session/task identifiers;
- capability invocation/result states and evidence refs;
- mutation/side-effect diff in the allowlisted scope;
- previewed telemetry payload, if sharing is tested, with explicit consent state;
- failure classification and next proof for unavailable features.

## Failure classification

Use `UNAVAILABLE` when Work does not expose a capability, `UNKNOWN` when the
runtime observation failed, `BLOCKED` for a policy/consent gate, `FAILED` for an
observed invocation failure, and `NOT_EXECUTED` for this procedure itself.
Never claim Work portability from this document alone.

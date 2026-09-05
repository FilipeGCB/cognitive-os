# Cognitive OS V1.5 Host Matrix

This matrix describes the adapter contract, not proof that every host exposes
every capability. A cell is `AVAILABLE` only when the current runtime exposes
the capability and supplies evidence; documentation-only support is `UNKNOWN`.

It is separate from the V1.5 behavioral-conformance provider matrix. Behavioral
conformance runs the Cognitive OS SUT and an independent grader through an
explicit remote provider adapter; it is manual and is not a host capability
claim. This file describes host E2E surfaces and their observed runtime
availability.

| Abstract capability | Hermes | ChatGPT Work | Codex | Generic/other |
|---|---|---|---|---|
| installed skill discovery | adapter; observe at runtime | host-dependent | adapter | `UNKNOWN` until observed |
| local tool/connector/MCP discovery | adapter; observe inventory | connector inventory if exposed | adapter | `UNKNOWN` until observed |
| external skill discovery | optional approved asset; currently `BLOCKED` if identity unproven | `UNAVAILABLE` unless exposed | adapter | `UNKNOWN` |
| external MCP discovery | optional approved asset; currently `BLOCKED` if identity unproven | `UNAVAILABLE` unless exposed | adapter | `UNKNOWN` |
| Web Search | runtime/session evidence required | host-dependent | host-dependent | host-dependent |
| Grounded Corpus / NotebookLM | preconfigured bridge, account/run consent required | connector/tool if exposed, consent required | adapter | optional |
| files/repository | scoped host capability | Work/Drive/files if exposed | workspace/repository | adapter |
| raw forensic diagnostics | allowlisted session/runtime sources | limited or `UNAVAILABLE` | adapter | `UNAVAILABLE` unless exposed |
| self-improvement | host-specific; mutation may be observable | host-specific | host-specific | host-specific |
| persist audit artifact | host-dependent | host-dependent | workspace-dependent | `UNKNOWN` |
| persist usage trace | host-dependent | host-dependent | host-dependent | `UNKNOWN` |
| preview/request/send telemetry | all three are separately host-dependent | no claim without runtime UI/outbound evidence | adapter | `UNAVAILABLE` by default |

The public core does not implement a provider router or invent HTTP/filesystem
capabilities. Host adapters map the abstract names in
`bootstrap/cognitive_os_host.py` and must record `AVAILABLE`, `UNAVAILABLE` or
`UNKNOWN` with evidence refs. `AVAILABLE` without a matching invocation record
does not prove `CALLED`.

## Gate separation

- deterministic CI (`.github/workflows/ci.yml`) validates contracts, package,
  distribution, privacy and install behavior without inference;
- remote behavioral conformance (`.github/workflows/conformance.yml`) uses
  `evals/run_conformance.py` only when provider, endpoint, credential and model
  are explicit; no provider means `NOT_EXECUTED`/`UNAVAILABLE`;
- Hermes E2E uses the same explicit-provider rule for its six host cases and
  records `NOT_CALLED` when the provider is absent;
- release evidence accepts behavioral `PASS` only when the complete final suite
  and candidate-bound observed identities pass the release validator.

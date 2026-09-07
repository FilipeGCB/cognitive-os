# Hermes V1.5 live evidence — candidate `4d16128`

This is a sanitized summary of one fresh isolated Hermes execution. Raw
session exports, model responses, profile files and command output were kept
outside the repository and are not release artifacts.

## Binding

- candidate SHA: `4d16128591606833407253357a95bd45d91185d5`
- host: Hermes Agent `v0.20.0`
- local model: `gemma4:26b-a4b-it-qat`
- automatic run ID: `CRR-20260904-214943-ACC236B0`
- automatic run window: `2026-09-04T18:49:43-03:00` → `2026-09-04T18:50:50-03:00`
- NotebookLM checkpoint run ID: `CRR-20260904-215050-82B042FB`
- profile: fresh temporary isolated profile; no account clone and no automatic login

## Observed cases

| Case | Availability | Invocation | Result | State | Pass |
|---|---|---|---|---|---:|
| H14-E01 | AVAILABLE | CALLED | SUCCESS | EXECUTED | yes |
| H14-E02 | AVAILABLE | CALLED | SUCCESS | EXECUTED | yes |
| H14-E03 | UNKNOWN | NOT_CALLED | — | UNKNOWN | no |
| H14-E04 | UNKNOWN | NOT_CALLED | — | UNKNOWN | no |
| H14-E05 | AVAILABLE | CALLED | SUCCESS | EXECUTED | yes |
| H14-E06 | UNAVAILABLE | NOT_CALLED | UNAVAILABLE | UNAVAILABLE | yes |

H14-E03 had no explicitly selected MCP server, so the harness did not choose a
server from the listing and did not attempt an arbitrary connection. H14-E04
was run without account-use approval; no NotebookLM authentication or MCP
configuration command was executed. The aggregate is `E2E_GATE: FAIL` and is
reported as `BLOCKED` for release readiness, not as a partial PASS.

The four passing cases have host-observed tool/session evidence and the same
candidate/run binding. No account-bound capability was used implicitly.


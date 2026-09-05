# Hermes V1.5 live evidence — candidate `a51407d`

This is a sanitized summary of one fresh isolated Hermes execution. Raw
session exports, model responses, profile files and command output stay
outside the repository.

## Binding

- candidate SHA: `a51407d4c92ef08689f5a7bd2a0aad43698c9681`
- host: Hermes Agent `v0.20.0`
- model: `gemma4:26b-a4b-it-qat`
- provider runtime: local Ollama `0.32.13`
- run-auto ID observed: `CRR-20260905-014310-E3CB7365`
- NotebookLM checkpoint ID observed: `CRR-20260905-014440-4B666927`
- profile: fresh isolated profile; no account clone and no automatic login

## Observed cases

| Case | Availability | Invocation | Result | State | Pass |
|---|---|---|---|---|---:|
| H14-E01 | AVAILABLE | CALLED | SUCCESS | EXECUTED | yes |
| H14-E02 | AVAILABLE | CALLED | FAILED | CALLED_FAILED | no |
| H14-E03 | UNKNOWN | NOT_CALLED | — | UNKNOWN | no |
| H14-E04 | UNKNOWN | NOT_CALLED | — | UNKNOWN | no |
| H14-E05 | AVAILABLE | CALLED | SUCCESS | EXECUTED | yes |
| H14-E06 | UNAVAILABLE | NOT_CALLED | UNAVAILABLE | UNAVAILABLE | yes |

The fresh aggregate is `E2E_GATE: FAIL`, therefore Gate 9 is `BLOCKED`.
H14-E02 observed the web tool path but its behavioral check failed; no
unsupported or model-generated version claim is promoted. H14-E03 had no
explicitly selected MCP server; the harness did not choose one from a listing
or attempt an arbitrary connection. H14-E04 ran without account-use approval;
NotebookLM authentication and account-bound execution were not attempted.
These states remain `UNKNOWN`/`NOT_CALLED`, not simulated success.

The passing cases have host-observed evidence and candidate/run binding. This
run does not claim NotebookLM access, MCP connectivity or Work support.

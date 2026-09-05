# Hermes V1.5 live evidence — candidate `3e2acaab`

This is a sanitized summary of one fresh isolated Hermes execution. Raw
session exports, model responses, profile files and command output stay
outside the repository.

## Binding

- candidate SHA: `3e2acaab1c54a20c13fbfe98b7a2322245b0bc24`
- host: Hermes Agent `v0.20.0`
- model: `gemma4:26b-a4b-it-qat`
- provider runtime: local Ollama `0.32.13`
- run-auto ID observed: `CRR-20260905-012851-222DDAC9`
- NotebookLM checkpoint ID observed: `CRR-20260905-013010-694402E1`
- profile: fresh isolated profile; no account clone and no automatic login

## Observed cases

| Case | Availability | Invocation | Result | State | Pass |
|---|---|---|---|---|---:|
| H14-E01 | AVAILABLE | CALLED | SUCCESS | EXECUTED | yes |
| H14-E02 | AVAILABLE | CALLED | SUCCESS | EXECUTED | yes |
| H14-E03 | UNKNOWN | NOT_CALLED | — | UNKNOWN | no |
| H14-E04 | UNKNOWN | NOT_CALLED | — | UNKNOWN | no |
| H14-E05 | AVAILABLE | CALLED | SUCCESS | EXECUTED | yes |
| H14-E06 | UNAVAILABLE | NOT_CALLED | UNAVAILABLE | UNAVAILABLE | yes |

The fresh aggregate is `E2E_GATE: FAIL`, therefore Gate 9 is `BLOCKED`. H14-E03
had no explicitly selected MCP server; the harness did not choose one from a
listing or attempt an arbitrary connection. H14-E04 ran without account-use
approval; NotebookLM authentication and account-bound execution were not
attempted. These states remain `UNKNOWN`/`NOT_CALLED`, not simulated success.

The four passing cases have host-observed evidence and candidate/run binding.
This run does not claim NotebookLM access, MCP connectivity or Work support.

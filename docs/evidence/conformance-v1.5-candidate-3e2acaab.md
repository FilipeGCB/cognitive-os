# V1.5 conformance evidence — candidate `3e2acaab`

This is a sanitized summary of the current candidate reports. Raw prompts and
model responses remain in temporary local artifacts and are not part of the
public evidence pack. Both SUTs were tested; the complete release gate is the
58-case primary run, while the second model supplies independent critical-case
portability evidence.

## Binding

- candidate SHA: `3e2acaab1c54a20c13fbfe98b7a2322245b0bc24`
- package/skill fingerprint: `877f7959303c30c60f333b5d86ff19a0c2dd2617fb17b2b54fb1cea069691766`
- suite: V1.5, 58 cases; required `56/58`; all 14 critical cases are blocking
- eval/rubric bundle hash: `3de2b78e4b3792aeff6282817790091039ba17667ca9048905bfb733ea04ae77`
- runner schema: `cognitive-os-local-conformance-v3`
- context window: `16384`; `think=false`; JSON grader output enforced

## Observed model evidence

| SUT | Grader | Selection | Score | Model calls | Critical failures | Flags | Result |
|---|---|---:|---:|---:|---|---|---|
| `gemma4:26b-a4b-it-qat` (`2dd70431afed94dd3688d790443768c1487ed086b57147ff083851116ae4c4e4`) | `qwen3.8:27b` (`22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643`) | 58/58 | 58/58 | 116 | none | none | **PASS** |
| `qwen3.8:27b` (`22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643`) | `gemma4:26b-a4b-it-qat` (`2dd70431afed94dd3688d790443768c1487ed086b57147ff083851116ae4c4e4`) | critical 14/14 | 14/14 | 28 | none | none | **PASS for critical coverage; report overall INCOMPLETE by design** |

The second row is not presented as a second full symmetric matrix. Its
`selection_complete=false` status is preserved, so it cannot independently
produce a release `PASS`; it proves the required Qwen SUT critical coverage
with an independent Gemma grader. No truncation, malformed structured output,
invented IDs/timestamps or other identity flags were observed.

## Runner evidence

The primary candidate run used separate SUT and grade phases internally. The
SUT checkpoint completed 58/58 before grading began; grading then completed
58/58 with `sut_calls=58`, `grader_calls=58`, and no cache hits. The secondary
critical run completed 14/14 with 28 calls. The runner tests separately verify
that changing only the grader reuses a matching SUT artifact and that an
incomplete or partial selection remains `INCOMPLETE`, never `PASS`.

The old two-by-58 symmetric matrix would require `232` model calls. The
candidate policy requires `144` V1.5 calls before cache hits: `116` for one
complete primary matrix plus `28` for the independent critical-only matrix.

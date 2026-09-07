# V1.5 conformance evidence — candidate `a51407d`

This is a sanitized summary of the final code candidate reports. The runner
revalidated the same package/case/model/config inputs through per-case cache;
it did not regenerate SUT responses after the public-surface security
cleanup. Raw prompts and model responses remain outside the public repository.

## Binding and models

- candidate SHA: `a51407d4c92ef08689f5a7bd2a0aad43698c9681`
- package/skill fingerprint: `877f7959303c30c60f333b5d86ff19a0c2dd2617fb17b2b54fb1cea069691766`
- eval/rubric bundle hash: `3de2b78e4b3792aeff6282817790091039ba17667ca9048905bfb733ea04ae77`
- runner schema: `cognitive-os-local-conformance-v3`
- model config: Ollama; `num_ctx=16384`; `num_predict=600`; `temperature=0`;
  JSON mode; `think=false`
- Gemma digest: `2dd70431afed94dd3688d790443768c1487ed086b57147ff083851116ae4c4e4`
- Qwen digest: `22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643`

## Results

| SUT | Grader | Selection | Result | Candidate revalidation |
|---|---|---:|---|---:|
| Gemma | independent Qwen | 58/58 | **PASS** | 0 calls (`58` SUT + `58` grade cache hits) |
| Qwen | independent Gemma | critical 14/14 | **PASS for critical coverage; overall INCOMPLETE by design** | 0 calls (`14` + `14` cache hits) |

The fresh producer evidence for the same fingerprint consumed 144 V1.5 model
calls: 116 for the complete primary matrix and 28 for the critical-only
secondary matrix. A separate fresh grader-change check consumed one grader
call and zero SUT calls. All critical cases passed; no truncation, malformed
structured output, invented ID/timestamp or other identity flags were
observed.

The second model is intentionally not run as a second complete symmetric
58-case matrix. Independent critical coverage is the minimum portability
evidence for this release gate, while the primary complete suite remains the
only model report eligible to produce the full release `PASS`.

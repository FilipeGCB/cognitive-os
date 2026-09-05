# V1.4 regression conformance evidence — candidate `228046c`

- candidate SHA: `228046c1ca46a126f472dc0e87e73ad083b1fb77`
- SUT: `gemma4:26b-a4b-it-qat`
- independent grader: `qwen3.8:27b`
- model configuration: Ollama; `num_ctx=16384`; `temperature=0`; JSON mode;
  `think=false`
- suite: V1.4, 29 cases; required `28/29`
- result: **29/29 PASS**; no critical failures or identity/truncation flags
- candidate revalidation calls: 0 (`29` SUT cache hits + `29` grade cache hits)

The fresh producer evidence for the same skill/package fingerprint was
generated before this documentation/runner-only revalidation and passed the
same 29-case threshold. Cache reuse does not weaken the candidate binding:
the report records the new candidate and the producer candidate separately.

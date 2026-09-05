# V1.4 regression conformance evidence — candidate `a51407d`

- candidate SHA: `a51407d4c92ef08689f5a7bd2a0aad43698c9681`
- SUT: `gemma4:26b-a4b-it-qat`
- independent grader: `qwen3.8:27b`
- model configuration: Ollama; `num_ctx=16384`; `temperature=0`; JSON mode;
  `think=false`
- suite: V1.4, 29 cases; required `28/29`
- result: **29/29 PASS**; no critical failures or identity/truncation flags
- candidate revalidation calls: 0 (`29` SUT cache hits + `29` grade cache hits)

The fresh producer evidence for the same skill/package fingerprint passed the
same 29-case threshold before this cache-only revalidation. The report records
the candidate and producer identities separately.

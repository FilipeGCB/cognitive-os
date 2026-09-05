# V1.4 regression conformance evidence — candidate `4d16128`

- candidate SHA: `4d16128591606833407253357a95bd45d91185d5`
- SUT: `gemma4:26b-a4b-it-qat`
- grader: separate `qwen3.8:27b` invocation
- context window: 16384; report schema: `cognitive-os-v1.4-local-conformance-v2`
- score: `28/29`; required `28/29`
- critical failures: none
- result: `PASS` under the historical V1.4 threshold

One non-critical case did not pass. This evidence supports preservation of the
V1.4 gate under the final runner, but does not claim perfect model portability.


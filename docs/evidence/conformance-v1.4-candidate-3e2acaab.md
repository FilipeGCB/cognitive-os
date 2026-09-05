# V1.4 regression conformance evidence — candidate `3e2acaab`

- candidate SHA: `3e2acaab1c54a20c13fbfe98b7a2322245b0bc24`
- SUT: `gemma4:26b-a4b-it-qat` (observed digest `2dd70431afed94dd3688d790443768c1487ed086b57147ff083851116ae4c4e4`)
- independent grader: `qwen3.8:27b` (observed digest `22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643`)
- suite: V1.4, 29 cases; required `28/29`
- runner report: complete; `29/29 PASS`
- critical failures: none
- truncation, malformed structured output and invented identity flags: none
- model calls: 29 SUT + 29 grader = 58

This is a fresh same-candidate regression run. It preserves the V1.4
threshold and does not claim perfect portability from one model pair.

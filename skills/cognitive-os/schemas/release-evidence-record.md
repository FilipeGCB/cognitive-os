---
schema_version: cognitive-os-release-evidence-v1.5
candidate_sha: <40-character git commit SHA>
version: 1.5.0-dev
repository: FilipeGCB/cognitive-os
---

# Release Evidence Record

This record is a machine-checkable index of evidence for one exact candidate commit. It is not a claim that the candidate is stable or production-ready.

## Binding contract

The `candidate_sha` is the exact commit whose canonical skill tree, manifests, harness, grader configuration and distribution inputs were tested. Every listed manifest has the same `source_commit`; every artifact has a recorded SHA-256; the execution record includes host-observed run identity and timestamps. A later documentation-only evidence commit may point back to the tested candidate, but it cannot silently promote a different commit.

Required evidence dimensions:

- version and repository;
- canonical skill fingerprint;
- manifests and their hashes;
- eval/harness paths and hashes;
- SUT and grader model(s), with independence flag;
- runtime host(s);
- test counts and critical-gate results;
- Hermes/Work/distribution status;
- telemetry Gate T and collector state;
- known limitations.

Validate with `tools/validate_release_evidence.py`. The release workflow must pass the verified workflow SHA to that validator; Markdown prose alone is insufficient.

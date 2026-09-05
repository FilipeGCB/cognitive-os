---
schema_version: cognitive-os-release-evidence-v1.5
candidate_sha: <40-character git commit SHA>
version: 1.5.0-dev
repository: FilipeGCB/cognitive-os
---

# Release Evidence Record

This record is a machine-checkable index of evidence for one exact candidate commit. It is not a claim that the candidate is stable or production-ready.

## Binding contract

The `candidate_sha` is the exact commit whose canonical skill tree, manifests, harness, grader configuration and distribution inputs were tested. Every listed manifest has the same `source_commit`; every artifact has a recorded SHA-256; the execution record includes host-observed run identity and timestamps. A later documentation-only evidence commit may point back to the tested candidate, but it cannot silently promote a different commit. The behavioral report is normally attached to that evidence commit: its `source_commit`, internal candidate/fingerprint fields and recorded SHA must still match the tested candidate.

Required evidence dimensions:

- version and repository;
- canonical skill fingerprint;
- manifests and their hashes;
- eval/harness paths and hashes;
- SUT and grader model(s), with independence flag;
- runtime host(s);
- test counts and critical-gate results;
- complete candidate-bound V1.5 behavioral conformance evidence, with observed
  remote SUT/grader identities and an independent grader;
- Hermes/Work/distribution status;
- telemetry Gate T and collector state;
- known limitations.

Validate with `tools/validate_release_evidence.py`. The release workflow must pass the exact candidate SHA from the evidence record to that validator and verify that the evidence commit descends from it; Markdown prose alone is insufficient.

The checked-in development record predates the remote-provider policy and is
validated only in historical compatibility mode. A current V1.5 release must
include `behavioral_conformance` with the complete `final` 58-case report,
candidate/eval fingerprints, observed provider identities, and a hashed report
artifact. `INCOMPLETE`, `UNAVAILABLE`, partial selection, unobserved identity,
or implicit local-provider evidence cannot satisfy the release gate.

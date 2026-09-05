# Self-Improvement Governance — Cognitive OS V1.5

Cognitive OS may learn from recurring operational evidence, but it never silently rewrites the active methodology or deploys a change because telemetry reported a problem.

## Active-run immutability

At run start, record a methodology snapshot containing the run ID, skill version, SHA-256 of the canonical skill and hashes of the references/policies used. Pin that snapshot for the active run. A proposed patch is staged, checked for format, references and dependencies, and activated only after the run when the host permits it. A broken reference or dependency is `BLOCKED` and cannot be promoted by the Cognitive OS-controlled path.

Record a mutation ledger entry for every observed change, including whether it occurred during the active run, validation result, affected phases, rollback availability and methodology drift. If the host cannot intercept self-improvement, record `UNKNOWN`/`PARTIAL`, the observed limitation and its impact on `EXECUTION_INTEGRITY`; do not claim enforcement that the adapter cannot provide.

## Evidence-driven improvement queue

The V1.5 telemetry collector maintains a categorical, privacy-preserving improvement queue. The loop is:

```text
sanitized failure event
-> server-derived issue signature
-> observing
-> repeated independent occurrences
-> candidate
-> reproduce / investigate
-> spec or patch proposal
-> tests + review + release evidence
-> accepted/rejected/resolved
```

Only failure/partial/blocking signatures enter the queue. No user-authored text, prompt, response or document content enters this loop.

A matching signature is promoted from `observing` to `candidate` after **3 accepted distinct events**. Duplicate `event_id` values are idempotent and do not increase evidence. The threshold is a triage trigger, not proof that the proposed cause or fix is correct.

`candidate` means “worth investigation.” It does not authorize:

- editing `SKILL.md` or a policy automatically;
- committing or merging code;
- changing a live run;
- installing a newly discovered capability;
- relaxing a privacy/security/consent gate;
- deploying a new version.

A candidate must be reproduced and then handled through the normal decision/spec/TDD/review/promotion path. The resulting change must be bound to its own tests and release evidence before activation.

## Persistent side effects

Persistent side effects are separate from methodology mutation. Use the exact types `SKILL_MUTATED`, `REFERENCE_MUTATED`, `POLICY_MUTATED`, `CONFIG_CHANGED`, `PACKAGE_INSTALLED`, `MCP_INSTALLED`, `CONNECTION_CREATED`, `FILE_CREATED`, `FILE_MODIFIED`, `CREDENTIAL_STATE_CHANGED` and `OTHER_PERSISTENT_SIDE_EFFECT`. “Nothing installed” does not mean “nothing changed”.

## Safety invariant

Telemetry can create evidence for future improvement; it cannot create authorization. Consent, security, review and release gates remain authoritative even when a recurring issue reaches the candidate threshold.

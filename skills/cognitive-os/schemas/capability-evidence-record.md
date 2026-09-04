# Capability Evidence Record — v1.4

## Purpose

Machine-verifiable contract for capability evidence without replacing the Cognitive Run Record.

Truth is scoped to:

```text
host + surface + capability
```

Evidence from one surface is never inherited by another by implication.

## Schema version

`cognitive-os-capability-evidence-v1.4`

## Evidence classes

### runtime_observed

Direct evidence from the current execution. Highest authority for the same host/surface/capability.

Requires a concrete result and non-empty evidence references.

### user_reported

The user reports availability/invocation but direct runtime evidence is not preserved. It may support `REPORTED_*` states but never an unqualified `EXECUTED` claim.

### baseline

Historical/deployment expectation. It helps determine what to inspect but never proves current invocation.

## Fields

- `record_id`: unique string
- `observed_at`: timezone-aware ISO 8601
- `host`: string
- `surface`: string
- `capability`: abstract/stable capability name
- `implementation`: optional concrete implementation
- `evidence_class`: `runtime_observed | user_reported | baseline`
- `availability`: `AVAILABLE | UNAVAILABLE | UNKNOWN`
- `invocation`: `CALLED | NOT_CALLED`
- `result`: result enum or null where allowed
- `declared_state`: optional derived-state assertion
- `evidence_refs`: non-empty list of non-empty strings
- `notes`: optional minimized note without secrets

## Result enum

`SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE`

## Canonical derivation

Runtime observed:

- `AVAILABLE + NOT_CALLED` → `AVAILABLE_NOT_EXERCISED`
- `UNAVAILABLE + NOT_CALLED` → `UNAVAILABLE`
- `UNKNOWN + NOT_CALLED` → `UNKNOWN`
- `CALLED + SUCCESS` → `EXECUTED`
- `CALLED + PARTIAL` → `CALLED_PARTIAL`
- `CALLED + TRUNCATED` → `CALLED_TRUNCATED`
- `CALLED + RATE_LIMITED` → `CALLED_RATE_LIMITED`
- `CALLED + UNAVAILABLE` → `CALLED_UNAVAILABLE`
- `CALLED + BLOCKED` → `CALLED_BLOCKED`
- `CALLED + FAILED` → `CALLED_FAILED`

`EXECUTED` without `CALLED + SUCCESS` is invalid.

Additional coherence rules:

- `SUCCESS`, `PARTIAL`, `TRUNCATED`, `RATE_LIMITED`, `FAILED` require `CALLED`;
- `SUCCESS` requires availability `AVAILABLE`;
- `NOT_APPLICABLE` cannot coexist with `CALLED`;
- baseline cannot claim current invocation.

## Authority and reduction

For the same host/surface/capability:

`runtime_observed > user_reported > baseline`

Within the same evidence class, prefer the latest real timestamp after timezone normalization.

## Security and minimization

Do not record tokens, credentials, cookies, full sensitive payloads, chain-of-thought or raw financial data. Prefer references to a versioned run/transcript marker when sufficient.

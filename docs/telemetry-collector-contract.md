# V1.5 Private Telemetry Collector Contract

This document defines the deployed collector contract for optional Cognitive OS diagnostics.

## Deployment

The V1.5 collector is deployed as a Supabase Edge Function:

```text
POST https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-telemetry
```

The public client still defaults to `OFF`. A deployed endpoint is **not** consent.

The request must include:

```text
Content-Type: application/json
X-Cognitive-OS-Consent: share-approved
X-Cognitive-OS-Policy: cognitive-os-telemetry-policy-v1.5
```

The collector is intentionally usable by an opted-in installation without requiring the user to create a Supabase account. It therefore uses a public HTTP boundary with custom validation rather than user JWT authentication. Database access remains private: direct table access is denied and the Edge Function writes through a service-role-only RPC.

## Untrusted input boundary

Every request is untrusted and may be forged. The deployed collector:

- accepts POST/OPTIONS only;
- requires the explicit-consent and exact policy-version headers;
- accepts JSON only;
- rejects a declared or actual body over 8 KiB;
- accepts only the exact versioned shared-payload allowlist and rejects unknown fields;
- rejects invalid enum/object shapes, run IDs and event IDs;
- rejects free text because no shared payload field can contain arbitrary text;
- stores no application-level IP address, complete User-Agent, fingerprint, tracking cookie or persistent installation ID;
- deduplicates by random `event_id`;
- derives the improvement signature server-side from bounded categories;
- separates detailed events from the improvement queue.

CDN, reverse-proxy or cloud-provider access logs may exist outside the Cognitive OS application tables. The deployment documents this limitation rather than promising that network metadata never exists anywhere in the infrastructure.

## Storage

Application data is isolated in the private Postgres schema:

```text
cognitive_os
```

Tables:

```text
cognitive_os.telemetry_events
cognitive_os.improvement_queue
```

Both tables have RLS enabled. `public`, `anon` and `authenticated` roles have no direct schema/table privileges. The ingestion RPC `public.cognitive_os_ingest_event(...)` is executable only by `service_role`.

### telemetry_events

Stores only the exact sanitized shared payload dimensions plus `received_at`. `event_id` is the idempotency key. The client-provided `run_id` and `event_id` are random, bounded, non-account identifiers.

### improvement_queue

Stores only a SHA-256 issue signature and bounded categorical dimensions:

```text
component | capability | failure_class | result | occurrences | status
```

No user-authored text is accepted.

Only failure/partial/blocking signatures enter the queue. Successful events do not create improvement work.

Queue lifecycle:

```text
observing -> candidate -> accepted/rejected -> resolved
```

A matching issue starts at `observing`. At the third distinct accepted event with the same signature, the database deterministically promotes it to `candidate`. A duplicate `event_id` does not increment the counter.

`candidate` means **investigate/propose a change**, not mutate production. Any change still requires spec/patch, tests, review and normal promotion evidence.

## Retention and aggregation

Default policy:

| Data class | Default retention |
|---|---:|
| Sanitized detailed events | 30 days |
| Improvement/aggregate records | up to 12 months |
| Raw conversation | 0 days |
| Research free text | 0 days |
| Application-stored IP | 0 days |

The ingestion RPC opportunistically removes detailed events older than 30 days. A scheduled maintenance job may be added by the deployment operator without changing the data contract. Increasing retention requires explicit privacy review.

Public aggregate reporting remains allowlisted and must suppress cohorts with `k < 10` by default. The maintainer-only improvement queue is not a public cohort report and contains no user text or account identifier.

## Consent and client state

Shared diagnostics require all of the following:

1. mode `SHARE_PRIVACY_PRESERVING_DIAGNOSTICS`;
2. explicit state `SHARE_APPROVED` for policy `cognitive-os-telemetry-policy-v1.5`;
3. preview of the exact sanitized event;
4. host sender capability;
5. Gate T controls green;
6. HTTPS transport with consent attestation headers.

Decline/revoke keeps product functionality available and blocks future sends.

## Trust boundary

Telemetry is product evidence about reported behavior. It is not automatically security evidence, audit evidence, compliance evidence or proof that a capability really executed on an individual host. It is suitable for identifying recurring product-quality hypotheses that must then be reproduced and tested.

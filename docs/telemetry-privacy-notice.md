# Cognitive OS V1.5 Telemetry Privacy Notice

Status: the diagnostics collector is deployed, but sharing is **explicit opt-in** and defaults to `OFF`. The share choice is never preselected.

Collector endpoint:

`https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-telemetry`

Policy version: `cognitive-os-telemetry-policy-v1.5`.

## Purpose

Optional privacy-preserving events help maintainers understand whether the Cognitive OS runtime reaches its intended capability, research, resilience and decision-state paths and which recurring failures deserve investigation. They are product diagnostics, not proof of a user's security posture, audit result or individual execution.

Refusing diagnostics **does not reduce Cognitive OS functionality**. Installation, capability discovery and normal use continue without shared telemetry.

## Consent

Shared diagnostics require an explicit opt-in after this notice is available to the user. The option must be presented unchecked/off by default. The user may choose local-only diagnostics instead, decline completely, or revoke a previous sharing choice. Revocation blocks future sends; it does not retroactively change already processed aggregates.

The client must preview the exact sanitized payload before the first send under a consent grant. A host that cannot surface the notice, record the policy version, preview the payload, or perform the sender operation must report sharing as `UNAVAILABLE` rather than assuming consent.

## Collected when explicitly shared

Only typed, low-cardinality fields are sent: schema/version; a random non-identifying event ID used for idempotency; a non-identifying random run ID; host/surface category; depth/audit mode; allowlisted capability outcome categories; research and context-compaction buckets; failure booleans; persistent-side-effect boolean; closed feedback enums; decision state; and run status. Custom capability names are represented as categories.

The collector derives a non-identifying issue signature from those categories. Repeated matching failures may create or promote an item in the maintainer improvement queue. The queue contains categories and counters, not user-authored text.

## Never collected by the shared client

Prompts, responses, chain-of-thought/reasoning traces, documents, file content or names, raw paths, private URLs, client/project names, e-mail/PII, credentials, tokens, cookies, detailed research queries, arbitrary free text and raw conversation. Precise client-side timestamps are omitted by default. The application tables do not store IP addresses or User-Agent strings.

## Retention and controls

Sanitized detailed events are retained for a target maximum of 30 days and are opportunistically purged during ingestion. Aggregated improvement records may be retained for up to 12 months. Raw conversation, research free text and application-stored IP retention are zero.

Infrastructure providers may produce transient security/access logs outside the Cognitive OS application tables; those provider-level limits are governed by the deployment infrastructure and are not represented as Cognitive OS diagnostic fields.

Sharing can be revoked at any time in a supporting host by returning the telemetry consent state to `REVOKED`/`OFF`. A deployment-side deletion request can only target records for which the requester has retained the non-identifying event/run receipt; no account identity is collected to look records up by person.

Contact: use the maintainer contact published in the Cognitive OS repository or Plugin Directory listing.

## Improvement queue and self-improvement limitation

Telemetry does not silently rewrite or redeploy Cognitive OS. Repeated sanitized issue signatures can become improvement candidates. Any resulting spec/code/policy change remains subject to normal review, tests, evidence and release gates before promotion.

## Limitations

This notice describes the public client's observable controls. It cannot eliminate transient provider or network metadata outside the application store, and it does not make an automatic LGPD/GDPR or other legal-compliance claim.

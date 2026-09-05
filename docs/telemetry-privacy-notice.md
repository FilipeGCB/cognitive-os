# Cognitive OS V1.5 Telemetry Privacy Notice

Status: public client is opt-in and defaults to `OFF`; no collector endpoint is
enabled by this repository at development time.

## Purpose

Optional privacy-preserving events help maintainers understand whether the
Cognitive OS runtime reaches its intended capability, research, resilience and
decision-state paths. They are product diagnostics, not proof of a user's
security posture, audit result or individual execution.

## Collected when explicitly shared

Only typed, low-cardinality fields are sent: schema/version; a random
non-identifying event ID used for idempotency; a non-identifying random run ID;
host/surface category; depth/audit mode; allowlisted capability outcome
categories; research and context-compaction buckets; failure booleans;
persistent-side-effect boolean; closed feedback enums; decision state; and run
status. Custom capability names are represented as categories.

## Never collected by the shared client

Prompts, responses, reasoning traces, documents, file content or names, raw
paths, private URLs, client/project names, e-mail/PII, credentials, tokens,
cookies, detailed research queries, arbitrary free text and raw conversation.
Precise timestamps are omitted by default.

## Retention and controls

The configured policy defaults to 30 days for sanitized detailed events, 12
months for aggregates, and zero for raw conversation, research free text and
application-stored IP. A deployment may shorten retention. Infrastructure
providers may produce transient access logs outside the application store;
those limits depend on deployment configuration and are not silently promised
away by this client.

Sharing requires a preview and explicit consent, can be revoked, and is never
required to use Cognitive OS. If deletion is offered by a future collector, the
deployment must document its receipt-based mechanism and contact channel.

Contact: use the maintainer/deployment contact published with the endpoint.

## Limitations

This notice describes the public client's observable controls. It cannot
eliminate transient provider or network metadata outside the application
store, and it does not make an automatic LGPD/GDPR or other legal-compliance
claim.

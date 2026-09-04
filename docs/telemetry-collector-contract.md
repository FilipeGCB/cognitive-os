# V1.5 Private Telemetry Collector Contract

This document defines the deployment contract for an optional private
collector. It is not an implementation of a public endpoint, and the public
Cognitive OS repository does not enable a destination by default.

## Endpoint

The logical route is:

```text
POST /v1/telemetry/events
```

The host, credentials and deployment URL are external configuration. The
public core must not hardcode a secret or require this endpoint to complete a
run.

## Untrusted input boundary

Every request is untrusted and may be forged. The collector must:

- accept only the versioned shared-payload schema and reject unknown fields;
- reject free text, prompts, responses, documents, paths, URLs, PII, secrets,
  cookies, tokens and conversation content;
- enforce a bounded request size before application-level persistence;
- validate the `event_id` and deduplicate/reject replayed events with an
  idempotency policy;
- apply a second-pass sanitizer before storing anything;
- rate-limit and abuse-protect at the edge without storing those edge metadata
  fields in the application event store;
- separate detailed events from aggregate metrics.

The application event store must not persist IP addresses, complete User-Agent
strings, fingerprints, tracking cookies or persistent installation IDs. The
`run_id` and `event_id` supplied by the client are random, bounded and
non-identifying; they are not account identifiers.

CDN, reverse-proxy or cloud-provider access logs may exist outside the
application boundary. The deployment must document and minimize that
limitation rather than promise that an IP can never exist anywhere in the
infrastructure.

## Retention and aggregation

Default policy:

| Data class | Default retention |
|---|---:|
| Sanitized detailed events | 30 days |
| Aggregates | 12 months |
| Raw conversation | 0 days |
| Research free text | 0 days |
| Application-stored IP | 0 days |

Retention is configurable only through an explicit privacy review. Aggregate
dimensions are allowlisted and bounded. The default k-anonymity-style
suppression threshold is `k >= 10`; small or rare combinations are suppressed,
custom names cannot become dimensions and arbitrary `group by` is forbidden.

If individual deletion is offered, it must use a non-identifying receipt or
deletion token and document the mechanism, retention boundary and contact
channel.

## Trust boundary

Telemetry is product evidence about reported behavior. It is not automatically
security evidence, audit evidence, compliance evidence or proof that a
capability really executed on an individual host.

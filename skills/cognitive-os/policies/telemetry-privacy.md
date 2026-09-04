# Telemetry Privacy Policy — Cognitive OS V1.5

This policy governs the optional Flight Recorder and shared diagnostic event.
The public default is `OFF`. Telemetry is product evidence, not security,
audit, compliance or individual execution evidence.

## Modes and consent

- `OFF`: no persistence or sharing is attempted.
- `LOCAL_DIAGNOSTICS`: a sanitized, typed trace may be persisted only when the
  host exposes persistence.
- `SHARE_PRIVACY_PRESERVING_DIAGNOSTICS`: sharing is available only when the
  host exposes preview, explicit consent and outbound sending, the endpoint is
  HTTPS, and the deployment has passed Gate T.

Consent is explicit, separate from capability/installation consent, revocable,
never preselected, and versioned against this policy. A refusal is not nagged.
Lack of host UI or outbound capability leaves sharing `UNAVAILABLE`.

## Constructed fields

The shared event is constructed only from an allowlist: schema/version, a
random non-identifying event ID for idempotency, a non-identifying run ID, host
and surface class, depth, audit flag, capability category outcomes,
research/compaction buckets, failure booleans, persistent-change boolean,
closed feedback enums, decision state and run status. Custom skills, MCPs,
connectors, private repositories and client systems are reduced to
`custom_capability` or an equivalent category.

The shared client rejects unknown fields, invalid enums and oversized payloads.
Sanitization is a second defense, not permission to capture unrestricted input.

## Excluded fields

Never share or persist in the shared event: user prompts, assistant responses,
chain-of-thought, reasoning traces, documents, file contents, private
filenames/paths/URLs, client/project names, e-mails, PII, credentials, tokens,
cookies, detailed research queries or arbitrary free text. Shared payloads do
not contain precise timestamps by default.

Detailed local traces and forensic bundles have separate contracts and are not
uploaded automatically.

## Retention and operation

The public defaults are 30 days for sanitized detailed events, 12 months for
aggregates, and zero days for raw conversation, research free text and
application-stored IP. Any deployment may reduce these values; increasing
retention requires a separate privacy review. Infrastructure/CDN/provider
access logs may be produced outside the application boundary and must be
documented and minimized by the deployment operator.

Users may revoke sharing locally at any time. Deletion is deployment-specific;
where an enabled collector offers event deletion it must expose a
non-identifying receipt/deletion token and document the mechanism.

## Contact and limitations

Privacy questions and deletion requests should use the contact channel supplied
by the deployment. This notice describes controls; it does not, by itself,
claim LGPD, GDPR or any other legal compliance.

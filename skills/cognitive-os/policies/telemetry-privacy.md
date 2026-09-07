# Telemetry Privacy Policy — Cognitive OS V1.5

This policy governs the optional Flight Recorder and shared diagnostic event. The public default is `OFF`. Telemetry is product evidence, not security, audit, compliance or individual execution evidence.

Collector:

`https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-telemetry`

Policy version: `cognitive-os-telemetry-policy-v1.5`.

## Modes and consent

- `OFF`: no persistence or sharing is attempted.
- `LOCAL_DIAGNOSTICS`: a sanitized, typed trace may be persisted only when the host exposes persistence.
- `SHARE_PRIVACY_PRESERVING_DIAGNOSTICS`: sharing is available only when the host exposes preview, explicit consent and outbound sending, the endpoint is HTTPS, and Gate T has passed.

Consent is explicit, separate from capability/installation consent, revocable, versioned and **never preselected**. The share option defaults unchecked/OFF. Declining or revoking diagnostics causes no Cognitive OS feature loss and must not trigger repeated nagging. Lack of host consent UI, preview or outbound capability leaves sharing `UNAVAILABLE`.

A transport send must attest the already-approved consent state using:

```text
X-Cognitive-OS-Consent: share-approved
X-Cognitive-OS-Policy: cognitive-os-telemetry-policy-v1.5
```

The collector independently rejects a request without both values. Headers attest the client-side consent checkpoint; they do not replace the host's duty to present the notice and obtain the user's affirmative choice.

## Constructed fields

The shared event is constructed only from an allowlist: schema/version, random non-identifying event/run IDs, host and surface class, depth, audit flag, capability category outcomes, research/compaction buckets, failure booleans, persistent-change boolean, closed feedback enums, decision state and run status. Custom skills, MCPs, connectors, private repositories and client systems are reduced to bounded categories.

The client and collector both reject unknown fields, invalid enums and oversized payloads. Sanitization is defense in depth, not permission to capture unrestricted input.

Before the first send for an event, show the actual bounded preview object and obtain explicit consent for the current policy version. An endpoint existing is not consent and a preview is not a send.

Public aggregates use only allowlisted dimensions and suppress every cohort with `k < 10` by default. The maintainer-only improvement queue is categorical and does not expose user cohorts publicly.

## Excluded fields

Never share or persist in the shared event: user prompts, assistant responses, chain-of-thought/reasoning traces, documents, file contents, private filenames/paths/URLs, client/project names, e-mails, PII, credentials, tokens, cookies, detailed research queries or arbitrary free text. Shared payloads do not contain precise client-side timestamps by default.

The application event store does not persist IP addresses, complete User-Agent strings, fingerprints, tracking cookies or persistent installation IDs. Infrastructure providers can still create transient network/security logs outside the application tables.

Detailed local traces and forensic bundles have separate contracts and are not uploaded automatically.

## Retention and operation

The deployed policy is 30 days for sanitized detailed events, up to 12 months for categorical improvement/aggregate records, and zero application retention for raw conversation, research free text and IP. Increasing retention requires a separate privacy review.

Users may revoke sharing locally at any time. `REVOKED` clears the client's preview authorization and blocks future sends. Already processed anonymous aggregates are not retroactively tied to an account because no account identity is collected.

## Improvement loop

Repeated sanitized failure signatures may enter `cognitive_os.improvement_queue`. At three accepted distinct events with the same bounded signature, the queue may promote the issue from `observing` to `candidate`. A candidate authorizes investigation only; it does not authorize a silent skill/code mutation or deployment.

## Contact and limitations

Privacy questions and deletion requests should use the maintainer contact supplied by the repository or plugin listing. This policy describes controls; it does not, by itself, claim LGPD, GDPR or any other legal compliance.

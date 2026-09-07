# Cognitive OS V1.5 — Telemetry Collector Deployment Evidence

Date: 2026-09-05

## Deployment

- Supabase project ref: `wsqumhrcdwgoskolziuy`
- Edge Function: `cognitive-os-telemetry`
- endpoint: `https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-telemetry`
- deployed function status observed: `ACTIVE`
- deployed function version after receipt hardening: `2`
- application schema: `cognitive_os`
- direct `public`, `anon` and `authenticated` table access: revoked
- ingestion RPC: service-role only

## Real HTTP smoke

The initial shell sandbox could not resolve external DNS, so the endpoint was exercised from the Supabase database through the `http` extension instead of treating a local-network failure as product evidence.

### Consent rejection

A POST without `X-Cognitive-OS-Consent` returned:

```text
HTTP 403
{"error":"explicit_opt_in_required"}
```

Result: PASS — a deployed endpoint alone cannot accept shared diagnostics.

### Valid ingestion

Three distinct schema-valid events were sent with:

```text
X-Cognitive-OS-Consent: share-approved
X-Cognitive-OS-Policy: cognitive-os-telemetry-policy-v1.5
```

Each request returned HTTP `202`. Database verification observed three distinct stored event IDs.

Result: PASS — consent-attested, allowlisted shared events reached the application store.

### Improvement queue

The three smoke events deliberately shared the same bounded failure signature:

```text
component     = capability
capability    = external_mcp_discovery
failure_class = failed
result        = failed
```

Database verification observed:

```text
occurrences = 3
status      = candidate
```

Result: PASS — three accepted distinct events promote the bounded signature from `observing` to `candidate`.

### Idempotency receipt

A materialized HTTP smoke against a new event returned:

```json
{
  "accepted": true,
  "duplicate": false,
  "queue_status": "candidate",
  "receipt": "EVT-000000000000000000000106"
}
```

A repeated event ID is stored only once and does not add evidence to the queue.

## Privacy boundary exercised

The deployed Edge Function accepts only the exact categorical V1.5 shared payload contract, enforces an 8 KiB request limit and consent/policy headers, derives the improvement signature server-side, and writes through a private service-role database boundary. Application tables do not include prompt/response/document/free-text/private-path/credential/token/cookie/client-name/project-name/IP/User-Agent/fingerprint fields.

## Self-improvement boundary

`candidate` is a maintainer investigation state. The smoke did not mutate the skill, repository or deployment. Any later improvement remains subject to reproduction, spec/patch, tests, review and promotion evidence.

## Test-data handling

The synthetic smoke records use clearly artificial CRR/event IDs and are deleted after this evidence is recorded so the real improvement queue starts without test pollution.

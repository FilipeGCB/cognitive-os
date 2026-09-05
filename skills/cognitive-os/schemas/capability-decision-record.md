---
id: CAP-YYYYMMDD-HHMMSS-XXXX
schema_version: cognitive-os-capability-decision-v1.5
status: proposed
capability: <abstract capability>
source: <repo/url/provider>
version_or_sha: <pin|n/a>
reviewed_at: YYYY-MM-DDTHH:MM:SSZ
reviewed_by: <string>
---

# Capability Decision Record

## Purpose

Canonical Gauntlet/governance record for a new or persistent capability. It records a decision; it does **not** implement runtime enforcement or prove runtime availability.

## Status

`proposed | test | quarantine | approved | rejected | blocked | continue-research | superseded`

`approved` means approved only within the recorded conditions. It does not mean installed, available, invoked or technically enforced.

## Completeness

For formal promotion or Full Flow/Audit:

- fill every material field;
- unobserved material information = `UNKNOWN`;
- sensitive capabilities cannot be `approved` with critical `UNKNOWN` in security, permissions/read-write, credentials/data access or preflight;
- distinguish provider documentation from behavior/tool surface actually observed.

## Need **[required]**

## Capability evaluated **[required]**

## Origin / officiality / maturity **[required]**

Record repository/provider and `GA | beta | preview | experimental | UNKNOWN` when material and observable.

## Value **[required]**

## Security **[required]**

Include proportional evidence about authentication, secret handling, isolation, external-content/tool-poisoning surface and known limitations.

## License / provenance **[required]**

If material and not observed: `UNKNOWN`.

## Permissions and read/write surface **[required]**

Record scopes/actions, mutations and technical ability to restrict write when relevant.

## Credentials / data accessed **[required]**

## Supply chain / dependencies **[required]**

## Maintenance / update model **[required]**

## Overlap with existing capabilities **[required]**

## Portability **[required]**

## Observability **[required]**

## Reversibility **[required]**

## Operational cost / footprint **[required]**

## Official/native/API alternative **[required when applicable]**

Do not assume MCP is better than REST/API or a native host feature.

## Preflight required **[required]**

Define the technical evidence required before promotion/use.

## Decision **[required]**

`test | quarantine | approved | rejected | blocked | continue-research`

## Conditions / limits of use **[required]**

## Material unknowns **[required]**

Use `none` only with sufficient evidence.

## Evidence / references **[required]**

For mutable external claims, record date/ref/version when material.

## V1.5 machine fields

The Markdown record remains the human-readable contract. The executable companion `capability-decision-record.schema.json` requires these fields and rejects unknown fields:

```yaml
id: CAP-YYYYMMDD-XXXX
schema_version: cognitive-os-capability-decision-v1.5
capability: <abstract capability>
discovery_class: EXISTING_CAPABILITY | LOCAL_SKILL_DISCOVERY | LOCAL_TOOL_DISCOVERY | LOCAL_CONNECTOR_DISCOVERY | EXTERNAL_SKILL_DISCOVERY | EXTERNAL_MCP_DISCOVERY | MANUAL_FALLBACK
source_or_adapter: <host or adapter>
candidate_provenance:
  source: <bounded source ref>
  provenance_class: HOST_OBSERVED | TOOL_OBSERVED | REPOSITORY_OBSERVED | USER_SUPPLIED | UNKNOWN
availability: AVAILABLE | UNAVAILABLE | UNKNOWN
auth_state: NOT_REQUIRED | REQUIRED_NOT_AUTHENTICATED | AUTHENTICATED | UNKNOWN
run_consent_state: NOT_REQUIRED | NOT_ASKED | NOT_GRANTED | DECLINED | GRANTED | REVOKED
invocation: CALLED | NOT_CALLED
result: SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE
consent_required: true
adoption_state: DISCOVERED | INSPECTED | REJECTED | TEST_APPROVED | PERSISTENT_ADOPTION_PENDING_CONSENT | APPROVED | QUARANTINED | UNAVAILABLE | BLOCKED
evidence_refs: [run://...]
```

`AVAILABLE`, `AUTHENTICATED` and `APPROVED` are not run consent. A capability that requires consent can only be `CALLED` with `run_consent_state: GRANTED`; a successful result requires runtime evidence references. Find Skills/Find MCP are represented as discovery assets and never as the candidate capability they discover.

For a read-only local capability that is available within observed host
permissions and does not cross an account or sensitive boundary, use
`run_consent_state: NOT_REQUIRED`; unrelated external-account or installation
consent must not block that use. This exception does not apply to external,
account-bound, persistent or consequential capabilities.

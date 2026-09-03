---
id: CAP-YYYYMMDD-HHMMSS-XXXX
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

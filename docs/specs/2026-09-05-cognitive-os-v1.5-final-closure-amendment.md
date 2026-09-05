# SPEC Amendment — Cognitive OS V1.5 Final Product Closure

**Status:** APPROVED / authoritative for final V1.5 closure  
**Date:** 2026-09-05  
**Amends:** `docs/specs/2026-09-04-cognitive-os-v1.5-public-final.md`

## Purpose

This amendment records final product decisions made after the 2026-09-04 V1.5 spec. Where this document conflicts with the earlier V1.5 spec, this amendment wins. It does not open a new feature cycle; it closes obligations already discussed with the project owner.

Detailed implementation design: `docs/superpowers/specs/2026-09-05-v1.5-product-closure-distribution-design.md`.

## 1. Find Skills and Find MCP are mandatory concrete discovery capabilities

For V1.5, the approved identities are no longer intentionally abstract/unproven.

### Find Skills

```text
repository: https://github.com/vercel-labs/skills
owner: vercel-labs
skill: find-skills
CLI pin: skills@1.5.23
release reference: v1.5.23
license: MIT
```

### Find MCP

```text
repository: https://github.com/modelcontextprotocol/registry
authority: Official MCP Registry
production API: https://registry.modelcontextprotocol.io/v0.1/servers
release reference: v1.7.9
license: Apache-2.0/MIT
```

For supported local Agent Skills hosts, a **complete Cognitive OS installation** must establish both discovery capabilities. The explicit installer may install the approved lightweight Find Skills dependency after the user accepts the disclosed Cognitive OS installation bundle. The bundled Find MCP client travels inside the Cognitive OS skill and performs read-only Official MCP Registry search.

This installation-time rule does not authorize any candidate later discovered by either mechanism. Candidate provenance/Gauntlet/permission/consent rules remain unchanged.

Cloud hosts such as ChatGPT cannot pretend to install software on the user's computer. They must package equivalent discovery behavior in their supported plugin/app surface and declare unavailable local-machine behavior honestly.

This supersedes earlier wording that treated exact discovery-asset identity as intentionally optional/unproven for V1.5.

## 2. Telemetry collector is a delivered V1.5 capability

The private collector is no longer a hypothetical or optional deployment item.

V1.5 includes:

- deployed HTTPS collector;
- strict shared-payload allowlist;
- explicit versioned consent;
- preview-before-send contract;
- share option OFF/unchecked by default;
- revocation for future sends;
- private application store with no direct public table write access;
- bounded improvement queue;
- real ingestion/consent smoke evidence.

Production collector:

```text
https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-telemetry
```

Supabase is a replaceable hosting/storage adapter for this deployed service and is not part of the Cognitive OS reasoning core.

Absence or outage of telemetry must never break normal Cognitive OS reasoning. Sharing remains optional even though the collector is deployed.

## 3. Consent UX

Optional diagnostic sharing requires affirmative opt-in. The checkbox must be unchecked by default. Installation consent and telemetry consent are separate decisions.

A supporting host must expose:

- purpose;
- exact bounded preview;
- categories collected;
- categories never collected;
- retention;
- privacy notice;
- ability to decline without feature loss.

No dark-pattern preselection is permitted.

## 4. Evidence-driven self-improvement

The telemetry improvement loop is part of V1.5, but silent self-mutation is not.

```text
sanitized failure event
-> bounded issue signature
-> observing
-> 3 distinct matching events
-> candidate
-> reproduce/investigate
-> spec/patch
-> tests/review
-> promotion
```

`candidate` never authorizes automatic edit, commit, merge, install or deploy.

## 5. Distribution surfaces

V1.5 closes three product-distribution families:

1. Agent Skills/local hosts;
2. Claude plugin packaging;
3. OpenAI Plugin packaging for ChatGPT/Codex.

### Claude

The repository must contain a valid Claude plugin/marketplace declaration and prove it with the current pinned Claude Code CLI in CI. Find Skills must resolve as an installation dependency where supported.

### OpenAI

The repository must contain:

```text
.codex-plugin/plugin.json
.mcp.json
skills/cognitive-os/
integrations/chatgpt-plugin/
chatgpt-app-submission.json
```

The OpenAI MCP app service may host only narrowly scoped product-supporting operations. V1.5 currently permits:

- `find_mcp`;
- `telemetry_status`;
- `render_telemetry_consent`;
- `submit_diagnostic`.

No general shell, filesystem, arbitrary HTTP, arbitrary candidate execution or arbitrary installation surface is part of the OpenAI plugin.

## 6. Hermes is a compatibility host, not a product dependency

Hermes is not part of Cognitive OS and users do not need Hermes to install or use Cognitive OS.

A Hermes E2E is useful compatibility evidence when the Hermes runtime is available. Hermes availability does not block the core release unless the release explicitly makes a Hermes-verified support claim.

The same rule applies to host-specific features generally: claims must follow evidence, but one unavailable host cannot become an accidental universal dependency.

## 7. Release claims

The stable V1.5 core still requires fresh remote behavioral conformance using an explicit remote SUT and independent remote grader, with no local-model fallback and evidence bound to the final candidate.

Host/directory states must be expressed separately:

```text
CORE_RELEASED
HOST_INSTALL_VALIDATED
HOST_E2E_VALIDATED
PLUGIN_SUBMISSION_READY
PLUGIN_SUBMITTED
PLUGIN_APPROVED/PUBLISHED
```

A repository can truthfully be `PLUGIN_SUBMISSION_READY` before an external directory finishes review. It may not claim `PLUGIN_APPROVED/PUBLISHED` until the platform reports that state.

## 8. Scope freeze after this amendment

After the obligations above are implemented, V1.5 accepts only:

- failed-gate fixes;
- security/correctness fixes;
- evidence/claim corrections;
- final host smoke wiring;
- stable version/release metadata.

Everything else is V1.6+.

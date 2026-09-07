# SPEC Amendment — Cognitive OS V1.5 Final Product Closure

**Status:** APPROVED / authoritative for final V1.5 closure  
**Date:** 2026-09-05  
**Amends:** `docs/specs/2026-09-04-cognitive-os-v1.5-public-final.md`

## Purpose

This amendment records final product decisions made after the 2026-09-04 V1.5 spec. Where this document conflicts with the earlier V1.5 spec, this amendment wins. It does not open a new feature cycle; it closes obligations already discussed with the project owner.

Detailed implementation design: `docs/superpowers/specs/2026-09-05-v1.5-product-closure-distribution-design.md`.

Authoritative product-boundary clarification: `docs/architecture/cognitive-os-product-boundary-v1.5.md`.

## 1. Cognitive OS is the product/system; the Agent Skill is its portable cognitive core

Cognitive OS must not be described as if the whole product were only `skills/cognitive-os/`.

The V1.5 architecture is:

```text
Cognitive OS product/system
├── portable cognitive core -> Agent Skill
├── capability layer -> native host capabilities + Find Skills + Find MCP + grounded corpus and other approved capabilities
├── adapters/integrations -> host adapters, connectors and MCP/app execution surfaces
├── product services -> privacy-preserving telemetry/improvement queue
└── distribution -> Agent Skill/local bundle + OpenAI plugin + Claude plugin
```

A functionality can be a first-class Cognitive OS capability without its implementation living physically inside the skill. The skill owns the portable reasoning, routing, policy, evidence and consent contracts; the host/adapters/MCPs/services supply execution where external or account-bound capability is required.

Examples:

- internet research is Cognitive OS functionality while the network/search implementation may be host-native;
- Grounded Corpus Research is Cognitive OS functionality while NotebookLM is one first-class adapter/implementation, not a mandatory core dependency;
- Find MCP may be executed by the bundled read-only client or an equivalent plugin/MCP surface;
- shared diagnostics are Cognitive OS functionality while collection is performed by the optional external telemetry service.

This is a terminology/product-boundary correction, not a V1.5 feature expansion and not a move to a centralized Cognitive OS SaaS/runtime.

## 2. Find Skills and Find MCP are mandatory concrete discovery capabilities

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

## 3. Telemetry collector is a delivered V1.5 capability

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

## 4. Consent UX

Optional diagnostic sharing requires affirmative opt-in. The checkbox must be unchecked by default. Installation consent and telemetry consent are separate decisions.

A supporting host must expose purpose, exact bounded preview, categories collected/never collected, retention, privacy notice and ability to decline without feature loss.

No dark-pattern preselection is permitted.

## 5. Evidence-driven self-improvement

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

## 6. Distribution surfaces

V1.5 closes three product-distribution families:

1. Agent Skills/local hosts;
2. Claude plugin packaging;
3. OpenAI Plugin packaging for ChatGPT/Codex.

The repository is the canonical source of the entire Cognitive OS product, including the portable skill, adapters, integrations, product services and distribution manifests. The user-facing plugin installation may occur inside the target platform; that does not make the plugin's source/versioning cease to live in the repository.

### Claude

The repository must contain a valid Claude plugin/marketplace declaration and prove it with the pinned Claude Code CLI in CI. Find Skills must resolve as an installation dependency where supported.

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

## 7. ChatGPT plugin does not require an inference API key

Creating, testing, submitting, approving or installing the ChatGPT/Codex plugin does **not** inherently require an OpenAI inference API key.

The plugin may package a skill and optionally a connected app/MCP surface. ChatGPT/Codex supplies the host model/runtime; the plugin author does not need to buy OpenAI API inference merely because the plugin exists.

The repository retains `.github/workflows/conformance.yml` only as an **optional maintainer QA harness** for explicit remote SUT + independent grader testing when someone intentionally chooses to spend remote API quota. It:

- is not a Plugin Directory requirement;
- is not a V1.5 release blocker;
- has no provider/model defaults;
- never falls back to a local model;
- may be used later as additional evidence.

This section supersedes prior closure wording that accidentally converted optional remote API conformance into a mandatory plugin/release dependency.

## 8. Hermes is a compatibility host, not a product dependency

Hermes is not part of Cognitive OS and users do not need Hermes to install or use Cognitive OS.

A Hermes E2E is useful compatibility evidence when the Hermes runtime is available. Hermes availability does not block the core release unless the release explicitly makes a Hermes-verified support claim.

The same rule applies to host-specific features generally: claims must follow evidence, but one unavailable host cannot become an accidental universal dependency.

## 9. Release claims

Host/directory states are expressed separately:

```text
CORE_RELEASED
HOST_INSTALL_VALIDATED
HOST_E2E_VALIDATED
PLUGIN_SUBMISSION_READY
PLUGIN_SUBMITTED
PLUGIN_APPROVED/PUBLISHED
```

A repository can truthfully be `PLUGIN_SUBMISSION_READY` before an external directory finishes review. It may not claim `PLUGIN_APPROVED/PUBLISHED` until the platform reports that state.

For ChatGPT specifically:

- use `HOST_E2E_VALIDATED` only after a real host smoke on the actual ChatGPT surface;
- otherwise use `PLUGIN_SUBMISSION_READY / HOST_SMOKE_PENDING` if package/MCP/submission evidence is complete.

The stable V1.5 core requires truthful deterministic/privacy/distribution evidence and release metadata, not a paid model-API run.

## 10. Scope freeze after this amendment

After the obligations above are implemented, V1.5 accepts only:

- failed-gate fixes;
- security/correctness fixes;
- evidence/claim corrections;
- final host smoke wiring;
- stable version/release metadata.

Everything else is V1.6+.

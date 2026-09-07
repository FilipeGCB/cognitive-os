# Cognitive OS V1.5 — Product Boundary

**Status:** authoritative architecture clarification for V1.5  
**Date:** 2026-09-05  
**Scope:** terminology/product-boundary correction only; no new feature scope

## Decision

Cognitive OS is a **host-neutral product/system** whose portable cognitive core is implemented as an **Agent Skill**.

The Agent Skill is therefore the canonical cognitive core, but it is **not the whole product**.

A Cognitive OS capability may be implemented by the skill itself, by a host-native capability, by an adapter, by an MCP/app connection, or by an optional external service. Product capability and physical code location are intentionally distinct concepts.

## Canonical model

```text
COGNITIVE OS — product/system
│
├── Cognitive Core
│   └── skills/cognitive-os/
│       methodology, reasoning workflows, policies, schemas,
│       capability-selection logic, evidence discipline and closure rules
│
├── Capability Layer
│   ├── native host capabilities (web, files, connected sources, etc.)
│   ├── Find Skills
│   ├── Find MCP
│   ├── Grounded Corpus / NotebookLM adapter
│   └── other approved capabilities discovered or supplied by a host
│
├── Adapter / Integration Layer
│   ├── adapters/
│   ├── integrations/
│   └── MCP/app connections where remote/account-bound execution is required
│
├── Product Services
│   ├── telemetry/
│   └── deployed diagnostics/improvement-queue service
│
└── Distribution Layer
    ├── portable Agent Skill/local bundle
    ├── OpenAI ChatGPT/Codex plugin packaging
    └── Claude plugin packaging
```

## What belongs inside the Skill

The skill owns the portable cognitive contract:

- when and how to reconstruct context;
- evidence/inference/assumption/unknown discipline;
- research and capability-routing policy;
- Sensemaking, Outside View, Diagnosis, Gauntlet/decision challenge, Value of Information, robustness and stop discipline;
- rules for deciding whether a capability is needed;
- safety, provenance, permission and consent policy;
- output/decision contracts and runtime-truth semantics.

The skill may also ship deterministic helper scripts when those helpers are portable and safe to bundle, such as the read-only Find MCP client.

## What does not need to live inside the Skill

A functionality can still be a first-class Cognitive OS capability even when execution is supplied elsewhere.

Examples:

| Cognitive OS functionality | Portable product contract | Possible execution surface |
|---|---|---|
| Web research | decide when/what to research; source/evidence policy | host-native web capability |
| Find Skills | discovery policy + approved dependency contract | bundled/host skill discovery |
| Find MCP | discovery policy + read-only client contract | bundled script or plugin/MCP service |
| Grounded Corpus Research | decide when grounded corpus is required; consent rules | NotebookLM adapter/MCP or another compatible corpus system |
| GitHub/Drive/connected data | capability selection + permission/consent rules | host connector/app/MCP |
| Shared diagnostics | bounded event contract + opt-in policy | telemetry client + external collector |
| Consent UI | consent contract | host/plugin UI surface |

Therefore, **“functionality of Cognitive OS” does not mean “code must be physically inside `skills/cognitive-os/`.”**

## Host-neutral capability resolution

Cognitive OS asks for a capability by purpose, not by vendor.

Example:

```text
Need: grounded corpus research
        ↓
Host A: NotebookLM adapter
Host B: native knowledge/corpus tool
Host C: approved MCP/RAG provider
```

NotebookLM can be a first-class implementation without becoming a mandatory dependency of the cognitive core.

Likewise, internet research is part of the product behavior even though the actual network/search tool is normally supplied by the host.

## Relationship to VPS

Cognitive OS is a software product/system in the architectural sense, like VPS, but its runtime model is different.

VPS owns a larger dedicated execution runtime. Cognitive OS deliberately keeps the cognitive core portable and lets approved host capabilities/adapters/services provide execution surfaces.

V1.5 does **not** introduce a centralized Cognitive OS SaaS/runtime. A future dedicated runtime could be added later without changing this product boundary, but it is outside V1.5.

## Distribution consequence

The repository remains the canonical source of the whole product, not only the skill:

```text
skills/          portable cognitive core
adapters/        capability/host adapters
integrations/    remote/plugin integration code
telemetry/       diagnostic client/contracts
distribution/    packaging by target
.codex-plugin/   OpenAI plugin metadata
.claude-plugin/  Claude plugin metadata
.mcp.json        declared OpenAI MCP connection
```

For end users, distribution may expose only the surface appropriate to the host. Installing the OpenAI or Claude plugin does not mean every Cognitive OS component is physically copied into the chat client; the plugin packages/references the necessary skill and integration surfaces.

## Non-goals / unchanged decisions

This clarification does not:

- turn Cognitive OS into a centralized hosted SaaS;
- make Supabase, NotebookLM, Hermes or any single vendor part of the reasoning core;
- add new capabilities to V1.5;
- weaken capability-state truthfulness (`AVAILABLE/UNAVAILABLE/UNKNOWN`, invocation and result states);
- authorize discovered skills/MCPs without provenance, Gauntlet, permissions and consent;
- change telemetry's OFF-by-default explicit opt-in model.

## One-sentence product definition

> **Cognitive OS is a host-neutral decision and research system whose portable cognitive core is an Agent Skill and whose external capabilities are resolved through host-native tools, approved adapters/MCPs and optional product services.**

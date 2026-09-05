# OpenAI distribution — ChatGPT and Codex

Canonical cognitive runtime: [`skills/cognitive-os`](../../skills/cognitive-os).

Verified against current OpenAI developer documentation on 2026-09-05.

## Product model

OpenAI currently exposes **Plugins** as the extension surface for ChatGPT and Codex, combining skills, MCP servers and optional UI. Cognitive OS uses that model directly: the reasoning methodology stays in the portable skill, while only capabilities that need a remotely reachable execution surface are exposed through a narrow MCP service.

The OpenAI package therefore has three pieces:

```text
skills/cognitive-os/                     portable reasoning core
.codex-plugin/plugin.json                plugin manifest
.mcp.json                                production MCP endpoint declaration
integrations/chatgpt-plugin/             MCP + consent UI source/evidence
```

Public Plugin Directory approval is an external platform state and is never implied merely because these artifacts exist.

## Current V1.5 architecture

### Skill

The canonical Cognitive OS reasoning workflow remains [`skills/cognitive-os`](../../skills/cognitive-os). It is not reimplemented in the MCP service.

### MCP service

Production endpoint:

```text
https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-plugin-mcp
```

The endpoint currently exposes four bounded tools:

- `find_mcp` — read-only discovery against the Official MCP Registry; it does not install or execute candidates;
- `telemetry_status` — reports the optional diagnostics policy and what is never collected;
- `render_telemetry_consent` — renders the exact bounded diagnostic and an unchecked opt-in control; rendering itself sends nothing;
- `submit_diagnostic` — sends one sanitized diagnostic only after explicit opt-in for the V1.5 policy.

There is no general shell, filesystem, arbitrary HTTP, arbitrary MCP execution or capability-installation tool in this service.

### Telemetry consent UI

The widget resource is:

```text
ui://cognitive-os/telemetry-consent-v1.html
```

Its checkbox is unchecked by default. The send button remains disabled until the user affirmatively checks it. The widget previews the exact bounded diagnostic, links to the privacy notice and calls only the declared `submit_diagnostic` tool through the ChatGPT tool bridge. Refusal causes no feature loss.

The widget has no wildcard CSP and no direct external-network dependency.

## Real protocol evidence

On 2026-09-05 the deployed MCP endpoint was exercised over real HTTPS/Streamable HTTP:

1. MCP `initialize` returned HTTP 200 and server `cognitive-os` / `1.5.0-dev`;
2. `tools/list` returned the declared tool descriptors and explicit review annotations;
3. `telemetry_status` returned `defaultMode=OFF`, `explicitOptInRequired=true` and `preselectedConsent=false`;
4. `find_mcp` queried the Official MCP Registry and returned real candidates while reporting `installationPerformed=false` and `executionPerformed=false`;
5. `submit_diagnostic` sent one synthetic, explicitly approved bounded diagnostic to the deployed collector and returned `SENT`;
6. the synthetic telemetry record was deleted after the smoke and the application telemetry/improvement tables returned to zero test records;
7. the consent widget resource and `render_telemetry_consent` descriptor were observed from the deployed MCP service.

This proves the remote MCP/app path itself. It does **not** by itself prove that the current ChatGPT client rendered the widget correctly; that remains a host smoke in Developer Mode.

## Find Skills and Find MCP across OpenAI hosts

On a local Codex/Agent Skills installation, the complete Cognitive OS bundle requires:

- the Cognitive OS skill;
- `vercel-labs/skills` → `find-skills` pinned through `skills@1.5.23`;
- the bundled Official MCP Registry client.

That local installation path is covered by CI install-smokes.

ChatGPT web is different: a cloud plugin cannot silently install software on the user's computer. The OpenAI plugin therefore packages the same **Find MCP behavior** behind the remote MCP endpoint, while skill/plugin discovery is handled through the OpenAI distribution surface. It must not pretend to perform a local computer installation.

## Submission package

[`chatgpt-app-submission.json`](../../chatgpt-app-submission.json) is generated from the actual tool implementation and contains:

- app info suggestions;
- all four MCP tools with explicit `readOnlyHint`, `openWorldHint` and `destructiveHint` values;
- review justifications;
- exactly five positive test cases;
- exactly three negative test cases.

Every exposed tool currently declares an `outputSchema`. The source inspection found no input requesting credentials, payment data, government identifiers, MFA codes, health data or similar sensitive identifiers.

## Remaining host/platform checks

Before claiming public OpenAI distribution as complete:

1. connect the production MCP endpoint in ChatGPT Developer Mode;
2. exercise `find_mcp`, `telemetry_status`, consent widget rendering and opted-in submit from the actual ChatGPT host;
3. verify the app/plugin metadata shown by the host;
4. submit the package through the current OpenAI review workflow when the V1.5 release candidate is otherwise ready;
5. claim public directory availability only after OpenAI approves/publishes it.

The repository may truthfully say **submission-ready** before review. It may not say **published in the Plugin Directory** before the external approval exists.

## Current official references

- OpenAI Developers: `https://developers.openai.com/`
- Apps SDK build/deployment/submission documentation under `https://developers.openai.com/apps-sdk/`
- OpenAI developer showcase/apps surface under `https://developers.openai.com/showcase/apps`

Re-verify these surfaces before each marketplace submission because product availability and manifest requirements can change independently of the Cognitive OS core.

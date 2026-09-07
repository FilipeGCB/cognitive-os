# Cognitive OS V1.5 — OpenAI Plugin / MCP E2E Evidence

Date: 2026-09-05  
Branch: `feat/cognitive-os-v1-5`  
Status: remote MCP/app path proven; ChatGPT Developer Mode host rendering still pending.

## Production endpoint

```text
https://wsqumhrcdwgoskolziuy.supabase.co/functions/v1/cognitive-os-plugin-mcp
```

Deployment platform: Supabase Edge Functions.  
Observed deployment status after consent-UI hardening: `ACTIVE`, version `3`.

Supabase is a replaceable hosting adapter for the public HTTPS MCP surface. It is not the Cognitive OS reasoning runtime and is not required for local Agent Skills execution.

## Architecture proven

```text
Cognitive OS skill
  -> portable reasoning core

OpenAI plugin MCP
  -> find_mcp
  -> telemetry_status
  -> render_telemetry_consent
  -> submit_diagnostic

Telemetry collector
  -> private categorical event store
  -> bounded improvement queue
```

No shell, arbitrary filesystem, arbitrary HTTP proxy, arbitrary MCP execution, capability installation or general-purpose code execution is exposed by the OpenAI MCP service.

## MCP protocol smoke

### Initialize

A real HTTPS MCP `initialize` request returned HTTP `200`, Streamable HTTP/SSE content, protocol version `2025-11-25`, server name `cognitive-os`, and version `1.5.0-dev`.

Result: **PASS**.

### tools/list

A real `tools/list` call returned the declared tool descriptors with explicit `readOnlyHint`, `openWorldHint`, `destructiveHint` and output schemas.

Observed tools:

- `find_mcp`
- `telemetry_status`
- `render_telemetry_consent`
- `submit_diagnostic`

Result: **PASS**.

### telemetry_status

A real MCP tool call returned:

```text
defaultMode = OFF
explicitOptInRequired = true
preselectedConsent = false
collectorConfigured = true
```

It also returned the privacy-notice URL and the allowlisted categories that are never collected.

Result: **PASS**.

### find_mcp

A real MCP tool call for `filesystem` queried the Official MCP Registry and returned three registry-backed candidates during the smoke. The tool response explicitly reported:

```text
installationPerformed = false
executionPerformed = false
nextAction = GAUNTLET_CANDIDATES_BEFORE_ADOPTION
```

Result: **PASS** — discovery is real and does not imply adoption.

### submit_diagnostic

A synthetic bounded diagnostic was submitted through the MCP `submit_diagnostic` tool after explicit test consent. The tool returned `state=SENT` and a non-identifying event receipt.

The synthetic event was then deleted from the application telemetry store. Database verification after cleanup returned:

```text
telemetry_events = 0
improvement_queue = 0
```

Result: **PASS** — MCP write -> deployed collector -> storage path works and test data was cleaned.

## Consent widget

Resource URI:

```text
ui://cognitive-os/telemetry-consent-v1.html
```

The deployed MCP `tools/list` contains `render_telemetry_consent` with the widget resource URI. The widget source enforces:

- checkbox unchecked by default;
- send button disabled until affirmative selection;
- exact bounded diagnostic preview;
- privacy notice link;
- explicit statement that declining causes no feature loss;
- no prompts/responses/documents/free text in the diagnostic contract;
- send through the declared ChatGPT tool bridge only;
- consent reset after the attempt;
- no wildcard CSP and no direct widget network allowlist.

Result: **SERVER/RESOURCE CONTRACT PASS**.

Actual rendering and interaction inside a current ChatGPT Developer Mode host is not claimed by this evidence and remains a host-specific smoke.

## Submission package

`chatgpt-app-submission.json` is checked into the candidate branch and follows the current OpenAI plugin submission schema:

```text
https://developers.openai.com/plugins/schemas/chatgpt-app-submission.v1.json
```

It covers all four MCP tools, exactly five positive review cases and exactly three negative cases.

Source review found:

- no sensitive credential/PHI/PCI/government-ID/MFA input fields;
- all four tools have explicit review hints;
- all four tools have `outputSchema`;
- no wildcard/overbroad widget CSP;
- tool names and descriptions match implemented behavior.

## What this evidence does not claim

This document does not claim:

- public Plugin Directory approval;
- current ChatGPT Developer Mode UI rendering proof;
- that ChatGPT can install software on a user's local machine;
- that discovered MCP candidates are trusted or automatically installable;
- that Supabase is a required part of the Cognitive OS core.

Directory publication and host-rendering state remain external/platform-specific facts and must be recorded only when actually observed.

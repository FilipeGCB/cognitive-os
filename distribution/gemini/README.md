# Gemini CLI distribution

Canonical runtime package: [`skills/cognitive-os`](../../skills/cognitive-os).

Verified against current Gemini CLI Agent Skills and Extensions documentation on 2026-09-03.

## Direct Agent Skill

Gemini CLI currently supports installing a skill from a Git repository or local directory and can target a subdirectory with its skill-management options. It discovers user and workspace skills and activates a matching skill with an explicit consent step before its resources are injected.

The canonical Cognitive OS folder can therefore be used directly rather than translated into a Gemini-specific instruction set.

## Extension wrapper

This repository also contains:

```text
gemini-extension.json
```

Gemini CLI extensions automatically discover Agent Skills bundled beneath `skills/`. That makes this repository installable as a thin extension wrapper while still using exactly:

```text
skills/cognitive-os
```

No MCP server or persistent `GEMINI.md` is required by Cognitive OS core.

A current Gemini CLI extension installation can use the repository URL, with explicit version/ref pinning recommended for stable Cognitive OS releases.

## Consent

Gemini's skill activation consent is independent from Cognitive OS's **capability installation consent**. Activating the Cognitive OS skill does not grant permission to install Docker, connect accounts, expose MCP servers or add write-capable integrations.

## Gallery/discovery

Listing an extension in any Gemini CLI gallery is a separate release/distribution step. The current wrapper is `1.5.0-dev`; re-verify current gallery eligibility/submission rules at release time and do not claim a listing until it is observed.

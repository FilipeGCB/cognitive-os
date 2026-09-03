# OpenAI distribution — ChatGPT and Codex

Canonical runtime package: [`skills/cognitive-os`](../../skills/cognitive-os).

Verified against current OpenAI product documentation on 2026-09-03.

## Current product surface

OpenAI currently treats **skills** as reusable workflows and the **Plugin Directory** as the discovery surface for workflow capabilities across ChatGPT and Codex. A plugin can contain skills, apps, or both.

ChatGPT's native Skills UI currently applies to eligible Business, Enterprise, Healthcare and Edu users, subject to workspace/product settings. Users can create skills and upload a skill from their computer; workspace sharing/install permissions are separately administered.

The Plugin Directory itself may be visible more broadly, but whether a particular skill/plugin can be installed or invoked varies by plan, role, workspace, region and surface.

## Cognitive OS packaging rule

Do **not** fork or rewrite the cognitive core for OpenAI. The source package remains:

```text
skills/cognitive-os/
```

Two distribution routes are relevant:

1. **Direct skill upload/install** on supported ChatGPT/Codex skill surfaces.
2. **Thin skill-only plugin listing** for directory discovery when the current OpenAI publication workflow supports it.

No external app is required for the core Cognitive OS skill. Optional external capabilities such as corpus connectors remain separate adapters and keep their own consent/auth boundaries.

## Development limitation

This repository does not yet claim that a public Plugin Directory listing has been submitted or approved. Directory submission/review is a release/distribution action and must be performed using the then-current OpenAI workflow after `v1.4.0` release gates pass.

Running `npx skills add` on a user's computer must **not** be described as automatically installing the skill into ChatGPT web. ChatGPT's own skill/plugin surfaces control ChatGPT installation.

## Current official references

- OpenAI Help Center: `Skills in ChatGPT`
- OpenAI Help Center: `Plugins in ChatGPT and Codex`

Re-verify these surfaces before each marketplace submission because availability and packaging can change independently of the Cognitive OS core.

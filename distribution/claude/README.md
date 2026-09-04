# Claude distribution

Canonical runtime package: [`skills/cognitive-os`](../../skills/cognitive-os).

Verified against current Anthropic Claude Code skill/plugin marketplace documentation on 2026-09-03.

## Claude Code marketplace

This repository contains:

```text
.claude-plugin/marketplace.json
```

The marketplace entry points directly to:

```text
skills/cognitive-os
```

No duplicate Claude-specific copy of the cognitive core exists.

Users can add the GitHub repository as a Claude Code marketplace and then install the plugin using Claude Code's current plugin commands:

```text
/plugin marketplace add FilipeGCB/cognitive-os
/plugin install cognitive-os@cognitive-os
```

Anthropic documents that marketplace owner email is optional, so the development manifest uses the public GitHub maintainer name only.

## Standalone/custom skills

Claude also supports skills as self-contained folders. Where a Claude surface supports custom skill upload or project/user skill directories, use the same `skills/cognitive-os/` package rather than maintaining another version.

## Update behavior

During `1.5.0-dev` the marketplace entry is a development artifact. The
distribution manifest records the package version and projected assets; a
stable tag/version must be reconciled before release.

## Marketplace discovery

A repository-hosted Claude Code marketplace makes the plugin installable; broader inclusion/highlighting in Anthropic-maintained discovery surfaces is a separate distribution/review step and must not be claimed until observed.

# Cognitive OS Bootstrap

This directory contains deterministic preflight/planning helpers for hosts that can inspect or configure their local environment.

The bootstrapper is **not required for the Cognitive OS skill to reason**. The distributable skill remains self-contained under `skills/cognitive-os/`.

## Safety boundary

`cognitive_os_bootstrap.py` is intentionally side-effect-free. It decides what should happen next; it does not execute third-party installers.

Possible decisions:

- `USE_EXISTING`
- `AUTO_INSTALL_ALLOWED`
- `ASK_SPECIFIC_CONSENT`
- `NO_APPROVED_IMPLEMENTATION`
- `BLOCKED`

A host-specific execution layer may act on `AUTO_INSTALL_ALLOWED` only when it can preserve the same policy and verify the resulting state. `ASK_SPECIFIC_CONSENT` requires a fresh user confirmation before any install/authentication action.

## First-use consent

The one-time safe-enhancement consent is intentionally narrow. See `../skills/cognitive-os/policies/installation-consent.md`.

Heavy components, Docker/persistent services, large downloads, external accounts, credentials, sensitive access, write capabilities and privileged/system-wide changes are always outside the one-time consent.

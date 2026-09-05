# Agent Skills distribution

Canonical runtime package: [`skills/cognitive-os`](../../skills/cognitive-os).

Cognitive OS follows the portable Agent Skills directory pattern: a self-contained folder with `SKILL.md` plus supporting references, schemas and policies.

## Generic install

Where the Skills CLI supports the current agent:

```bash
npx skills add FilipeGCB/cognitive-os --skill cognitive-os -g
```

The CLI is an installer/manager. Node.js is not required by the Cognitive OS runtime after the skill has been copied/configured.

For project-scoped installation, omit global scope or use the agent's project/workspace skill directory as documented by that host.

## Manual install

Copy `skills/cognitive-os/` into a supported user/global or workspace skill directory.

## Update discipline

Prefer tagged releases for stable installations. Do not make runtime behavior silently follow repository `main`; explicit version upgrades preserve reproducibility and rollback.

During `1.5.0-dev`, users who install directly from the repository are opting into development state rather than a stable release. The installed artifact must be checked against its V1.5 distribution manifest.

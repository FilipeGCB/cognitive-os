# GitHub Actions Economy — repository policy

Canonical policy: `FitaCFO/fita-operacao/00_gestao/governanca/GITHUB_ACTIONS_ECONOMY_POLICY.md`.

Mandatory rules:
- Fita Cloud/CFO-IA remains DEV-ONLY. Other projects follow their own release/deploy policy.
- Local first, remote once.
- Do not push every micro-fix.
- Do not use GitHub Actions as a development loop.
- Run lint/tests/build/Playwright locally before publishing.
- Batch changes before push.
- No Windows/macOS GitHub-hosted runner without manager approval.
- macOS must not run on every PR synchronize.
- Heavy browser/security/build workflows should be manual/label-gated/path-filtered.
- Use concurrency + cancel-in-progress where applicable.
- Docs-only must not trigger heavy CI.
- Dependabot does not automatically authorize heavy runners.
- Before any expensive runner, check monthly Actions usage.
- Above 85% budget: only essential remote gates.
- Above 95%: expensive Actions blocked until reset or explicit human override.

Provider behavior:
- ChatGPT manager decides publication timing.
- Claude integrates locally and publishes in batches.
- Codex may commit locally; push only when candidate is ready.
- AGY-A/AGY-B use isolated worktrees and do not publish micro-iterations.
- Jules does not create PR/CI for intermediate planning.
- Copilot/Dependabot PRs must not fan out into expensive workflows automatically.

A repository may be stricter than this policy, never more permissive.

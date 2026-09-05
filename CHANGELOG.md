# Changelog

All notable public Cognitive OS changes are recorded here.

## 1.5.0-dev — 2026-09-04

Development line; no stable release or tag is published by this branch.

### Added

- versioned V1.5 public specification and architecture gap analysis;
- fail-closed account-bound capability and candidate-SHA release evidence contracts;
- strict run, capability, forensic and usage-trace schemas with deterministic validators;
- capability discovery 2.0, configurable research budgets, Web→Corpus routing and truth-domain reconciliation;
- self-improvement governance, mutation/side-effect ledgers and provider closure contracts;
- local Flight Recorder and opt-in privacy-preserving telemetry client (shared sender remains disabled until Gate T/deployment evidence).

## v1.4.0 — 2026-09-04

### Added

- self-contained host-neutral Cognitive OS Agent Skill;
- Adaptive Discovery Interview;
- sensemaking meta-routing;
- Outside View / reference-class discipline;
- Value of Information prioritization for next proof;
- robustness lens for deep uncertainty;
- Decision Quality closure check;
- abstract Deep Research and Grounded Corpus Research capability routing;
- consent-aware capability bootstrap planner;
- NotebookLM adapter candidate and Grounded Corpus companion Gauntlet;
- Decision Brief editorial/output policy;
- optional dependency-free Decision Brief HTML renderer;
- public behavior/output eval manifests and deterministic package guards.

### Verified for release promotion

- Apache License 2.0 present and authoritative at the repository root;
- fresh v1.4 behavioral conformance passed 29/29 with Gemma and 29/29 with an independent Qwen cross-grader, with zero critical failures and zero grader disagreements;
- live Hermes capability E2E passed 6/6 on one candidate SHA, including Web Search, MCP discovery, read-only NotebookLM Grounded Corpus Research with observed `source_read`, prompt-injection/authorization boundary behavior, and explicit unavailable-capability handling;
- Agent Skills discovery/install smoke tests passed for Codex, Claude Code and Gemini CLI;
- the pinned `notebooklm-py[mcp]==0.8.2` candidate installed and exposed its CLI/MCP entrypoints in CI;
- repository-history Gitleaks secret scan passed;
- public-package, PII, renderer and Python compile checks passed.

The stable `v1.4.0` tag is created only after the final promotion commit passes CI on the feature branch, the PR is explicitly approved for merge, and downstream `main` CI satisfies the release workflow.

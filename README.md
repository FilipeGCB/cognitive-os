# Cognitive OS

> **Think before you spec. Decide before you execute.**

**A portable Agent Skill that helps agents mature consequential decisions before acting — by separating evidence from assumptions, challenging the leading conclusion, and identifying the next useful proof.**

**PT-BR:** Uma Agent Skill portátil para amadurecer decisões antes da execução, separando evidência de suposição, desafiando a conclusão dominante e identificando a próxima prova útil.

[Português (Brasil)](README.pt-BR.md)

## In 10 seconds

Use Cognitive OS when the important question is not yet “how do I build this?” but **“what should I actually decide, and what evidence would change that decision?”**

It reconstructs context, chooses proportional research/reasoning methods, challenges the recommendation, and stops when more analysis is unlikely to change the answer.

It is **not** a software delivery lifecycle and not an autonomous executor. A decision may hand off to a human, a coding workflow, a research process, another agent — or to no action at all.

> **Current development line:** `1.5.0-dev`. The latest stable release remains [`v1.4.0`](https://github.com/FilipeGCB/cognitive-os/releases/tag/v1.4.0) until the V1.5 release gates are complete.

## Install

On Agent Skills-compatible environments supported by the Skills CLI:

```bash
npx skills add FilipeGCB/cognitive-os --skill cognitive-os -g
```

The V1.5 **complete local bundle** also requires the approved discovery layer:

- **Find Skills:** `vercel-labs/skills` → `find-skills`, pinned through `skills@1.5.23`;
- **Find MCP:** Cognitive OS's bundled read-only client for the Official MCP Registry at `registry.modelcontextprotocol.io`.

The supported installer boundary is [`bootstrap/cognitive_os_install.py`](bootstrap/cognitive_os_install.py). It requires acceptance of the disclosed Cognitive OS bundle terms, installs/verifies Find Skills where the host supports local Agent Skills, and verifies Find MCP discovery. The deterministic bootstrap planner remains side-effect-free.

Installing discovery **does not** authorize a discovered skill or MCP candidate. Candidates still pass provenance/security/permission/consent checks before use or installation.

`npx` is installation transport; Node.js is not part of the Cognitive OS reasoning runtime.

Manual copying of only [`skills/cognitive-os/`](skills/cognitive-os/) is still useful for inspection or constrained hosts, but it is not the fully verified V1.5 local bundle unless the two discovery capabilities are also present. Host-specific notes live under [`distribution/`](distribution/).

## 60-second use

After installation, ask your agent normally:

> I want to build an AI product for small businesses. Help me decide whether the idea is worth pursuing before I start building it.

If the situation is materially ambiguous, Cognitive OS asks **one high-value question at a time**. If the task is already clear, it does not force an intake ritual.

A strong result should read like a concise analyst/consultant brief:

```text
decision first
↓
what changed from the initial idea, when relevant
↓
why the decision changed
↓
what could still change it
↓
one clear next move
```

See [`examples/`](examples/) for compact examples.

## What changes with Cognitive OS

| | Starting point | Matured decision |
|---|---|---|
| Problem | Accept the proposed solution as the problem | Reconstruct context and formulate the real decision |
| Truth | Plausible statements blend together | Distinguish evidence, inference, hypothesis, assumption, unknown, and contradiction |
| Research | Search because more information feels safer | Obtain information only when it can materially change the decision |
| Challenge | List generic risks | Close each material attack to its impact on the recommendation |
| Action | Keep analyzing or start building | Decide, test, wait, stop, investigate further — or deliberately do nothing |

## Cognitive core

The installed skill includes a selective, adaptive set of capabilities:

- **Adaptive Discovery Interview** — interview only when ambiguity can materially change the outcome.
- **Sensemaking** — identify what kind of response the situation requires before choosing a method.
- **Evidence discipline** — separate observed facts/evidence from inference, assumptions, and unknowns.
- **Outside View** — look for defensible comparable outcomes/base rates when they can change the judgment; never invent them.
- **Diagnosis** — causal reasoning, bottleneck analysis, and first principles when justified.
- **Decision challenge** — trade-offs, red team, premortem, reversibility, second-order effects, and kill criteria.
- **Value of Information** — prioritize the smallest evidence worth obtaining next.
- **Robustness** — under deep uncertainty, prefer decisions that survive multiple plausible futures rather than fake precision.
- **Decision Quality closure** — check framing, alternatives, information, values/trade-offs, reasoning, and next action before closing a material decision.
- **Stop discipline** — know when additional research is unlikely to change the recommendation.

Methods are not shown merely to prove rigor. Cognitive OS reports what they helped discover.

## Capability discovery, not vendor lock-in

The core requests abstract capabilities rather than hard-coding products. It first uses a sufficient native capability, then local discovery, and only then approved external discovery when a material capability gap remains.

Find Skills and Find MCP are discovery infrastructure, **not trust shortcuts**. A discovered candidate is quarantined until its provenance, permissions and applicable Gauntlet/consent state are known.

### NotebookLM

NotebookLM is a first-class implementation of Grounded Corpus Research, not a mandatory dependency. The evaluated community adapter is [`notebooklm-py`](adapters/notebooklm/). Because it requires Google/NotebookLM authentication and local authentication material, Cognitive OS always requires specific consent before account-bound use. It is not represented as an official Google API.

## Zero-config where possible

> **Zero-config whenever possible. One confirmation when necessary. Explicit consent when consequential.**

The deterministic bootstrap detects what a host already provides. The separate installer applies only an approved, disclosed bundle. External accounts, credentials, sensitive data access, persistent services, privileged changes and write-capable integrations retain their own consent boundaries.

## Optional diagnostics and improvement loop

Cognitive OS V1.5 has a privacy-preserving Flight Recorder. Shared diagnostics are **OFF by default**, require explicit opt-in, are never preselected, can be revoked, and refusing them does not reduce product functionality.

The deployed collector accepts only a strict categorical allowlist — never prompts, responses, documents, file contents, private paths/URLs, credentials, tokens, cookies, client/project names, PII, arbitrary free text or chain-of-thought. See [`docs/telemetry-privacy-notice.md`](docs/telemetry-privacy-notice.md).

Repeated sanitized failure signatures can enter a maintainer improvement queue. Three distinct matching events promote an issue from `observing` to `candidate`. A candidate triggers investigation; it **does not** silently edit or redeploy Cognitive OS. Changes still require reproduction, spec/patch, tests, review and release evidence.

## Decision artifacts

```text
Decision Pack          canonical structured decision truth
└── Decision Brief     human/editorial projection

Cognitive Run Record   separate observable audit evidence when needed
```

Full Flow/Audit is available when a formal gate or explicit request requires observable execution evidence without persisting private chain-of-thought.

## Runtime truth

Cognitive OS distinguishes:

```text
availability = AVAILABLE | UNAVAILABLE | UNKNOWN
invocation   = CALLED | NOT_CALLED
result       = SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE
```

Installed or documented does **not** mean executed. V1.5 additionally separates availability, authentication, run consent, invocation and result.

## Distribution

The same cognitive core is packaged for multiple host families under [`distribution/`](distribution/). V1.5 is closing three discovery/install surfaces:

- portable Agent Skills/local hosts;
- Claude plugin packaging;
- ChatGPT/Codex plugin packaging using a skill plus narrowly scoped MCP app operations where remote execution is required.

A package being submission-ready is not the same as being approved in an external plugin directory; directory publication is claimed only after the platform completes its review.

## Verifiable V1.5 boundary

- push/PR CI is deterministic; no local LLM is a release gate;
- behavioral conformance is a separate explicit **remote** SUT + independent remote grader workflow;
- Hermes E2E remains a separate real host-capability proof;
- release evidence is candidate-SHA-bound and may not reuse historical model runs as current promotion proof.

Historical V1.4 evidence remains documented at [`docs/releases/v1.4.0-release-evidence.md`](docs/releases/v1.4.0-release-evidence.md). V1.5 closure status lives at [`docs/releases/v1.5-final-closure-checklist.md`](docs/releases/v1.5-final-closure-checklist.md).

## Repository layout

```text
cognitive-os/
├── skills/cognitive-os/       # portable reasoning core
├── bootstrap/                 # deterministic planner + explicit installer/discovery boundary
├── adapters/                  # candidate/host capability adapters
├── telemetry/                 # privacy-preserving client/flight recorder
├── evals/                     # behavioral cases and validators
├── examples/                  # Decision Brief examples
├── renderers/                 # optional presentation layer
├── distribution/              # host/plugin packaging
├── tests/                     # deterministic contract/regression tests
└── docs/                      # architecture, evidence, privacy and release docs
```

## License

Cognitive OS is licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE).

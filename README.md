# Cognitive OS

> **Think before you spec. Decide before you execute.**

**A portable Agent Skill that helps agents mature consequential decisions before acting — by separating evidence from assumptions, challenging the leading conclusion, and identifying the next useful proof.**

**PT-BR:** Uma Agent Skill portátil para amadurecer decisões antes da execução, separando evidência de suposição, desafiando a conclusão dominante e identificando a próxima prova útil.

[Português (Brasil)](README.pt-BR.md)

## In 10 seconds

Use Cognitive OS when the important question is not yet “how do I build this?” but **“what should I actually decide, and what evidence would change that decision?”**

It reconstructs context, chooses proportional research/reasoning methods, challenges the recommendation, and stops when more analysis is unlikely to change the answer.

It is **not** a software delivery lifecycle and not an autonomous executor. A decision may hand off to a human, a coding workflow, a research process, another agent — or to no action at all.

## Install

On Agent Skills-compatible environments supported by the Skills CLI:

```bash
npx skills add FilipeGCB/cognitive-os --skill cognitive-os -g
```

`npx` is only the installation transport. **Node.js is not part of the Cognitive OS runtime.** The installed skill is a self-contained directory of instructions, references, policies, and schemas.

Manual installation is also possible by copying:

```text
skills/cognitive-os/
```

into a skill directory supported by your agent. Host-specific notes live under [`distribution/`](distribution/).

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

> **Current stable release:** [`v1.4.0`](https://github.com/FilipeGCB/cognitive-os/releases/tag/v1.4.0). Behavioral conformance, live host/capability E2E, promotion CI, downstream `main` CI, and the stable release workflow passed before publication.

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

## Capabilities, not vendor lock-in

The core requests abstract capabilities rather than hard-coding products:

| Need | Capability |
|---|---|
| Current external information | Web Search |
| Broad/deep external investigation | Deep Research |
| Large or persistent closed corpus | Grounded Corpus Research |
| Current code/repository state | Repository Research |
| Authorized documents/files | Document/File Research |
| Material quantitative work | Data Analysis |
| Multi-page structured collection | Structured Crawl |
| Specialized technical security work | Security Analysis |
| Find reusable procedures/connections | Capability Discovery |

The current host maps those needs to tools it actually has. A native capability that is already sufficient wins over installing another tool.

### NotebookLM

NotebookLM is a first-class **implementation** of Grounded Corpus Research, not a dependency of Cognitive OS.

The evaluated community adapter is [`notebooklm-py`](adapters/notebooklm/), which provides a CLI/MCP path to NotebookLM. Because it requires Google/NotebookLM authentication and stores authentication material locally, Cognitive OS **always asks for specific consent** before installing or connecting it.

A bounded read-only Hermes E2E has been observed with successful `source_read`, but NotebookLM remains an optional account-bound candidate implementation rather than a bundled/default dependency or an official Google API.

### Open-source corpus companions

Cognitive OS is also evaluating local alternatives such as OpenNotebookLM, Open Notebook, SurfSense, and AnythingLLM. None is installed by default. See [`docs/capabilities/grounded-corpus-gauntlet.md`](docs/capabilities/grounded-corpus-gauntlet.md).

## Zero-config where possible

> **Zero-config whenever possible. One confirmation when necessary. Explicit consent when consequential.**

The optional bootstrap planner detects what the host already provides. It may recommend demand-driven installation only for components that satisfy the declared safety constraints; consequential changes such as external accounts, credentials, sensitive data access, persistent services, privileged changes, or write-capable integrations require explicit consent.

The bootstrap planner itself is side-effect-free: it returns an installation decision and does not execute third-party installers.

## Decision artifacts

Cognitive OS keeps three responsibilities separate:

```text
Decision Pack          canonical structured decision truth
└── Decision Brief     human/editorial projection

Cognitive Run Record   separate observable audit evidence when needed
```

A normal conversation should feel natural and direct. Full Flow/Audit exists when a formal gate or explicit request needs observable execution evidence without persisting private chain-of-thought.

## Output quality is part of correctness

A correct conclusion that is hard to read is a worse decision product.

Markdown is the portable human format. An optional dependency-free HTML renderer produces a restrained editorial/executive-memo view:

```bash
python renderers/decision-brief/render.py \
  examples/decision-brief-idea-evolution.md \
  decision.html
```

## Runtime truth

Cognitive OS distinguishes:

```text
availability = AVAILABLE | UNAVAILABLE | UNKNOWN
invocation   = CALLED | NOT_CALLED
result       = SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE
```

A capability being installed or documented does **not** prove that it executed. Successful execution is claimed only when runtime evidence supports it.

## Repository layout

```text
cognitive-os/
├── skills/cognitive-os/       # self-contained runtime skill
│   ├── SKILL.md
│   ├── references/
│   ├── schemas/
│   └── policies/
├── bootstrap/                 # optional side-effect-free capability planner
├── adapters/                  # isolated candidate/host capability adapters
├── evals/                     # behavioral case definitions and validators
├── examples/                  # human-facing Decision Brief examples
├── renderers/                 # optional presentation layer
├── distribution/              # host/discovery packaging guidance
├── tests/                     # deterministic contract/regression tests
└── docs/                      # architecture, evidence, and release documentation
```

## Conformance and release evidence

The private predecessor V1.3 established the behavioral and auditability baseline from which this public product was derived. Those historical results do **not** automatically prove V1.4.

The public `v1.4.0` candidate passed the declared 29-case behavioral/output suite with the local Gemma SUT and an independent Qwen cross-grader, with zero critical failures and zero grader disagreements. Live Hermes capability E2E also passed 6/6 on one candidate SHA. Promotion CI, downstream `main` CI, and the stable release workflow subsequently passed before the tag and GitHub Release were created.

See [`docs/releases/v1.4.0-release-evidence.md`](docs/releases/v1.4.0-release-evidence.md) for the evidence boundary.

## License

Cognitive OS is licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE).

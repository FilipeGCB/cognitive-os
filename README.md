# Cognitive OS

> **Think before you spec. Decide before you execute.**

Cognitive OS is a portable Agent Skill for maturing decisions before consequential action. It reconstructs context, separates evidence from assumptions, chooses proportional research and reasoning methods, challenges the leading conclusion, identifies the next useful proof, and knows when further analysis is no longer worth its cost.

It is deliberately **not** a software delivery lifecycle or an autonomous executor. A decision may hand off to a human, a coding workflow, a research process, another agent—or to no action at all.

> **Current status:** `v1.4.0` promotion candidate. Behavioral conformance and live host/capability E2E have passed. The stable GitHub tag/release is still gated on final feature-branch CI, explicit merge approval, and downstream green `main` CI.

## Install

On Agent Skills-compatible environments supported by the Skills CLI:

```bash
npx skills add FilipeGCB/cognitive-os --skill cognitive-os -g
```

`npx` is only an installation transport. **Node.js is not part of the Cognitive OS runtime.** The installed skill is a self-contained directory of instructions, references, policies and schemas.

You can also install manually by copying:

```text
skills/cognitive-os/
```

into a skill directory supported by your agent. Host-specific notes live under [`distribution/`](distribution/).

## 60-second use

After installation, ask your agent normally:

> I want to build an AI product for small businesses. Help me decide whether the idea is worth pursuing before I start building it.

If the idea is too ambiguous to analyze responsibly, Cognitive OS asks **one high-value question at a time**. If the task is already clear, it does not run an intake ritual.

For a material decision, the result should read like a strong analyst/consultant brief—not a dump of internal frameworks:

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

A vague starting idea can mature without being buried in process.

| | Starting point | Matured decision |
|---|---|---|
| Problem | Accept the proposed solution as the problem | Reconstruct context and formulate the real decision |
| Truth | Plausible statements blend together | Distinguish evidence, inference, hypothesis, assumption, unknown and contradiction |
| Research | Search because more information feels safer | Obtain information only when it can materially change the decision |
| Challenge | List generic risks | Close each material attack to its impact on the recommendation |
| Action | Keep analyzing or start building | Decide, test, wait, stop, investigate further—or deliberately do nothing |

## Cognitive core

The installed skill includes a selective, adaptive set of capabilities:

- **Adaptive Discovery Interview** — interview only when ambiguity can materially change the outcome.
- **Sensemaking** — identify what kind of response the situation requires before choosing a method.
- **Evidence discipline** — separate observed facts/evidence from inference, assumptions and unknowns.
- **Outside View** — look for defensible comparable outcomes/base rates when they can change the judgment; never invent them.
- **Diagnosis** — causal reasoning, bottleneck analysis and first principles when justified.
- **Decision challenge** — trade-offs, red team, premortem, reversibility, second-order effects and kill criteria.
- **Value of Information** — prioritize the smallest evidence worth obtaining next.
- **Robustness** — under deep uncertainty, prefer decisions that survive multiple plausible futures rather than fake precise probabilities.
- **Decision Quality closure** — check framing, alternatives, information, values/trade-offs, reasoning and next action before closing a material decision.
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

The evaluated community adapter is [`notebooklm-py`](adapters/notebooklm/), which provides a CLI/MCP path to NotebookLM. Because it requires Google/NotebookLM authentication and stores authentication material locally, Cognitive OS **always asks for specific consent** before installing or connecting it. A bounded read-only Hermes E2E has been observed with successful `source_read`, but NotebookLM remains an optional account-bound candidate implementation rather than a bundled/default dependency or an official Google API.

### Open-source corpus companions

Cognitive OS is also evaluating local alternatives such as OpenNotebookLM, Open Notebook, SurfSense and AnythingLLM. None is currently installed by default. Repository review selected OpenNotebookLM as a future direct integration candidate, but no default will be promoted until direct retrieval/citation and installation tests pass. See [`docs/capabilities/grounded-corpus-gauntlet.md`](docs/capabilities/grounded-corpus-gauntlet.md).

## Zero-config where possible

For hosts that can inspect/configure their environment, Cognitive OS follows this principle:

> **Zero-config whenever possible. One confirmation when necessary. Explicit consent when consequential.**

The optional bootstrap planner first detects what the host already provides. A one-time consent may allow demand-driven installation of approved components only when they are light, local/user-space, reversible, require no account/secret, access no sensitive persistent data, expose no external write, and make no privileged change.

It **always asks again** before Docker/persistent services, large downloads, external accounts, API keys/credentials, sensitive data access, write-capable integrations, privileged changes or other material consequences.

The bootstrap planner itself is side-effect-free; it returns an installation decision and does not execute third-party installers.

## Decision artifacts

Cognitive OS keeps three responsibilities separate:

```text
Decision Pack          canonical structured decision truth
└── Decision Brief     human/editorial projection

Cognitive Run Record   separate observable audit evidence when needed
```

A normal conversation should feel natural and direct. Full Flow/Audit is available when a formal gate or explicit user request requires evidence of what was traversed or executed, without persisting chain-of-thought.

## Output quality is part of correctness

A correct conclusion that is hard to read is a worse decision product.

Decision Brief guidance treats hierarchy, whitespace, density and typography as functional requirements. Markdown is the portable human format. An optional dependency-free HTML renderer produces a restrained editorial/executive-memo view with system fonts, responsive layout and light/dark support:

```bash
python renderers/decision-brief/render.py \
  examples/decision-brief-idea-evolution.md \
  decision.html
```

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
├── distribution/              # thin host/discovery packaging guidance
├── tests/                     # deterministic contract/regression tests
└── docs/                      # architecture, evidence and release documentation
```

## Runtime truth

Cognitive OS distinguishes:

```text
availability = AVAILABLE | UNAVAILABLE | UNKNOWN
invocation   = CALLED | NOT_CALLED
result       = SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE
```

A capability that is installed or documented has **not** necessarily executed. Successful execution is claimed only when runtime evidence supports it.

## Conformance

The private predecessor V1.3 established the behavioral and auditability baseline from which this public product was derived. Those historical results do **not** automatically prove V1.4.

The public V1.4 case manifests live under [`evals/`](evals/). The release candidate passed the declared 29-case behavioral/output suite with the local Gemma SUT and an independent Qwen cross-grader, with zero critical failures and zero grader disagreements. Live Hermes capability E2E also passed 6/6 on one candidate SHA. See [`docs/releases/v1.4.0-release-evidence.md`](docs/releases/v1.4.0-release-evidence.md) for the evidence boundary and remaining promotion steps.

## License

Cognitive OS is licensed under the **Apache License 2.0**. See [`LICENSE`](LICENSE).

The immutable stable tag/release is created only after the explicit release gate is satisfied on the promotion branch, the PR is approved and merged, and downstream `main` CI is green.

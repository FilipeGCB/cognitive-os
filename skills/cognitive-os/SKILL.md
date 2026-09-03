---
name: cognitive-os
description: "Use to mature decisions before consequential action: reconstruct context, clarify the real problem, ground claims in evidence, choose proportional reasoning and research capabilities, challenge conclusions, identify the next useful proof, know when to stop, and hand off a clear recommendation without self-authorizing execution."
---

# Cognitive OS

## Core rule

Context before problem. Problem before solution. Evidence before confidence. Decision before execution. Textual policy is not technical enforcement.

Cognitive OS is a host-neutral decision layer. It requests abstract capabilities and lets the current host map them to native tools, apps, plugins, MCPs, APIs or local adapters that are actually available.

## What it is

Use Cognitive OS when a task benefits from better framing, evidence, diagnosis, comparison, challenge, research or decision quality before action.

It is not a software delivery lifecycle, an autonomous executor, a universal RAG server, or a requirement to run a fixed framework on every request.

## Ambiguity and Adaptive Discovery Interview

Do not silently invent the user's current intent.

When unresolved ambiguity can materially change the framing, evidence needs, alternatives, scope or recommendation, read `references/discovery-interview.md` and ask the highest-value missing question first.

Do not interview by ritual. If the request is already clear enough to analyze safely, proceed.

Never claim `created`, `installed`, `executed`, `changed`, `researched`, or equivalent without observable evidence that the action actually occurred.

## Adaptive flow

The flow is conceptual, not a visible checklist:

0. Contextualize the system, state, constraints, prior decisions and authoritative sources.
1. Formulate the real question before accepting the requested solution as the problem.
2. Ground reality: distinguish fact/evidence, inference, hypothesis, assumption, preference, unknown and contradiction.
3. When ambiguity is material, perform enough sensemaking to choose the right reasoning strategy.
4. Choose proportional depth and a soft budget. Default is Normal.
5. Choose only the sources, capabilities and methods that can materially reduce uncertainty.
6. Compare meaningful alternatives when they exist.
7. Challenge the leading conclusion proportionally to risk and reversibility.
8. Identify the next proof, its information value, and the stop condition.
9. Recommend clearly. Consequential execution remains a separate authorization boundary.

Read `references/routing.md`, `references/source-authority.md`, `references/lenses.md`, `references/extended-lenses.md`, `references/workflows.md`, `references/capabilities.md`, `references/research-routing.md`, and `references/output.md` only as needed.

## Materiality

Treat something as material when it can plausibly change the decision, recommendation, scope, success criterion, reversibility, security/compliance posture, feasibility, a blocking dependency, or cost/time/effort by about 25% or more unless a better domain threshold exists.

## Depth

Default = Normal.

- Fast: low impact, reversible, low uncertainty.
- Normal: ordinary substantive decision work.
- Deep: more evidence/alternatives/challenge are material.
- Board360: maximum justified depth for high-stakes decisions, still selective.

Full Flow/Audit is a separate auditability axis. It does not mean Board360 and neither mode means using every lens or tool.

## Evidence and source authority

Use `references/source-authority.md` when the answer depends on current external state, code, canonical documents, or conflicting sources.

Current implementation/state should be observed from the authoritative system when material. Historical context and model knowledge do not silently replace missing current evidence.

External mutable claims such as current price, limits, license, terms, product status, version or capability availability require current evidence when that could change the decision.

## Capability truth

For material/auditable capability use, distinguish:

- `availability = AVAILABLE | UNAVAILABLE | UNKNOWN`
- `invocation = CALLED | NOT_CALLED`
- `result = SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE`

Availability is not execution. Only runtime-observed `AVAILABLE + CALLED + SUCCESS` supports an unqualified claim that the capability executed successfully.

Use the smallest sufficient capability. Prefer an already available native capability over installing a redundant companion.

## Research

Research is selected by need, not by brand.

- current/simple external fact → Web Search
- broader external investigation → composed research or Deep Research when its information value justifies the extra cost/time
- repeated reasoning over a closed or large document corpus → Grounded Corpus Research
- structured multi-page extraction → Structured Crawl when ordinary search is insufficient

NotebookLM is an important implementation of Grounded Corpus Research, not a dependency of the core. See `references/research-routing.md` and `references/capabilities.md`.

## Methods

Core methods live in `references/lenses.md`. Extended methods live in `references/extended-lenses.md` and are loaded only when justified.

Do not create or invoke a methodology merely because it exists. A method earns context by changing understanding, evidence or decision quality.

## Challenge

For a material attack on a recommendation, close the loop:

`attack → evidence/plausibility → what breaks → recommendation impact → mitigation/next proof`

Recommendation impact is one of: maintains, weakens, conditions, reverses.

## Next proof and stop

The next proof is the smallest new evidence likely to change the decision. Prioritize it by qualitative information value: decision impact versus cost, delay and reversibility. Do not fabricate probabilities or precise expected values.

Stop when additional research is unlikely to change the decision, when no material unknown remains, or when a bounded experiment is cheaper/more informative than more analysis.

`STOP_RESEARCH_AND_TEST` is valid and does not mean the hypothesis is already validated.

## Decision Quality closure

Before closing a material decision, ensure the chosen depth has sufficiently addressed:

- framing;
- meaningful alternatives;
- relevant information/evidence;
- values and trade-offs;
- defensible reasoning/challenge;
- a clear next action or deliberate no-action state.

This is a closure check, not a framework that must be exposed to the user.

## Full Flow / Audit

Activate only when explicitly requested or required by a formal gate.

Account for relevant phases and conditional branches without persisting chain-of-thought. Non-applicable branches are `NOT_APPLICABLE`; applicable incomplete branches are `PARTIAL` or `BLOCKED`. Tool failures, truncation, rate limits and unavailability remain visible when material.

Use `schemas/cognitive-run-record.md` for observable audit evidence.

## Output

Cognitive OS should end in understanding, not process reporting.

For material decisions, use the Decision Brief behavior in `references/output.md`. `schemas/decision-pack.md` remains the canonical structured decision record. `schemas/cognitive-run-record.md` remains separate audit evidence.

Show what changed from the initial idea when that delta helps understanding. Do not expose internal phase names, lens names, raw enums or framework ritual in normal output unless they materially help.

## Execution boundary

Cognitive OS may prepare a recommendation or draft/proposed handoff. It does not transform its own recommendation into authorization for consequential execution.

## Style

Be clear, direct, didactic and natural. Use jargon only when the subject requires it. Prefer whitespace and hierarchy over walls of bullets. Visual richness should be proportional to decision complexity.

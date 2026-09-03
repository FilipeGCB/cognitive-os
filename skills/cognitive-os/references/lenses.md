# Core Lenses — Cognitive OS v1.4

These are the lenses available by default. Extended lenses live in `extended-lenses.md` and are loaded only when justified.

## Truth and uncertainty

### /evidence
Use when facts, opinions and assumptions are mixed.

Question: what do we actually know, and what supports it?

Output: facts/evidence, inferences, hypotheses, assumptions, preferences, unknowns and contradictions as relevant.

In Full Flow/Audit, material claims may be classified as:

`FACT | EVIDENCE | INFERENCE | HYPOTHESIS | ASSUMPTION | PREFERENCE | UNKNOWN | CONTRADICTION`.

### /assumptions
Use before committing to a solution or decision when unproven beliefs matter.

Output: assumption, materiality, evidence status and a possible test.

### /unknowns
Use when uncertainty remains.

Output: unknowns prioritized by potential decision impact, not by curiosity.

### /contradictions
Use when sources or premises conflict.

Output: incompatible claims, authority/temporal context and evidence needed to resolve the conflict.

### /missingquestion
Use when analysis appears complete suspiciously early.

Output: the important unasked question and how it could change the decision.

## Sensemaking

### /sensemaking
Use when the nature of the situation itself is unclear enough to change how reasoning should proceed.

Question: what kind of response does this situation require before we choose a method?

Internal routing categories:

- clear → recover procedure/rule;
- complicated → analyze/compare/seek expertise;
- complex → safe-to-fail probe, observe, adapt;
- chaotic → stabilize before analysis;
- unclear → gather enough context to classify strategy.

Do not force these labels into the human response unless they improve understanding.

## Cause and diagnosis

### /gut
Capture the initial judgment and why, before heavy analysis, so later evidence can reveal whether the view changed.

### /5why
Use when there is a symptom and a causal chain can reveal a controllable cause.

Do not force five iterations or pretend causality is proven when evidence is weak.

### /bottleneck
Use when system throughput/outcome is constrained.

Output: principal constraint, evidence and expected effect of relieving it.

## Foundations

### /firstprinciples
Use when inherited assumptions may be constraining the design.

Question: what must remain true independently of the current solution?

## Decision and challenge

### /tradeoffs
Use when no path dominates on every relevant dimension.

Output: benefits, sacrifices and decision-relevant values.

### /outsideview
Use when outcomes from comparable cases can materially change the judgment.

Question: what happened in a defensible reference class before we rely only on the inside view?

Rules:

- seek observed comparable outcomes/base rates when material;
- state why the reference class is relevant;
- never fabricate a reference class, base rate or numerical prior;
- if no defensible outside view is available, keep that limitation explicit.

### /redteam
Use when a proposal deserves adversarial attack.

Material attacks must close through the Challenge workflow to recommendation impact.

### /premortem
Assume the decision failed and identify plausible failure paths, leading indicators and mitigations.

### /secondorder
Ask what happens after the immediate consequence; include downstream incentives/dependencies when material.

### /reversible
Assess how easy, costly or harmful it is to undo the decision. Reversibility should influence analysis depth and willingness to experiment.

### /killcriteria
Define observable facts that justify stopping, reversing or abandoning the path before sunk-cost attachment dominates.

### /nextproof
Use when a material unknown remains.

Question: what is the smallest new evidence capable of changing the recommendation?

For a falsifiable proof, prefer:

- hypothesis;
- question tested;
- smallest experiment or observation;
- required data;
- metric;
- proposed threshold, explicitly labeled as proposed;
- kill criterion;
- cost/effort;
- expected delay;
- what changes on PASS;
- what changes on FAIL.

#### Value of Information extension

Prioritize candidate proofs qualitatively by:

- how much the evidence could change the decision;
- how likely the unknown is to remain decision-relevant;
- cost and delay of acquiring it;
- reversibility of acting without it;
- whether a cheaper proof exists.

`HIGH | MEDIUM | LOW` information value may be used with justification. Do not invent precise probabilities or expected-value mathematics for appearance.

### /stop
Use at the end of research/analysis.

Question: can continued analysis materially change the recommendation enough to justify its cost/delay?

Normal output: `STOP`, `CONTINUE`, or `STOP_RESEARCH_AND_TEST` with a short reason.

`STOP_RESEARCH_AND_TEST` means a test is now more informative than more research; it does not mean the hypothesis is validated.

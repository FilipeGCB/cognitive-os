# Routing — Cognitive OS v1.4

## Default and materiality

Default depth is **Normal**.

Something is material when it can plausibly alter the decision/recommendation, scope, success criterion, reversibility, security/compliance, feasibility, a blocking dependency, or cost/time/effort by about 25% or more unless a better domain threshold is stated.

## Depth and soft budgets

### Fast

Low impact + easy reversal + low uncertainty.

- usually 0–1 external source;
- up to 2 lenses;
- up to 1 capability family;
- no deep research or crawl unless explicitly necessary.

### Normal

- usually up to 3 sources;
- up to 4 lenses;
- up to 2 capability families.

### Deep

- usually up to 8 sources;
- up to 6 lenses;
- up to 3 capability families;
- explicit challenge.

### Board360

- usually up to 12 sources;
- up to 8 lenses;
- up to 4 capability families;
- meaningful alternatives + challenge + kill criteria + next proof;
- robustness analysis may be used when deep uncertainty is material.

Exceed a soft budget only when the next evidence or method can still materially change the decision.

## Sensemaking before method choice

When the situation is materially ambiguous, classify its nature only enough to choose a strategy:

- **clear** → recover the rule/procedure and act proportionally;
- **complicated** → analyze, compare and seek expertise/evidence;
- **complex** → prefer safe-to-fail probes, observation and adaptation;
- **chaotic** → stabilize first, then analyze;
- **unclear** → perform additional sensemaking before committing to a method.

Do not expose these labels unless they improve the user's understanding.

## Full Flow / Audit

Auditability is separate from depth.

When explicitly requested or required by a formal gate:

- account for the adaptive phases and material conditional branches;
- use `NOT_APPLICABLE` for branches that were considered and do not apply;
- use `PARTIAL` or `BLOCKED` when a necessary branch is incomplete;
- record material failures, rate limits, truncation and unavailability;
- use `../schemas/cognitive-run-record.md`;
- never persist chain-of-thought.

## Capability routing

The core asks for abstract capabilities:

- current external information → **Web Search**;
- broad, multi-source, high-information-value external investigation → **Deep Research** when available/justified;
- repeated/large closed-corpus reasoning → **Grounded Corpus Research**;
- current code/repository state → **Repository Research**;
- authorized documents/files → **Document/File Research**;
- material quantitative work → **Data Analysis**;
- structured multi-page extraction → **Structured Crawl**;
- specialized technical security work → **Security Analysis**;
- procedure/skill/connectivity discovery → **Capability Discovery**.

Concrete implementations are chosen by the host or approved adapter. Vendor names never define the cognitive architecture.

## Existing capability first

Before filling a capability gap:

1. inspect the current host/surface when observable;
2. prefer a sufficient native or already configured capability;
3. avoid redundant installation;
4. if a gap remains, evaluate approved adapters under the installation-consent policy;
5. heavy/account/sensitive/write capabilities require specific consent.

## Temporal research

Mutable claims about current price, limits, licensing, terms, availability, release/status, provider capabilities or product behavior require current evidence when they can change the decision. Prefer primary/official sources.

If no real research occurred, do not say `researched` or imply current verification.

## Runtime truth

For material/auditable capability use:

```text
availability = AVAILABLE | UNAVAILABLE | UNKNOWN
invocation   = CALLED | NOT_CALLED
result       = SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE
```

- available but not called = available, not exercised;
- documentation or a host matrix is not invocation;
- a simple mental calculation is not Data Analysis tool execution;
- a truncated or failed material call cannot silently become COMPLETE.

## Failure recovery

When a material source/capability fails:

1. preserve the failure as evidence about the run;
2. retry or recover only proportionally;
3. use a safe alternative if one exists;
4. keep a gap visible when required evidence remains absent;
5. do not fill the gap silently with model knowledge.

## Stop and escalation

Stop when:

- no material unknown remains;
- the next evidence is unlikely to change the recommendation;
- a bounded test is cheaper or more informative than more research;
- the soft budget is exhausted and escalation has no material justification.

## Economy rule

> Use the smallest combination of sources, capabilities and methods sufficient to reduce material uncertainty, and describe only what was actually observed or executed.

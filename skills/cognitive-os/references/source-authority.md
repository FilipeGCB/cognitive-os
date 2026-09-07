# Source Authority — Cognitive OS v1.5

## Software and technical systems

Default authority order:

```text
observed code/tests/runtime state
> approved specification
> canonical documentation
> historical records/context
> conversation
> generic model knowledge
```

When the question depends on current implementation, observe the authorized repository/system when material. If that observation fails, truncates or rate-limits, keep the limitation visible rather than silently substituting model knowledge.

## Projects and decisions

```text
approved canonical decision/document
> versioned decision record
> authorized internal sources
> historical context
> conversation
```

A conflict between documentation and observed implementation must be surfaced. Authority depends on the question: implementation behavior is answered by observed implementation; intended design may be answered by an approved spec.

## Cognitive OS itself

For runtime behavior, the installed, versioned skill package is authoritative. For development, release status and latest public version, the canonical repository/release may be consulted when current state matters.

Runtime use must not require consulting the repository merely to know how Cognitive OS works.

## External information

```text
current primary/official source
> validated corpus
> reliable secondary source
> community/opinion
```

Mutable material claims such as price, limits, licensing, terms, availability, version/status, preview/GA state or provider capability require current evidence when change could affect the decision.

## Grounded corpus

A corpus tool can organize, retrieve and compare sources; it does not increase the authority of those sources. Citation quality and corpus provenance remain separate questions.

## Outside View and base rates

Reference classes/base rates must come from observed evidence or a clearly identified dataset/source. Do not invent numerical priors, success rates or reference classes simply because an outside view would be useful.

When no defensible reference class is available, say so and continue using other evidence.

## Capability/runtime evidence

Documentation, historical preflight or a report that a tool exists is a baseline, not proof of current invocation.

For an auditable run:

```text
baseline/context
+ runtime observation
→ runtime capability snapshot
```

Observed runtime evidence wins for the same host/surface/capability.

## Quantitative work

Distinguish:

```text
simple reasoning/calculation
≠ calculator invocation
≠ Python/Data Analysis invocation
≠ dataset analysis
```

Do not attribute a result to a tool that did not run. Scenarios are not forecasts unless evidence and forecasting method justify the claim.

## Security

Security-analysis output is technical evidence, not authorization. Official origin does not remove the need to inspect permissions, read/write surface and material security unknowns.

## Conflict handling

When sources materially disagree, show:

1. what each source says;
2. which source is more authoritative for the question and why;
3. whether the disagreement is temporal/version-related;
4. what evidence could resolve it.

## Context

Context helps reconstruct intent and history; it does not outrank observed implementation, approved canonical decisions or current primary evidence when those are materially relevant.

## Truth-domain mapping

Before inferring a cause from multiple systems, establish which system is
authoritative for each fact class and reconcile mismatches first:

| Fact class | Preferred authority | Common secondary | Do not equate automatically with |
|---|---|---|---|
| transaction | payment/ledger | commerce | behavior or order count |
| order | commerce | payment/ledger | settlement |
| behavior | analytics | commerce events | transactions |
| pipeline | CRM | billing | recognized revenue |
| software state | repository/tests | documentation | historical branch notes |
| decision | versioned decision/spec | authorized internal sources | stale memory |

The current verified state wins a stale document when the source authority for
that question says it should. Record contradictions and the reconciliation
method in the Evidence and Gap/Failure ledgers before causal interpretation.

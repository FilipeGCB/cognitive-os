# Research Routing — Cognitive OS v1.5

Research depth is driven by **decision impact and information value**, not by the availability of an impressive tool.

## Route

### Web Search

Use for current/simple external facts, a small number of sources, or bounded verification.

### Composed research

Use ordinary search plus proportional triangulation when several sources are needed but a full Deep Research run is not justified.

### Deep Research

Use a native host Deep Research capability when all are materially true:

- breadth/depth beyond ordinary search can change the recommendation;
- the cost/delay is justified by information value;
- the host exposes a suitable capability;
- the decision benefits from multi-source synthesis rather than one authoritative lookup.

If the host requires **user activation**, explain why deeper research may change the decision and tell the user exactly what native mode/control to activate. Do not pretend to invoke it when the host cannot.

If unavailable, use a bounded fallback composed from available capabilities and disclose material limitations.

### Grounded Corpus Research

Use when the important universe is a closed/curated or large persistent corpus and the task requires repeated source-grounded comparison/synthesis.

Routing preference:

1. sufficient native host corpus capability already available;
2. already configured trusted adapter;
3. approved implementation offered under consent policy;
4. bounded Document/File Research fallback with limitation disclosed.

NotebookLM is one implementation. It is not required by the core.

### Structured Crawl

Use when the need is structured/multi-page collection that ordinary Web Search does not efficiently or reliably provide. Prefer an existing host capability before adding a crawler provider/adapter.

## Source authority still applies

A research tool does not make a weak source authoritative. Prefer primary/current sources for mutable material claims and preserve contradictions.

## Direct routing signals

When a request already states that internal documents and current external
sources must be reconciled across multiple queries, route to Grounded Corpus
Research immediately (while retaining separate internal/external evidence).
Do not ask for the subject, URLs or a corpus inventory before stating that
route; those details are inputs to the plan, not a reason to hide a determined
capability route.

## Stop

Stop research when:

- additional sources are unlikely to change the recommendation materially;
- a next proof/experiment has higher information value;
- a required capability remains unavailable and further retries have low expected value;
- the chosen depth budget is exhausted without a justified escalation.

## Web versus grounded corpus

Use Web for open discovery, current facts, new sources, market/regulatory
signals and freshness. Use a Grounded Corpus for repeated queries over a
curated corpus, cross-source comparison, contradictions, revisitation,
internal plus external evidence, context pressure and auditability. NotebookLM
is an optional host-dependent implementation, not a core dependency or a
synonym for every large corpus.

In Deep, Board360 and Full Flow, strongly consider corpus migration when
material sources accumulate, internal and external evidence must be joined,
queries repeat, compaction/context pressure appears, open discovery converges,
traceability degrades or a future run will revisit the same corpus. These are
configurable soft signals, not universal hard thresholds. Reconcile sources
according to `source-authority.md` before inferring causality.

## Research budget controller

Before a deep run, write the question, subquestions, source classes, expected
evidence, budgets and stop condition. Track observable counters where the host
allows it. Check at approximately 50% and 80%, and before a hard limit; reserve
budget for validation, contradiction checking, challenge, synthesis and
closure. If a rate limit or hard guardrail is reached:

```text
freeze search → synthesize evidence already obtained → record limitation/gap
→ choose fallback or next proof → close the run
```

Do not claim grounded-corpus use without a runtime source read. If the corpus is
unavailable, use an authorized composed fallback and preserve the limitation.

When compaction occurs, record a checkpoint that explicitly revisits the
grounded-corpus choice, source traceability and remaining budget. The
checkpoint is an observable control point, not permission to silently drop
provenance.

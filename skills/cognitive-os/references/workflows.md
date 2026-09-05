# Workflows — Cognitive OS v1.5

Workflows compose only the lenses and capabilities needed for the current problem. Depth is controlled by routing; do not create duplicate workflows for depth variants.

When ambiguity is material, use sensemaking before selecting the workflow. Full Flow/Audit records applicable phases/branches but does not force non-applicable workflows.

## /ground

Purpose: reconstruct factual state before analysis.

`context → authoritative sources → current state → prior decisions → constraints → conflicts/staleness → current understanding`

## /discover

Purpose: understand before deciding.

`context → adaptive interview if needed → evidence → assumptions → unknowns → contradictions → missing question → next proof`

For product/user discovery, selectively load JTBD, Mom Test and hypotheses when they can change understanding.

## /diagnose

Purpose: find cause and principal constraint.

`context → initial hypothesis → evidence → causal analysis as justified → bottleneck → alternative causes/challenge → next proof`

5 Whys is optional, not mandatory. Use Ishikawa/Pareto/leverage when the problem is genuinely multicausal or data concentration matters.

## /decide

Purpose: structure a material decision.

`framing → evidence → assumptions → meaningful alternatives → values/trade-offs → reversibility → outside view when material → second-order effects → premortem → kill criteria → challenge → next proof/stop → recommendation`

Before closure, run the Decision Quality check proportionally:

- framing sufficient?
- meaningful alternatives considered?
- information/evidence sufficient for chosen depth?
- values/trade-offs explicit enough?
- reasoning survived proportional challenge?
- next action/no-action state clear?

This check is internal by default.

## /challenge

Purpose: attempt to break a proposal and close the impact of material attacks.

```text
attack / contradiction / premortem / missing question
↓
evidence or plausibility
↓
what would break
↓
recommendation impact
maintains | weakens | conditions | reverses
↓
mitigation / next proof
```

In Board360 or Full Flow/Audit, every material attack must close recommendation impact. Listing risks without explaining effect on the recommendation is incomplete.

Steelman, inversion and failure modes may be loaded when risk justifies them.

## /research

Purpose: gather enough evidence to answer the decision question.

`question → depth/value routing → authoritative sources/capabilities → proportional triangulation → contradictions → next proof/stop`

Read `research-routing.md` for capability selection.

Mutable material external claims require current evidence when they may have changed. Failure/truncation/rate-limit in required evidence remains a gap.

### /deepresearch

Alias for `/research` at Deep or Board360 depth. It is not a vendor-specific workflow. Native Deep Research is one possible capability implementation.

## /capability

Purpose: determine whether a better reusable procedure or connection already exists before building/installing something new.

```text
need
→ classify
   ├── reusable procedure → Find Skills
   └── connectivity/tooling → Find MCPs / provider API / host-native capability
→ inspect real candidates
→ capability gate / Gauntlet when persistent
→ reject | test | promote | block | continue researching
```

Discovery is not installation. Finding a tool does not prove that it is safe, available, invoked or appropriate.

The `/capability` pipeline is material-gap driven: existing capability, local
discovery, approved external discovery, candidate assessment, Gauntlet,
consent, execution/installation and runtime verification. Find Skills/Find MCP
are discovery assets, not candidates; `related_skills` is not a substitute for
discovery. External discovery being unavailable is an explicit state with a
fallback, never a simulated search result. Temporary external execution is
subject to the same security and consent boundary as installation.

### `/research` budget and migration

Deep research begins with a budget contract and checkpoints. Reconsider Web →
Grounded Corpus when source crossing, internal/external evidence, repeated
queries, compaction/context pressure, convergence, traceability degradation or
future revisitation makes a persistent corpus materially useful. NotebookLM is
optional and host-dependent. At a hard search limit, freeze, synthesize the
evidence already observed, mark the gap, select the next proof/fallback and
close.

### Full Flow/Audit V1.5 ledgers

When requested, include Phase, Conditional Branch, Capability, Method,
Evidence, Gap/Failure, Challenge, Mutation and Persistent Side Effects ledgers,
plus research budget and provider/host failure summaries. Keep flow coverage,
execution integrity, run status and decision state separate. Do not persist
private chain-of-thought.

### Find Skills

Search in this order when material and actually accessible:

1. core/workflows/lenses already present;
2. project/repository skills;
3. skills installed/exposed by the host;
4. trusted registries/directories;
5. GitHub/Web when external discovery can change the decision.

A plugin related to a problem is not evidence that its skill contract covers the need. Inspect manifests/SKILL.md when material.

### Find connectivity

Compare host-native features, official apps/connectors/MCPs/APIs and trusted community implementations. MCP is not automatically better than API/REST.

For sensitive capabilities, unknown critical permissions/read-write/security information blocks promotion.

## Modes

### /board360

Maximum justified depth applied to the active workflow. Requires meaningful alternatives, challenge, kill criteria, next proof and stop discipline. Under deep uncertainty, `/robustness` may be loaded.

### Full Flow / Audit

Auditability mode, separate from depth. Account for relevant phases/branches and observable execution without chain-of-thought.

## Extended workflows

### /architect

`technical ground → first principles → boundaries/invariants/dependencies/failure modes as needed → trade-offs → migration/eval if applicable`

### /product

`discover → JTBD/ICP/pain chain/hypotheses/wedge/value proposition as needed → outside view if material → next proof`

### /learn

`Feynman / mental model / analogy / comparison as needed`

### /repo-mine

Bounded investigation of a technology/capability candidate. Evaluate proportionally:

- identity/repository/ref/release;
- provenance/license;
- maintenance/update model;
- security/auth/credential handling;
- API/tool surface and read/write behavior;
- deployment/installation footprint;
- supply-chain risk when material;
- architectural fit/overlap/observability/reversibility;
- limitations of the investigation.

Do not call the investigation complete if material evidence could not be observed.

## Output / handoff

`/execute` is not a cognitive workflow.

After a clear decision, Cognitive OS may prepare a draft/proposed Decision Pack or handoff. Consequential execution remains outside the decision layer unless separately authorized by the user and host policy.

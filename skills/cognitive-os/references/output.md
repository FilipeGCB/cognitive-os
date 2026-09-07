# Output and Editorial Policy — Cognitive OS v1.4

Cognitive OS should terminate in **understanding, not process reporting**.

## Output layers

```text
adaptive analysis
↓
Decision Pack            canonical structured decision truth
├── Decision Brief       human/editorial projection
│   ├── chat
│   ├── Markdown
│   └── optional derived HTML
└── downstream handoff

Cognitive Run Record     separate audit/execution evidence when applicable
```

Do not create another parallel canonical decision model.

## When to use a Decision Brief

- simple factual request → answer simply;
- small diagnosis → conclusion + explanation + next step;
- material decision → Decision Brief;
- shareable/high-stakes decision → fuller Decision Brief + Decision Pack when useful;
- Full Flow/Audit → human Brief plus structured audit artifacts when required.

For a decision brief about an existing capability and a possible new audience,
lead with a bounded decision (or decision condition), then name the audience,
problem and expected outcome before describing any market opportunity. Keep
mechanism, product, operation and market opportunity as separate claims. If
the prompt does not supply a real case, label a compact illustrative scenario
as hypothetical rather than presenting invented facts as validated evidence.

## Editorial hierarchy

For a material decision, the reader should normally learn, in this order:

1. **the decision/conclusion**;
2. **idea evolution** — what changed from the initial proposal, when there was a meaningful initial proposal;
3. **decisive reasons** — only factors that actually moved the decision;
4. **what could still change it** — material risk, condition or unknown;
5. **next move** — one clear action, experiment, wait/stop or deliberate no-action state.

This is a semantic hierarchy, not a mandatory visible five-section template.

## Idea evolution

When applicable, make the delta easy to see:

> You started with A. The analysis matured it into B. Here is what changed and why.

Use prose by default. Use a compact comparison table only when it makes the transformation faster to understand.

## Progressive technical disclosure

```text
DECISION
↓
HUMAN EXPLANATION
↓
USEFUL DETAIL
↓
TECHNICAL DETAIL IF NEEDED
↓
EVIDENCE / AUDIT IF REQUESTED
```

Do not lead with implementation internals when the user needs the decision first.

## Hide framework ritual by default

In normal mode, do not dump internal process such as:

- `Phase 3 complete`;
- `lens used: /redteam`;
- raw capability enums;
- Gauntlet status;
- internal sensemaking category;
- a list of methods used merely to demonstrate rigor.

Expose a method or technical state when the shape itself explains the insight, the user explicitly requests auditability, or the state materially changes what the user should trust/do.

## Internal states in human language

Do not expose raw enum values by default.

Translate, for example:

- `READY` → ready to advance;
- `RECOMMENDATION_ONLY` → a recommendation exists, but final commitment still depends on the user/context;
- `TEST_REQUIRED` → the direction is plausible but should be tested before commitment;
- `MORE_RESEARCH_REQUIRED` → missing evidence can still change the decision;
- `BLOCKED` → the decision cannot responsibly be closed yet.

Do not invent pseudo-precision confidence percentages.

## Method visibility

Show a method only when it improves comprehension:

- 5 Whys when the causal chain is itself the insight;
- decision tree when branching conditions determine the answer;
- trade-off table when real alternatives need comparison;
- timeline when chronology is decisive;
- causal diagram when relationships are hard to express linearly.

Otherwise report the discovery, not the toolbox.

## Chat and Markdown readability

- put the conclusion in the first meaningful block;
- use informative headings, not generic `Analysis / Considerations / Conclusion` boilerplate;
- paragraphs usually 2–4 sentences;
- leave real whitespace between distinct ideas;
- bold sparingly;
- avoid walls of bullets;
- keep tables compact and purposeful;
- use technical jargon only when the subject requires it;
- avoid decorative badge/card overload;
- use almost no emoji by default;
- visual richness is proportional to decision complexity.

Markdown is the portable human-source format. Avoid requiring platform-specific Markdown extensions.

## HTML derived view

HTML is optional and derived from the Decision Brief. It is never the source of truth.

Default target:

- system UI font stack;
- body around 17–18px;
- line height around 1.6;
- reading width around 720–820px / roughly 70–75 characters;
- strong title/section hierarchy;
- generous section spacing;
- restrained borders/cards;
- neutral palette with controlled accent;
- dark mode;
- responsive/mobile;
- accessible contrast and visible focus;
- state is never communicated only by color.

The visual feel should resemble an excellent editorial publication or executive memo, not a SaaS dashboard.

## Audit mode exception

Full Flow/Audit may append the structured evidence/status summary required by its contract. The human-facing recommendation should still lead with comprehension rather than the ledger.

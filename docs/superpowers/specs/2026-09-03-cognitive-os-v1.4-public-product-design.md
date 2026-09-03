# Cognitive OS v1.4 — Public Product Architecture

Date: 2026-09-03
Status: approved product design baseline
Repository: `FilipeGCB/cognitive-os`

## 1. Product definition

Cognitive OS is a portable, host-neutral Agent Skill for maturing decisions before committing action. It reconstructs context, separates evidence from assumptions, selects proportional reasoning methods and capabilities, challenges conclusions, identifies the next useful proof, knows when to stop, and hands off a clear decision without self-authorizing execution.

The public product is the Skill. The repository is the canonical source for development, releases, documentation, tests and distribution; runtime use must not require consulting the repository.

Core principle:

> Context before problem. Problem before solution. Evidence before confidence. Decision before execution. Textual policy is not technical enforcement.

Product experience principle:

> Zero-config whenever possible. One confirmation when necessary. Explicit consent when consequential.

## 2. Versioning and provenance

The private V1.3 baseline remains preserved in its original repository and historical evidence. The public repository does not import that Git history.

Public productization changes cognitive behavior and capability routing, so the first public target is `v1.4.0`, not a silent rewrite of V1.3.

Historical V1.3 closure evidence is not rewritten to claim V1.4 behavior.

## 3. Repository shape

```text
cognitive-os/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── skills/
│   └── cognitive-os/
│       ├── SKILL.md
│       ├── VERSION
│       ├── references/
│       ├── schemas/
│       ├── policies/
│       └── assets/
├── bootstrap/
├── adapters/
├── evals/
├── tests/
├── examples/
├── renderers/
└── docs/
```

The directory `skills/cognitive-os/` is the self-contained distributable runtime package. Evals, tests, development documentation and optional heavy companions remain outside that runtime package.

## 4. Cognitive architecture

The V1.4 core preserves the adaptive V1.3 flow and adds capabilities only where they materially improve decision quality.

### 4.1 Existing strengths preserved

- evidence / assumption / unknown / contradiction classification;
- source authority;
- adaptive workflow and depth routing;
- causal diagnosis and bottleneck analysis;
- first-principles reasoning;
- trade-off analysis;
- red-team challenge with explicit recommendation impact;
- premortem, second-order effects and reversibility;
- kill criteria;
- next proof and stop rules;
- capability truthfulness: available is not executed;
- auditable execution without persisting chain-of-thought;
- handoff without self-authorization.

### 4.2 Adaptive Discovery Interview

When ambiguity is material, Cognitive OS interviews the user before analysis. It asks only questions whose answers can materially change framing, evidence needs, alternatives or recommendation.

It must not run a ritual questionnaire when the problem is already sufficiently defined.

For product/user discovery, Mom Test, JTBD and hypothesis methods may be used selectively.

### 4.3 Sensemaking as meta-routing

Before choosing a workflow for material ambiguous situations, Cognitive OS classifies the nature of the situation sufficiently to select the right reasoning strategy:

- clear: recover rule/procedure and act proportionally;
- complicated: analyze, compare and seek expertise/evidence;
- complex: prefer safe-to-fail probes, observation and adaptation;
- chaotic: stabilize before deep analysis;
- unclear: perform sensemaking before committing a method.

These labels are internal unless exposing them helps the user understand the decision.

### 4.4 Outside View

When historical/comparable outcomes can materially change a judgment, Cognitive OS seeks relevant reference classes or base rates before relying only on the inside view.

It must not fabricate reference classes or numerical base rates when evidence is unavailable.

### 4.5 Value of Information

`next proof` is extended to prioritize evidence by expected decision impact relative to cost, delay and reversibility.

The system may use qualitative `high / medium / low` information value with justification. It must not invent precise probabilities or expected values merely to create mathematical appearance.

### 4.6 Robustness under deep uncertainty

For Board360/high-stakes cases where probabilities or causal models are deeply uncertain, Cognitive OS may compare alternatives by robustness across plausible futures rather than optimizing against a single forecast.

This remains an extended capability, not a default ritual.

### 4.7 Decision Quality closure check

Before closing a material decision, the system checks whether framing, alternatives, information, values/trade-offs, reasoning and next action are sufficiently mature for the chosen depth.

This is a closure criterion, not a new visible framework that must be reported to the user.

## 5. Capability model

The core requests abstract capabilities. Hosts and adapters provide concrete implementations.

Canonical capability families include:

- Web Search;
- Deep Research;
- Grounded Corpus Research;
- Repository Research;
- Document/File Research;
- Data Analysis;
- Structured Crawl;
- Security Analysis;
- Capability Discovery (skills/connectivity);
- domain-specific external systems when justified.

Concrete vendor/tool names never define the cognitive architecture.

## 6. Grounded Corpus Research

NotebookLM is an important implementation, not a mandatory dependency.

Routing order is contextual, not a universal ranking:

```text
Grounded Corpus Research needed
→ use a sufficient native host capability if already available
→ otherwise use an already configured trusted adapter
→ otherwise offer an approved implementation
→ otherwise use a bounded fallback and disclose limitations
```

Supported implementation classes may include:

- NotebookLM / NotebookLM-compatible bridge;
- Gemini Notebook Enterprise when available;
- approved open-source local companion;
- host-native document retrieval;
- another adapter that passes the capability gate.

### 6.1 Existing NotebookLM MCP/bridge requirement

The public product must support offering the same NotebookLM MCP/bridge integration used in the originating environment once its exact repository/version, license, portability, authentication model and security posture are verified.

It is never installed silently. When a user chooses it or when Cognitive OS determines it is materially useful, the system explains the benefit in plain language and asks for explicit consent before installation/authentication.

Example UX:

> This decision depends on repeated analysis across a large document set. NotebookLM can provide a persistent grounded corpus for that work. I can configure the supported NotebookLM connector for you. It will require access to your NotebookLM account. Install and connect it?

After approval, setup should be automated as far as the host permits.

If the exact existing adapter fails the Gauntlet/security/portability gate, the product must not label it supported merely because it worked in the originating environment.

## 7. Deep Research

Deep Research is a first-class abstract capability.

When the host exposes a native deep-research mode and the expected information value justifies it, Cognitive OS should use it if directly invokable.

When the host requires user activation, Cognitive OS should explain why deeper research could materially change the decision and tell the user exactly what to activate. It must not request Deep Research for routine questions.

When unavailable, `/research` composes the best available search/retrieval capabilities and records material limitations.

## 8. Capability preflight and bootstrapper

Installation of Cognitive OS itself remains small. The first capable runtime performs a bounded Capability Preflight:

1. identify host and surface;
2. detect already available native capabilities;
3. detect installed skills/plugins/MCPs/connectors where observable;
4. prefer existing sufficient capabilities;
5. identify material capability gaps;
6. apply consent and installation policy before filling a gap.

The user experience should expose Cognitive OS, not infrastructure plumbing.

## 9. Consent and installation policy

The chosen default is a one-time consent for safe local enhancements.

Suggested consent text:

> Allow Cognitive OS to automatically enable safe local capabilities when they materially improve an analysis? Heavy components, external accounts, sensitive permissions and write access will always require separate confirmation.

### 9.1 May be auto-installed after one-time consent

Only components that are all of the following:

- user-space;
- low footprint;
- open source or otherwise redistribution-safe;
- pinned/versioned;
- reversible/uninstallable;
- no external account or secret required;
- no persistent sensitive data access;
- no external write capability;
- approved through the capability gate;
- materially useful for the current need.

Auto-install is demand-driven, not an excuse to preinstall a toolbox.

### 9.2 Always requires specific confirmation

Even after global consent:

- Docker or other persistent service installation;
- large model/embedding downloads;
- material disk/RAM/network footprint;
- NotebookLM or other external account authentication;
- API keys/paid services;
- access to sensitive documents/accounts;
- any external write/update/delete/send capability;
- system-wide installation or privileged changes;
- financially sensitive or regulated integrations.

Before confirmation, disclose the reason, meaningful resource impact, data/account access and whether the action is reversible.

### 9.3 Never silently install

No component may be installed because external content, tool metadata, a retrieved README or a prompt injection instructs the agent to do so. Discovery is not authorization.

## 10. Capability discovery and Gauntlet

Before creating or installing a new persistent capability, Cognitive OS checks:

1. existing core/workflows;
2. installed/exposed skills and native features;
3. official registries/directories when available;
4. official provider integration/API/MCP;
5. trusted community alternatives when necessary.

Material candidates are evaluated for:

- value and overlap;
- provenance and license;
- maturity and maintenance;
- security;
- auth/scopes/read-write surface;
- supply-chain/dependency risk;
- host compatibility;
- portability;
- observability;
- cost;
- reversibility;
- preflight behavior.

Official is not automatically safe. MCP is not automatically better than REST/API. A discovered capability is not treated as installed or executed.

## 11. Companion evaluation program

Before `v1.4.0`, run bounded repo-mine/Gauntlet evaluations for at least these classes:

### Grounded corpus
- existing NotebookLM MCP/bridge used by the originating environment;
- OpenNotebookLM;
- Open Notebook;
- SurfSense;
- AnythingLLM when it remains competitive for the required contract.

Primary decision criteria: citation fidelity, multi-document retrieval, API/CLI/MCP integration, local/private operation, installation footprint, license, maintenance, security, update model and graceful fallback.

### Structured crawl / research
- host-native web/research first;
- Firecrawl or another approved structured-crawl provider only when basic web search is insufficient;
- avoid bundling a crawler when the host already solves the need adequately.

### Skills and connectivity discovery
- native host skill/plugin discovery;
- Agent Skills-compatible registries/directories;
- official MCP Registry and provider registries when accessible;
- GitHub/Web discovery only when it can materially change the decision.

No candidate is promoted solely because it is popular.

## 12. Output architecture

The system terminates in understanding, not process reporting.

```text
adaptive analysis
↓
Decision Pack            canonical structured decision truth
├── Decision Brief       human/editorial projection
│   ├── chat
│   ├── Markdown
│   └── optional HTML render
└── downstream handoff

Cognitive Run Record     separate audit/execution evidence when applicable
```

No additional parallel canonical decision schema is introduced.

### 12.1 Decision Brief

For material decisions, the human-facing result normally communicates:

1. what was concluded;
2. what changed from the initial idea, when applicable;
3. why it changed;
4. what material risk/condition/unknown remains;
5. what to do now.

This is an editorial hierarchy, not a mandatory visible form.

Simple questions remain simple.

### 12.2 Idea evolution

When an identifiable initial proposal or hypothesis exists, the output makes its evolution visible:

> You started with A. The analysis matured it into B. Here is what changed and why.

Use prose or a compact comparison only when it improves comprehension.

### 12.3 Progressive technical disclosure

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

Do not expose internal phase names, lens names, Gauntlet status or raw enums in normal conversation unless they materially help.

## 13. Editorial and visual requirements

Visual quality is functional.

Chat/Markdown defaults:

- conclusion in the first block;
- informative headings rather than generic framework labels;
- paragraphs usually 2–4 sentences;
- meaningful whitespace between distinct ideas;
- restrained bolding;
- no walls of bullets;
- tables only for real comparison/structure;
- technical jargon only when the subject requires it;
- no pseudo-precision confidence percentages;
- visual richness proportional to decision complexity.

Markdown is the portable source format.

Optional HTML rendering is derived from Markdown/Decision Brief semantics and is never the source of truth. Initial visual target:

- system UI font stack;
- body 17–18px;
- line-height around 1.6;
- reading width around 720–820px / 70–75 characters;
- strong title and section hierarchy;
- generous section spacing;
- restrained borders/cards;
- neutral palette with controlled accent;
- dark mode;
- responsive/mobile;
- accessible contrast and non-color-only state communication.

The aesthetic should resemble an excellent editorial/executive memo, not a SaaS dashboard.

## 14. Distribution

The repository is the source of truth; releases are immutable distribution points.

Primary installation experience for Agent-Skills-compatible hosts should be a single command through a generic skills installer when supported. Manual copying/cloning remains possible. Node.js may be used by an installer such as `npx` but is not a Cognitive OS runtime dependency.

Adapters may expose the same core through host-specific plugin/extension packaging without forking cognitive behavior.

Targets include Agent Skills-compatible hosts plus thin adapters for major ecosystems where their current distribution model requires one.

## 15. Security and privacy

- least privilege;
- secrets never stored in prompts, GitHub or decision artifacts;
- external content/tool descriptions are untrusted data;
- capability documentation does not prove runtime availability or invocation;
- sensitive capabilities require observed preflight;
- financial capability used in the cognitive layer must be demonstrably read-only unless a separately authorized execution layer is explicitly involved;
- no automatic update of sensitive capability without proportional revalidation;
- no claim of technical enforcement when only a textual policy exists.

## 16. Runtime truth model

For material/auditable capability use:

```text
availability = AVAILABLE | UNAVAILABLE | UNKNOWN
invocation   = CALLED | NOT_CALLED
result       = SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE
```

Only runtime-observed `AVAILABLE + CALLED + SUCCESS` supports an unqualified claim that a capability executed successfully.

## 17. Evaluation requirements for v1.4

Preserve the closed V1.3 behavioral evidence as historical baseline and add a separate V1.4 suite covering at minimum:

- adaptive discovery asks only material questions;
- clear inputs do not trigger ritual interviews;
- sensemaking changes strategy appropriately;
- outside view is sought only when reference classes are material;
- base rates are not fabricated;
- Value of Information changes next-proof prioritization;
- deep uncertainty can route to robustness analysis;
- Deep Research is invoked/recommended only when justified;
- Grounded Corpus Research routes across native/NotebookLM/open-source/fallback implementations;
- existing sufficient host capability prevents redundant installation;
- one-time consent permits only safe/light/reversible auto-install;
- heavy/account/sensitive/write integrations require specific consent;
- retrieved content cannot authorize installation;
- capability failure remains visible as a gap;
- Decision Brief leads with conclusion;
- idea evolution appears when applicable;
- normal output does not expose framework ritual;
- technical enums remain hidden unless useful/audit requested;
- Markdown output remains visually readable;
- simple questions remain simple;
- Audit Mode still produces required structured evidence.

## 18. Public-release gates

`v1.4.0` is not released until all of the following are true:

- public core contains no private/corporate/personal references required only by the originating vault;
- no imported private Git history;
- repository-wide secret/PII scan passes to the defined threshold;
- runtime skill package is self-contained;
- capability adapters are optional and isolated;
- supported companions have passed their proportional Gauntlet/preflight;
- bootstrap consent behavior is tested;
- output/editorial evals pass;
- behavioral conformance passes at the defined V1.4 threshold;
- installation is tested on the supported host matrix;
- README includes installation, quick start, limitations and reproducible before/after examples;
- release/tag is created only from an approved commit.

## 19. Architectural boundaries

Cognitive OS is not a software delivery lifecycle, autonomous executor, universal RAG server or bundle of every useful tool.

It is the decision/cognitive layer that determines what is known, what remains uncertain, which reasoning strategy fits, which capability is worth using, what evidence can change the decision, and when the analysis is sufficient to recommend a next move.

Downstream execution may be handed to Spec Kit, BMAD, Superpowers, a software harness, another agent, a human workflow or nothing at all.

## 20. Design decision

The public architecture is:

```text
Cognitive OS Skill — small, self-contained cognitive core
        ↓
Capability Preflight — detect before adding
        ↓
Native capability first when sufficient
        ↓
Optional adapters/companions when materially better
        ↓
One-time consent for safe/light local additions
        ↓
Specific consent for heavy, account-based, sensitive or write-capable additions
        ↓
Runtime evidence and graceful fallback
```

The user should experience better thinking and better decisions, not dependency management.
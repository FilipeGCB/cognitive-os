# Extended Lenses — Cognitive OS v1.4

This library is **not loaded by default**. Use an extended lens only when a specialized workflow, explicit request or material unknown justifies the extra context.

## Truth / analysis

### /signalvsnoise
Separate signal, opinion, exception and noise.

### /ishikawa
Map families of causes in multicausal problems.

### /pareto
Find impact concentration when data supports it.

### /leverage
Identify the intervention point with the best impact-to-change ratio.

## Architecture

### /boundaries
Define validity conditions and system limits.

### /invariants
Identify guarantees that must remain true.

### /dependencies
Map material input/output dependencies.

### /blast-radius
Assess the surface affected by a change or failure.

### /migration
Design transition, coexistence, rollback and cutover constraints.

### /adr
Record an architectural decision after it is made.

## Challenge / risk

### /steelman
Construct the strongest serious argument against the leading position.

### /inversion
Ask what would reliably cause failure, then invert those conditions.

### /failuremodes
Map specific failure modes, effects, detectability and mitigation.

### /optionality
Assess which path preserves valuable future choices.

### /regret
Assess likely regret across a relevant time horizon without inventing numeric certainty.

### /robustness
Use under deep uncertainty when probabilities or causal models are not trustworthy enough for a single optimal forecast.

Question: which option remains acceptable across multiple plausible futures or assumption sets?

Use only when uncertainty is genuinely deep. Compare fragility, thresholds, reversibility and adaptation paths; do not manufacture probability distributions.

## Discovery / product

### /jtbd
Identify the progress/job the user is actually trying to accomplish.

### /momtest
Ground discovery in concrete past/current behavior rather than hypothetical praise or stated intent.

### /painchain
Connect operational pain to human/financial consequence and decision ownership.

### /hypotheses
Convert beliefs into falsifiable hypotheses.

### /wedge
Find the smallest entry point that creates value and supports expansion.

### /icp
Identify the customer profile with pain, urgency, budget and decision power.

### /valueprop
Translate a feature/capability into purchased value.

### /pricing
Relate price to value unit, alternatives and adoption friction.

### /moat
Assess mechanisms of defensibility rather than feature novelty alone.

### /commoditize
Ask what remains valuable if current technical capabilities become commodity.

## AI / RAG / agents

### /eval
Define cases, metrics, rubrics and thresholds with clear provenance.

### /ragtrace
Trace retrieval → ranking → context → response and identify where grounding failed.

### /contextaudit
Audit context presence, relevance, conflict and recency.

### /agentboundary
Define autonomy, approval, prohibitions and escalation path.

## Learning

### /feynman
Explain simply to expose gaps.

### /mentalmodel
Model inputs, transformation, outputs, feedback and failure modes.

### /analogy
Use an analogy and explicitly state where it breaks.

### /compare
Compare options across explicit, decision-relevant dimensions.

## Loading rule

Load one or more lenses only when:

1. the active workflow explicitly needs them;
2. the user asks for the method;
3. core lenses cannot resolve a material unknown;
4. the expected decision-quality gain justifies the context cost.

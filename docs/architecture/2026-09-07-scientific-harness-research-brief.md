# Brief de Pesquisa e Arquitetura
## Cognitive OS — evolução para um Scientific Research & Decision Harness com execução resiliente

**Data:** 2026-09-07  
**Objetivo:** entregar este documento ao **Cognitive OS atual** para que ele próprio investigue, critique e recomende a evolução do produto.  
**Escopo desta rodada:** **pesquisa e decisão arquitetural**. Não implementar mudanças produtivas ainda.

---

# 1. Contexto

O Cognitive OS já evoluiu de uma simples coleção de prompts para um **harness portátil de investigação e decisão**, cujo núcleo cognitivo é uma **Agent Skill** e cuja execução depende das capabilities disponíveis em cada host.

A arquitetura atual já possui, em diferentes graus:

- framing e sensemaking;
- roteamento por profundidade;
- pesquisa web;
- pesquisa profunda;
- grounded corpus;
- pesquisa de repositório;
- análise de dados;
- discovery de Skills/MCPs;
- Gauntlets/challenge;
- evidência, gaps e next proof;
- segurança e consentimento;
- telemetria/observabilidade;
- contratos de disponibilidade, invocação e resultado;
- adapters e distribuição multi-host.

Entretanto, as últimas investigações e o dogfooding no Claude Code revelaram que ainda existe uma lacuna entre:

1. **capability abstrata necessária**;
2. **executor concreto escolhido**;
3. **recuperação quando esse executor falha**;
4. **degradação para uma capability inferior**.

Hoje o Cognitive OS já prevê fallback, mas em vários casos o fallback muda a própria capability. O objetivo agora é investigar como transformar isso num harness mais resiliente **sem explodir custo, latência ou complexidade**.

Ao mesmo tempo, surgiu uma segunda percepção: o core do produto pode estar perdendo elementos de sistemas científicos modernos, especialmente na forma de:

- gerar hipóteses;
- escolher a próxima evidência;
- medir ganho de informação;
- testar causalidade;
- desenhar experimentos;
- atualizar crenças;
- resolver contradições;
- calibrar incerteza;
- decidir quando parar.

Esta pesquisa deve tratar **primeiro do core científico**, e **depois da camada de ferramentas/executores**.

---

# 2. Princípios arquiteturais já discutidos

Considere estes princípios como hipóteses de trabalho a serem **testadas e criticadas**, não como dogmas.

## 2.1 Cognitive OS como harness lógico, não necessariamente runtime próprio

A formulação atual mais adequada é:

> **Cognitive OS é um harness portátil de investigação e decisão. Seu core cognitivo é uma Agent Skill. O runtime é fornecido pelo host, e bundles/adapters materializam capabilities adicionais em cada superfície.**

Evitar os dois extremos:

- `Cognitive OS = apenas um SKILL.md`;
- `Cognitive OS = SaaS/runtime próprio obrigatório`.

## 2.2 Skill como core portátil

A Skill deve conter:

- contratos;
- políticas;
- workflows;
- schemas;
- critérios de decisão;
- regras de roteamento;
- comportamento cognitivo.

Capabilities externas são materializadas por:

- recursos nativos do host;
- Skills adicionais;
- Apps/connectors;
- MCPs;
- APIs;
- CLIs;
- adapters;
- serviços remotos.

O core não deve depender de um vendor específico.

## 2.3 Roles/contracts são canônicos; agentes são otimização de execução

Hipótese:

> **Roles are canonical; agents are an execution optimization.**

Em hosts simples:

- a mesma LLM executa contratos/papéis sequencialmente.

Em hosts capazes:

- determinados papéis podem ser materializados como subagentes independentes.

Multiagente não deve ser requisito universal nem mecanismo de tolerância a falha.

## 2.4 Capability, não vendor

Princípio:

> **Cognitive OS requires capabilities, not vendors.**

Um provider de discovery não precisa ser o vendor oficial para ser útil.

Separar:

- **confiança no mecanismo de discovery**;
- **confiança no candidato descoberto**.

Um mecanismo aprovado não transfere confiança automaticamente para o Skill/MCP encontrado.

## 2.5 Inventory-first

Princípio atual desejado:

> **Reuse before install. Discover before recommend. Rank before install. Consent before change. Fallback after refusal.**

Antes de instalar qualquer coisa:

1. verificar o que já existe;
2. verificar se já satisfaz a capability;
3. usar capability nativa suficiente;
4. descobrir alternativas apenas quando houver gap material;
5. pedir consentimento antes de instalar/conectar algo novo.

---

# 3. Finding principal: fallback ainda está conceitualmente fraco

Hoje precisamos distinguir claramente três coisas.

## 3.1 Retry

Mesma ferramenta/executor, novamente.

Exemplo:

`Firecrawl -> timeout -> Firecrawl novamente`

Adequado apenas para falhas transitórias.

## 3.2 Executor substitution

Troca para **outro executor da mesma capability**.

Exemplo:

`WEB_SEARCH -> native search falhou -> Exa -> Tavily`

A promessa da capability continua essencialmente a mesma.

## 3.3 Capability degradation

Não existe mais executor equivalente adequado.

Exemplo:

`GROUNDED_CORPUS -> NotebookLM indisponível -> nenhum executor equivalente -> leitura manual de PDFs`

A tarefa ainda pode continuar, mas **com perda declarada de capability**.

## 3.4 Princípio proposto

> **Failure of an executor is not failure of the capability.**

A ordem ideal é:

`retry -> equivalent executor -> discovery -> equivalent executor descoberto -> capability degradation -> stop`

Nunca tratar automaticamente:

`executor falhou -> faça qualquer coisa parecida`

como fallback equivalente.

---

# 4. Nova peça arquitetural candidata

Investigar se o Cognitive OS deve possuir formalmente:

## Capability Contract

Define o que significa cumprir uma capability.

Exemplos:

- WEB_SEARCH;
- DEEP_RESEARCH;
- GROUNDED_CORPUS;
- STRUCTURED_CRAWL;
- REPOSITORY_RESEARCH;
- DATA_ANALYSIS;
- SECURITY_ANALYSIS;
- BROWSER_AUTOMATION;
- CAPABILITY_DISCOVERY.

## Executor Registry

Cada capability pode possuir múltiplos executores conhecidos.

Exemplo conceitual:

```text
WEB_SEARCH
├── host-native
├── Exa
├── Tavily
├── Brave
└── Firecrawl
```

O registry deve permitir metadata como:

- equivalence class;
- priority;
- installed;
- available;
- authenticated;
- security state;
- provenance;
- version/digest;
- cost;
- latency;
- last success;
- recent failure rate;
- user preference.

## Equivalence classes

Investigar um modelo como:

- **E0 — Contract Equivalent** — cumpre integralmente o contrato da capability.
- **E1 — Functionally Equivalent** — cumpre tudo que é material para este run, embora existam diferenças.
- **E2 — Degraded Substitute** — cumpre apenas parte do contrato.

A equivalência precisa ser provada por benchmark, não presumida.

## Failure Classifier

Possíveis classes:

- TRANSIENT;
- RATE_LIMIT;
- TIMEOUT;
- AUTH_REQUIRED;
- BAD_INPUT;
- PROVIDER_UNAVAILABLE;
- UNSUPPORTED;
- PARTIAL;
- EXECUTOR_SECURITY_BLOCK;
- CAPABILITY_SECURITY_BLOCK;
- USER_DECLINED.

A resposta do harness deve depender da classe de falha.

## Recovery Budget

O harness não deve tentar indefinidamente.

Investigar políticas por profundidade, por exemplo:

- FAST: primary + no máximo 1 retry transitório; sem discovery automático.
- NORMAL: até 2 executores equivalentes; 1 correção semântica quando necessária.
- DEEP: até 3 executores quando o ganho esperado justificar; discovery permitido.
- AUDIT: semelhante a DEEP; toda degradação/fallback registrada.

O orçamento deve controlar globalmente chamadas externas, troca de executor, retries, LLM turns, wall time e custo estimado, evitando retry multiplication.

---

# 5. Pesquisa Parte A — Sistemas científicos e motores de decisão

Esta é a **primeira prioridade**. Não começar pelas ferramentas.

Investigar profundamente os melhores modelos, sistemas e métodos atuais para construir um harness científico de investigação e decisão.

## 5.1 Hipóteses concorrentes

Avaliar se o Cognitive OS precisa de um **Hypothesis Engine** explícito e como sistemas científicos estruturam múltiplas hipóteses, evitam confirmation bias e escolhem evidência discriminante.

## 5.2 Information Gain / Next Best Evidence

Hipótese central: o Cognitive OS deve escolher **qual próxima evidência tem maior chance de mudar a decisão**.

Investigar Bayesian experimental design, active learning, value of information, expected information gain, sequential decision making, optimal stopping e active hypothesis testing.

## 5.3 Bayesian belief updating

Investigar representação de crenças, priors, evidências, atualização, confiança, posterior e materialidade da incerteza, evitando pseudo-precisão.

## 5.4 Causal inference

Investigar causal graphs/DAGs, confounders, correlation vs causation, interventions, counterfactuals, difference-in-differences, matching, interrupted time series, causal impact e randomized experiments.

Pergunta central: quando pesquisa observacional deixa de ser suficiente?

## 5.5 Experiment Design

Avaliar se `next proof` deve evoluir para capability explícita cobrindo hypothesis -> observable -> intervention -> control -> metric -> time window -> threshold -> kill criterion.

Investigar experiment design, sequential testing, A/B testing, sample size, stopping rules, falsification e reproducibility.

## 5.6 Counterfactual / Scenario Engine

Separar challenge/red team de scenario analysis e counterfactual reasoning. Investigar sensitivity analysis, stress testing, scenario planning, Monte Carlo, robust decision making, minimax regret e decision under deep uncertainty.

## 5.7 Reference classes / base rates

Investigar outside view, reference class forecasting, base-rate reasoning, planning fallacy e calibration. Verificar se o Outside View atual é operacional o suficiente.

## 5.8 Uncertainty calibration

Evoluir FACT / INFERENCE / UNKNOWN para considerar evidence strength, uncertainty, material uncertainty, sensitivity to uncertainty, confidence calibration e epistemic vs aleatory uncertainty.

## 5.9 Contradiction resolution

Investigar contrato explícito para resolver divergências por authority, freshness, directness, independence e reproducibility, buscando tie-break evidence e marcando `resolved | unresolved`.

## 5.10 Evidence weighting / source quality

Investigar autoridade, directness, freshness, independence, relevance, reproducibility, methodological quality e sample quality. Evitar contagem ingênua de fontes.

## 5.11 Assumption Registry

Avaliar registro estruturado de facts, assumptions, hypotheses, unknowns e dependencies. Pergunta-chave: qual assumption, se falsa, derruba a decisão?

## 5.12 Reversibility / Option Value

Investigar real options, option value, reversible vs irreversible decisions, information-buying decisions, lock-in e staged commitments.

## 5.13 Execution Readiness

Separar DECISION MADE de READY TO EXECUTE por dependencies, owners, permissions, resources, risks, rollback e success metric.

## 5.14 Scientific stop discipline

Investigar como decidir continuar pesquisando, experimentar, aceitar incerteza, parar, decidir ou adiar, conectando value of information, marginal information gain, custo, tempo, reversibilidade e risco.

---

# 6. Pesquisa Parte B — Harnesses, frameworks e ferramentas

Somente depois da Parte A.

## 6.1 Frameworks/harnesses a benchmarkear

Pesquisar, entre outros relevantes encontrados pelo próprio Cognitive OS:

- OpenAI Agents SDK;
- Anthropic agent/tooling patterns;
- PydanticAI;
- LangGraph;
- Temporal;
- Google ADK;
- AutoGen;
- LiteLLM;
- outros frameworks atuais realmente relevantes.

Avaliar retry, failure classification, executor substitution, fallback, circuit breaker, health checks, durable execution, state/checkpoints, human-in-the-loop, tool routing, multi-agent, lazy loading, cost controls, telemetry, security e deterministic control plane.

## 6.2 Executor candidates por capability

Não instalar nada. Criar candidate pools para avaliação.

- Web Search: host-native, Exa, Tavily, Brave, Firecrawl, outros atuais.
- Web Fetch / Structured Crawl: host-native, Firecrawl, Crawl4AI, outros.
- Browser / Dynamic Web: host-native, Playwright CLI, Playwright MCP, Browser Use, outros.
- Deep Research: host-native Deep Research, Exa Deep, Tavily Research, Firecrawl Deep Research, outros.
- Grounded Corpus: host-native, NotebookLM, Open Notebook, SurfSense, outros realmente comparáveis.
- Repository Research: git/ripgrep/local filesystem, GitHub native/plugin/MCP, outros.
- Data Analysis: native Code Interpreter, Python, DuckDB, Polars, warehouse-specific connectors, outros.
- Capability Discovery: local inventory, official MCP Registry, Vercel Skills/skills.sh, official vendor skill repos, GitHub/Web, outros providers.

---

# 7. Executor Equivalence Benchmark

Não afirmar equivalência apenas porque duas ferramentas “fazem busca”.

Para cada capability crítica, propor benchmark medindo task success, contract coverage, citation correctness, source quality, coverage/breadth, latency, token cost, financial cost, tool calls, failure rate, auth requirements, permission footprint, security surface e reproducibility.

Resultado esperado: `executor A -> E0`, `executor B -> E1`, `executor C -> E2`.

---

# 8. Lazy loading e custo

Responder quanto a arquitetura de múltiplos executores encarece o harness.

Investigar tool search, deferred loading, progressive disclosure, namespacing, dynamic tool materialization, cached tool definitions, lazy MCP activation e routing determinístico.

Princípio: **o registry pode conhecer muitos executores; a LLM não precisa enxergar todos**.

---

# 9. Deterministic control plane

Investigar até onde decisões operacionais podem ser determinísticas. `provider unavailable -> next ranked equivalent executor` não deveria exigir nova chamada à LLM.

Separar cognitive plane e control plane. Considerar determinísticos: retry, timeout, circuit breaker, health, ranking básico, budget, policy enforcement, security gate, telemetry schema e state transitions.

---

# 10. Segurança

Reavaliar prompt injection, indirect injection, tool poisoning, tool shadowing, line jumping, rug pull, dependency compromise, malicious Skills/MCPs, credential leakage, filesystem abuse, excessive agency e exfiltration.

Manter:

- Supply-chain Security Gate antes de instalar/conectar;
- Runtime Injection Gate antes de confiar em conteúdo externo/tool output;
- Consequential Action Gate antes de write/delete/send/install/privilege escalation.

Considerar immutable pins, digest/hash, frozen tool snapshots, revalidation on change, quarantine, provenance, allowlist e permission scope. Nunca alegar “prompt-injection proof”.

---

# 11. Telemetria / Capability Intelligence

Além de “o que foi usado”, considerar campos categóricos como capability_required, executor_selected, equivalence_class, already_installed, success/partial/failed/blocked, failure_class, retry_used, executor_switch, degradation_used, capability_gap, duration bucket, cost bucket e security warning category.

Nunca registrar prompt, resposta, arquivos, documentos, URLs privadas, credenciais, nomes de cliente, chain-of-thought ou texto livre sensível.

Investigar rare-cell suppression, minimum aggregation thresholds e privacy-safe capability intelligence.

---

# 12. Findings recentes que precisam ser incorporados

- **Reframing excessivo:** proteger contra problem drift.
- **Attribution error:** separar user requested, system selected e inferred.
- **Coverage bug:** investigar User Requirement Ledger com COMPLETE / PARTIAL / NOT_COVERED / BLOCKED.
- **Authority bias no discovery:** separar provider authority, provider trust, candidate trust e candidate approval.

---

# 13. Partial capability availability

Investigar se `AVAILABLE | UNAVAILABLE | UNKNOWN` precisa representar também capability parcialmente disponível/degradada, sem decidir o nome antes de analisar os schemas atuais.

---

# 14. O que NÃO fazer nesta rodada

- não alterar implementação produtiva;
- não alterar manifests;
- não mudar metadata de release;
- não instalar dependências sem consentimento;
- não promover executores;
- não transformar todos os papéis em agentes;
- não criar dezenas de tools no contexto;
- não assumir equivalência sem benchmark;
- não abrir nova arquitetura apenas por moda de framework;
- não usar LLM local para validação do Cognitive OS.

---

# 15. Preferência de uso de modelos

Quando o host permitir multi-agent:

- usar modelos menores/mais baratos para fan-out de pesquisa ampla;
- usar o modelo mais forte disponível para síntese, crítica e decisão;
- somente quando o ganho justificar custo.

Multi-agent não deve ser obrigatório.

---

# 16. Uso do Cognitive OS nesta própria pesquisa

Use **integralmente o Cognitive OS presente no repositório atual**. Não replique manualmente seus workflows neste brief.

O Cognitive OS deve escolher profundidade, workflows, capabilities, pesquisas, tools, Gauntlets, next proofs e stop criteria.

Se Deep Research nativo estiver disponível e agregar valor, use-o. Se não estiver, use fallback honesto e registre a limitação. Respeite consentimento para instalar/conectar capability nova.

---

# 17. Requisitos de observabilidade

Precisamos auditar depois:

`expected contract -> chosen capability -> chosen executor -> invocation -> result -> failure -> retry/switch/degradation -> conclusion`

Registrar sem chain-of-thought privado, no mínimo:

- User Requirement Ledger;
- Capability Ledger;
- Executor Ledger;
- Failure/Recovery Ledger;
- Evidence Ledger;
- Challenge Ledger;
- Gap Ledger;
- Cost/Research Budget;
- Mutation Ledger;
- Stop state.

Distinguir FACT, STRONG INFERENCE, HYPOTHESIS e UNKNOWN.

---

# 18. Entregáveis esperados

## A. Scientific Systems Benchmark
Quais etapas científicas faltam, quais já existem, quais são redundantes e quais realmente melhorariam decisão.

## B. Harness/Framework Benchmark
Separar conceito útil, implementação específica, vendor-specific e arquitetura generalizável.

## C. Capability/Executor Architecture
Propor Capability Contract, Executor Registry, equivalence classes, Failure Classifier, Recovery Budget, deterministic control plane, lazy loading e degradation rules.

## D. Scientific Core Gap Matrix

| Capability científica | Já existe? | Parcial? | Ausente? | Valor | Custo | Prioridade |
|---|---|---|---|---|---|---|

## E. Executor Candidate Matrix

| Executor | Equivalência estimada | Custo | Latência | Segurança | Auth | Observações |
|---|---:|---:|---:|---|---|---|

Não promover sem benchmark.

## F. Cost Model
Comparar arquitetura atual, arquitetura com equivalent executors, arquitetura com discovery e arquitetura multi-agent, estimando tokens, calls, wall time, cost e worst-case recovery.

## G. Security Impact
Mostrar o aumento de risco da nova arquitetura e mitigação.

## H. V1.5 vs V1.6+
Classificar em MUST BEFORE V1.5 CLOSE, SHOULD BEFORE V1.5 CLOSE, V1.6, FUTURE e DO NOT DO, evitando scope creep.

---

# 19. Perguntas finais

1. O core atual já se aproxima de um sistema científico real?
2. Quais capacidades científicas ainda faltam?
3. Qual delas traz maior ganho marginal?
4. Information Gain / Next Best Evidence deve virar mecanismo central?
5. Hypothesis Engine deve existir como capability explícita?
6. Como representar uncertainty sem pseudo-precisão?
7. Como decidir quando pesquisar, experimentar, agir ou parar?
8. Como distinguir retry, executor substitution e capability degradation?
9. Quantos executores equivalentes realmente precisamos por capability?
10. Quanto isso encarece o uso real do harness?
11. Que parte do routing pode ser determinística?
12. Que ferramentas atuais representam melhor cada capability?
13. Quais executores são realmente equivalentes?
14. Como medir essa equivalência?
15. Como evitar que o registry aumente contexto e custo?
16. Como detectar capability drift e rug pull?
17. Como aprender com telemetria sem comprometer privacidade?
18. O que é correção necessária da V1.5 e o que é claramente V1.6?
19. O Cognitive OS atual está sendo excessivamente prescritivo, ou ainda insuficientemente operacional?
20. Qual é o menor conjunto de mudanças que produz o maior salto de qualidade?

---

# 20. Critério de sucesso

A pesquisa será bem-sucedida se terminar com:

1. um **modelo científico melhor do pipeline cognitivo**;
2. um **modelo resiliente de execução por capability**;
3. um **mecanismo claro de custo/benefício**;
4. uma **separação forte entre executor failure e capability failure**;
5. uma **lista curta de mudanças de maior impacto**;
6. uma separação honesta entre V1.5 e evolução posterior.

O objetivo não é tornar o Cognitive OS maior.

O objetivo é torná-lo **mais científico, mais resiliente, mais econômico e mais honesto sobre seus limites**.

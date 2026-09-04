# SPEC V1.5 — Cognitive OS
## Capability Discovery, Grounded Research, Observability, Self-Improvement Governance e Portabilidade

**Status:** proposta consolidada, sanitizada e pronta para implementação pública  
**Base funcional:** Cognitive OS v1.4.x  
**Data:** 2026-09-04  
**Objetivo desta versão:** endurecer o comportamento real observado em múltiplos hosts sem transformar o Cognitive OS em runtime, agente executor ou plataforma própria; adicionar observabilidade e retorno voluntário de uso sem coletar o conteúdo privado das análises.

---

## 0. Resumo executivo

A V1.5 evolui o Cognitive OS em seis frentes:

1. **Capability Discovery 2.0** — distinguir capacidades já disponíveis, discovery local e discovery externo; tratar Find Skills e Find MCP como ativos concretos de discovery, não como verbos abstratos.
2. **Grounded Research 2.0** — usar Web para descoberta aberta e corpus/NotebookLM para cruzamento, preservação e investigação de evidências; controlar orçamento de pesquisa e evitar runaway.
3. **Grounded Strategic Analysis** — incorporar ao core princípios universais de análise estratégica baseada em evidência sem criar dependência da skill `analise-estrategica-grounded`.
4. **Self-Improvement Governance** — permitir hosts autoaperfeiçoáveis, como Hermes, sem contaminar silenciosamente o run ativo; validar patches e registrar mutações.
5. **Observable Run Telemetry** — criar um Flight Recorder nativo, privacy-preserving, com compartilhamento estritamente opt-in e bundle forense opcional.
6. **Host Portability & Resilience** — declarar capacidades abstratas e deixar adapters mapearem para Work, Hermes, Codex ou outros hosts; garantir fechamento mínimo mesmo quando tools/providers falharem.

A regra fundadora permanece:

> **Context before problem. Problem before solution. Evidence before confidence. Decision before execution.**

E ganha uma regra operacional complementar:

> **Discover before duplicating. Ground before concluding. Observe before claiming. Consent before changing.**

---

# 1. Base canônica e compatibilidade

## 1.1 Fonte de verdade

A implementação V1.5 deve partir do estado real mais recente do repositório público do Cognitive OS e preservar a arquitetura existente:

```text
skills/cognitive-os/SKILL.md
skills/cognitive-os/references/
skills/cognitive-os/policies/
skills/cognitive-os/schemas/
evals/
tests/
bootstrap/
tools/
docs/
```

O documento histórico `03_SPEC_V1_Implementacao.md` continua útil como origem arquitetural, mas a implementação observada da V1.4 prevalece quando houver divergência.

Ordem de autoridade:

```text
código + testes + estado runtime observado
> spec aprovada mais recente
> documentação canônica
> registros históricos
> conversa/memória
```

## 1.2 Compatibilidade

A V1.5 deve ser evolução compatível da V1.4. Durante desenvolvimento, manifests/version fields devem usar semântica coerente de prerelease (por exemplo `1.5.0-dev`) e ser sincronizados antes da promoção estável.

Não remover:

- fluxo adaptativo;
- separação decisão vs execução;
- source authority;
- Fast / Normal / Deep / Board360;
- Capability Discovery;
- Full Flow/Audit;
- instalação somente com consentimento;
- Decision Pack / New Evidence Pack / Result Pack;
- Capability Ledger;
- Evidence Ledger;
- stop / next proof;
- host-neutralidade;
- tratamento de tool output como não confiável.

Mudanças de schema devem ser aditivas quando possível.

---

# 2. Objetivos

A V1.5 deve permitir que qualquer host compatível:

1. contextualize antes de analisar;
2. formule a pergunta real;
3. separe fato, evidência, inferência, hipótese, preferência, desconhecido e contradição;
4. escolha profundidade proporcional a impacto, incerteza e reversibilidade;
5. determine qual fonte é autoridade para cada classe de fato;
6. descubra capacidades já disponíveis no host;
7. diferencie discovery local de discovery externo;
8. use Find Skills e Find MCP quando os discovery assets aprovados estiverem disponíveis e houver lacuna material;
9. nunca confunda discovery com autorização de instalação/conexão;
10. use Web para descoberta atual e Grounded Corpus/NotebookLM quando cruzamento e persistência de evidências trouxerem ganho;
11. controle orçamento de pesquisa antes de atingir guardrails externos;
12. preserve princípios de análise estratégica grounded no core;
13. registre capacidades usadas, falhas, fallbacks e side effects observáveis;
14. governe self-improvement sem alterar silenciosamente a metodologia do run;
15. produza telemetria local sanitizada sem conteúdo do usuário;
16. permita compartilhamento privacy-preserving somente após opt-in explícito;
17. feche o run com estado, evidência e próximo passo mesmo após falha secundária de provider/tool;
18. permaneça portátil entre Hermes, ChatGPT Work, Codex e hosts futuros.

---

# 3. Não objetivos

A V1.5 não deve:

- virar plataforma multiagente;
- substituir Hermes, NotebookLM, Memory Hub, Describe, GitHub ou Harness;
- criar runtime obrigatório;
- exigir um MCP Gateway dedicado;
- instalar automaticamente skills, MCPs, packages ou conectores encontrados;
- executar código de terceiros só porque apareceu em um registry;
- enviar logs ou telemetria sem opt-in;
- coletar prompts, documentos ou respostas para telemetria;
- persistir chain-of-thought;
- tornar NotebookLM obrigatório para qualquer pergunta;
- transformar toda pergunta em pesquisa profunda;
- criar skill separada para cada lente;
- depender de `analise-estrategica-grounded` para funcionar;
- bloquear hosts sem Find Skills/Find MCP externo;
- fingir que um mecanismo foi chamado quando o host não o expôs;
- permitir que self-improvement silencioso altere a metodologia ativa sem registro;
- iniciar engenharia antes de decisão aprovada.

---

# 3.1 Gate de estabilização herdado da V1.4

Antes de implementar novas capacidades V1.5 ou executar E2E account-bound, o branch deve corrigir/fechar findings públicos já observados na baseline V1.4:

1. **Consentimento E2E account-bound:** caminhos automáticos não podem selecionar NotebookLM ou outra capability ligada a conta sem consentimento explícito; o runner deve falhar fechado.
2. **Critical-case accounting:** nenhum caso crítico pode ser excluído do cálculo de sucesso global.
3. **Release evidence binding:** evidência comportamental usada para promoção deve estar ligada ao mesmo candidate SHA, versão, SUT/modelo, grader, manifests e artefatos da release. Evidência antiga não pode aprovar commit novo.
4. **Machine-verifiable contracts:** estados de disponibilidade/invocação, timestamps/IDs, referências de evidência e campos sensíveis devem ser validados por schema/código, não apenas por Markdown ou auto-relato do modelo.
5. **Grader hardening:** detectar truncamento, respostas excessivas quando o contrato exige concisão, falsa disponibilidade e IDs/timestamps inventados; preferir grader independente do SUT quando possível.
6. **Session/run binding:** E2E deve vincular evidência ao run/session criado para o caso, evitando selecionar sessão antiga/concorrente.
7. **Mutation detection:** ampliar detecção de efeitos persistentes relevantes além de uma única forma de escrita.
8. **Reprodutibilidade:** pinar dependências/ferramentas críticas quando possível e sincronizar VERSION, manifests e documentação.
9. **Model portability:** pelo menos dois SUT/model families devem ser testados quando o ambiente permitir; falha crítica em um target suportado impede alegação genérica de portabilidade.

Esses itens são **P0 de confiabilidade**, não features opcionais. Se um deles não puder ser fechado, a V1.5 deve declarar a limitação e não promover claims de production-grade correspondentes.

---

# 4. Arquitetura V1.5

```text
Usuário
  ↓
Cognitive OS
  ↓
Context / Grounding
  ↓
Question Framing
  ↓
Depth Router
  ↓
Source-of-Truth Map
  ↓
Capability Router
  ├── Existing capability
  ├── Local discovery
  ├── External discovery
  └── Manual fallback
  ↓
Research Router
  ├── Web discovery
  ├── Structured web/crawl
  ├── Grounded corpus / NotebookLM
  └── Quantitative analysis
  ↓
Cognitive Methods / Strategic Grounding
  ↓
Challenge
  ↓
Stop / Next Proof
  ↓
Recommendation
  ↓
Decision
  ↓
Decision Pack
  ↓
Harness / executor
```

Camadas transversais:

```text
Observability / Flight Recorder
Consent & Installation Policy
Self-Improvement Governance
Provider / Host Resilience
Privacy / Diagnostic Sharing
```

---

# 5. Fluxo cognitivo 0–10

A V1.4 possuía fluxo adaptativo. A V1.5 formaliza uma etapa adicional de observabilidade sem transformar o fluxo em ritual visível.

## 0. Contextualizar

Reconstruir:

- projeto;
- objetivo;
- estado;
- decisões anteriores;
- restrições;
- fora de escopo;
- sistemas vizinhos;
- fontes de verdade;
- capabilities já conhecidas;
- preferências de pesquisa do perfil.

## 1. Formular a pergunta real

Não aceitar automaticamente a solução pedida como sendo o problema.

## 2. Ancorar na realidade

Separar:

- FACT;
- EVIDENCE;
- INFERENCE;
- HYPOTHESIS;
- PREFERENCE;
- UNKNOWN;
- CONTRADICTION.

## 3. Definir profundidade

- FAST;
- NORMAL;
- DEEP;
- BOARD360;
- FULL_FLOW_AUDIT quando explicitamente pedido ou exigido por política.

## 4. Mapear fontes de verdade

Antes de cruzar sistemas diferentes, declarar qual fonte é autoridade para qual classe de fato.

Exemplo:

```text
Stripe / Shopify → verdade transacional
GA4 → comportamento / atribuição
CRM → pipeline comercial
ticketing → suporte
repo/testes → comportamento de software
documento aprovado → decisão canônica
```

Conflitos devem permanecer visíveis.

## 5. Resolver capabilities

Executar Capability Discovery 2.0 apenas quando uma capacidade puder reduzir incerteza material.

## 6. Escolher estratégia de pesquisa

Decidir entre:

- Web;
- structured crawl;
- Grounded Corpus / NotebookLM;
- quantitative analysis;
- internal docs;
- repo;
- connectors/MCPs;
- combinação sequenciada.

## 7. Aplicar métodos

Usar apenas lentes/métodos que mudem materialmente compreensão ou decisão.

## 8. Comparar e desafiar

- alternatives;
- tradeoffs;
- red team;
- premortem;
- second-order effects;
- kill criteria;
- contradiction checks.

## 9. Stop / Next Proof

Parar quando pesquisa adicional tiver valor marginal inferior a um experimento, observação ou teste.

## 10. Fechar e registrar

Produzir:

- recomendação humana;
- decision state;
- next proof;
- stop reason;
- run state;
- registros observáveis compatíveis com a profundidade.

O fluxo não precisa ser mostrado ao usuário em tarefas simples.

---

# 6. Capability Discovery 2.0

## 6.1 Princípio

Capability Discovery existe para evitar:

- reinventar procedimento;
- construir integração que já existe;
- pedir trabalho manual desnecessário;
- assumir que o host não possui capacidade;
- instalar tooling desnecessariamente.

Mas discovery só deve ocorrer quando houver uma **capability gap material**.

## 6.2 Quatro classes de discovery

### A. Existing Capability

Capacidade já carregada ou conhecida no runtime.

Exemplos:

- Web;
- Files/Drive;
- GitHub;
- NotebookLM;
- análise de dados;
- connector já autenticado.

### B. Local Skill Discovery

Enumerar/inspecionar skills já instaladas/expostas no host.

Exemplo observado em Work:

```text
necessidade de diagnóstico de métricas
→ listar habilidades disponíveis
→ selecionar skill especializada já exposta
```

### C. Local Tool / Connector / MCP Discovery

Enumerar ferramentas, conectores e MCPs já registrados no host.

### D. External Discovery

Usar discovery assets aprovados para procurar novas capacidades fora do runtime atual.

Subtipos:

- `EXTERNAL_SKILL_DISCOVERY`
- `EXTERNAL_MCP_DISCOVERY`

---

# 7. Find Skills e Find MCP como discovery assets concretos

## 7.1 Definição

Find Skills e Find MCP não devem ser tratados somente como comandos semânticos.

São **discovery assets concretos** — skills, repositórios, CLIs ou mecanismos aprovados que sabem consultar ecossistemas de skills/MCPs.

A spec não deve hardcodar um único fornecedor. O registry interno deve manter quais discovery assets estão aprovados por host.

## 7.2 Bootstrap

Em hosts controlados pelo projeto, discovery assets aprovados podem ser preparados uma única vez, **mas o bootstrap/preflight determinístico deve permanecer side-effect-free**. A instalação/configuração persistente deve ocorrer em uma etapa separada e explicitamente autorizada.

Exemplo:

```text
bootstrap/preflight host (read-only)
→ detectar necessidade e plano
→ mostrar provenance/version/permissões
→ consentimento explícito
→ apply/install em etapa separada
→ validar
→ registrar provenance/hash/version
→ tornar disponível ao Cognitive OS
```

Não reinstalar a cada análise. Não transformar o preflight em instalador implícito.

## 7.3 Discovery asset ≠ capability candidata

Distinguir:

```text
Find Skills / Find MCP
= infraestrutura de busca

skill/MCP encontrado
= candidato
```

A infraestrutura de busca pode ser pré-aprovada.

O candidato encontrado não é automaticamente confiável.

## 7.4 Pipeline obrigatório

```text
Capability gap
↓
Existing capability?
↓ não
Local skill/tool/connector discovery
↓ insuficiente
External discovery asset disponível?
↓ sim
Find Skills ou Find MCP
↓
Candidate shortlist
↓
Provenance inspection
↓
Gauntlet
↓
Candidate execution needed?
↓
Trust/permission policy + Gauntlet
↓
If account-bound, sensitive, or persistent → explicit consent
↓
Ephemeral test/use OR persistent install/connect
```

**Ephemeral is not automatically safe.** Executar código, skill ou MCP externo sem instalação persistente continua sendo execução de capability não confiável e deve respeitar provenance, permissões, sandbox/least privilege e consentimento quando houver acesso a conta, rede, arquivos sensíveis ou efeitos externos.

Se external discovery estiver indisponível:

```text
availability = UNAVAILABLE
invocation = NOT_CALLED
fallback = local/manual path
```

Nunca fingir execução.

---

# 8. Discovery routing

## 8.1 Procedimento / conhecimento operacional

Preferir:

```text
installed skill
→ Local Skill Discovery
→ External Skill Discovery
```

## 8.2 Conectividade com sistema, banco, SaaS ou dado

Preferir:

```text
existing connector/MCP
→ Local Tool/MCP Discovery
→ External MCP Discovery
```

## 8.3 Forma de automação ambígua

Automation Recommender ou equivalente pode ser consultado, mas não é etapa obrigatória.

## 8.4 Pergunta ao usuário

Antes de pedir upload/exportação manual, verificar capacidades disponíveis quando isso for proporcional e seguro.

Exceção: se a própria verificação exigir acesso sensível não autorizado.

---

# 9. Proveniência e Gauntlet de capability

Todo candidato externo deve registrar, quando disponível:

- source registry;
- repository;
- maintainer;
- version/tag/commit;
- license;
- last update;
- popularity/maturity signal;
- requested permissions;
- network access;
- filesystem access;
- credential requirements;
- persistence;
- dependencies;
- supply-chain risk;
- overlap with existing capabilities;
- portability;
- reversibility.

Estados possíveis:

```text
DISCOVERED
INSPECTED
REJECTED
TEST_APPROVED
PERSISTENT_ADOPTION_PENDING_CONSENT
APPROVED
QUARANTINED
UNAVAILABLE
```

Discovery não autoriza execução de código desconhecido.

---

# 10. Consentimento e instalação

## 10.1 Regra

Consentimento deve ser exigido para qualquer ação persistente ou sensível, incluindo:

- instalar skill;
- instalar package;
- instalar MCP;
- conectar conta;
- autenticar serviço;
- gravar configuração persistente;
- conceder permissões;
- ativar escrita externa.

## 10.2 Sem consentimento implícito

O usuário pedir “analise meus dados do Stripe” não equivale a:

- instalar um Stripe MCP;
- autenticar a conta;
- salvar credenciais;
- conceder escrita.

## 10.3 Preview

Antes de instalação/conexão, informar de forma curta:

- o que foi encontrado;
- por que ajuda;
- o que será instalado/conectado;
- permissões;
- persistência;
- risco relevante;
- como reverter.

---

# 11. Grounded Research 2.0

## 11.1 Web e NotebookLM têm papéis diferentes

### Web

Melhor para:

- descoberta aberta;
- atualidade;
- novos concorrentes;
- regulamentação;
- notícias;
- sinais externos.

### Grounded Corpus / NotebookLM

Melhor para:

- cruzar múltiplas fontes;
- preservar corpus de investigação;
- voltar às evidências;
- procurar contradições;
- comparar documentos repetidamente;
- manter investigação longa entre runs;
- reduzir reenvio de contexto;
- produzir grounded synthesis.

## 11.2 Regra nova

Não limitar Grounded Corpus a “corpus grande”.

Considerar corpus quando o valor depender de:

- cruzamento;
- preservação;
- revisitação;
- auditoria;
- múltiplas fontes internas + externas;
- perguntas repetidas sobre o mesmo conjunto de evidências.

## 11.3 Padrão recomendado para Deep/Board360/Full Flow

```text
internal grounding
→ open-web discovery
→ source curation
→ grounded corpus
→ structured corpus questions
→ synthesis
→ challenge
→ decision / next proof
```

O corpus não substitui pesquisa atual. **Considerar NotebookLM/Grounded Corpus não autoriza acesso a uma conta.** Se a capability for account-bound, disponibilidade técnica, autenticação e consentimento do run devem ser tratados separadamente antes de qualquer leitura.

## 11.4 Preferência de perfil

O core público deve manter NotebookLM como capability opcional.

Um deployment profile pode permitir:

```yaml
research_preferences:
  grounded_corpus:
    mode: prefer
    deep_analysis: strongly_consider
    full_flow_audit: strongly_consider
```

Se indisponível, fallback explícito.

---

# 12. Web → Corpus migration triggers

O Research Router deve reconsiderar a estratégia quando qualquer condição ocorrer:

- múltiplas fontes materiais precisam ser cruzadas;
- fontes internas e externas estão sendo combinadas;
- o agente repete perguntas sobre fontes já encontradas;
- o número de fontes começa a pressionar o contexto;
- compaction se aproxima ou ocorre;
- a análise precisa continuar em runs futuros;
- a rastreabilidade de claims está ficando difícil;
- a pesquisa aberta já encontrou o universo relevante e a pergunta virou síntese.

Heurística não normativa:

- checkpoint após cerca de 10–15 fontes materiais;
- checkpoint quando o contexto usado passar de aproximadamente 40–50%, **somente se essa métrica for observável no host**;
- obrigatoriamente reconsiderar após qualquer compaction observável.

Quando o host não expuser uso de contexto, usar proxies observáveis como número de fontes materiais, repetição de consultas, tamanho do corpus temporário e eventos de truncamento/compaction. Esses números são soft defaults, configuráveis por host.

---

# 13. Research Budget Controller

## 13.1 Objetivo

Evitar:

- runaway de web search;
- limite de host;
- contexto inflado;
- interrupção sem síntese;
- repetição de consultas de baixo valor.

## 13.2 Planejamento

Antes de pesquisa profunda:

```text
research question
→ subquestions
→ source classes
→ expected evidence
→ budget
→ stop condition
```

## 13.3 Budget contract

O budget deve ser representável por counters observáveis, nunca por números inventados. O host pode suportar uma ou mais dimensões:

```yaml
budget_units:
  web_calls: {soft_limit: null, hard_limit: null}
  source_count: {soft_limit: null, hard_limit: null}
  elapsed_seconds: {soft_limit: null, hard_limit: null}
  context_fraction: {soft_limit: null, hard_limit: null, observable: false}
```

Campos não observáveis permanecem `UNKNOWN`/`null`. O `cognitive-run-record` deve registrar budget planejado, consumido e motivo de stop/fallback.

## 13.4 Checkpoints

Reavaliar o valor marginal em:

- ~50% do budget;
- ~80% do budget;
- antes de atingir limite externo conhecido.

Reservar capacidade para:

- verificação;
- challenge;
- fechamento.

## 13.5 Guardrail externo

Se um host bloquear novas buscas:

**não encerrar automaticamente o run.**

Executar:

```text
freeze new search
→ synthesize existing evidence
→ mark RATE_LIMITED/BLOCKED
→ identify material gap
→ next proof/fallback
→ close
```

---

# 14. Grounded Strategic Analysis no core

A V1.5 absorve princípios universais úteis de análise estratégica grounded.

## 14.1 Regras obrigatórias

- fonte antes da interpretação;
- fato ≠ hipótese ≠ recomendação;
- decisão ≠ proposta ≠ backlog;
- mecanismo ≠ valor;
- produto ≠ operação ≠ infraestrutura;
- capability existente não é automaticamente oportunidade de mercado;
- estado atual observado vence documento histórico quando a classe de fato assim exigir;
- posicionamento exige: público, problema, resultado;
- diferencial técnico sem job-to-be-done não basta;
- nova oportunidade deve ser testada contra o portfólio existente para evitar “reembalagem”.

## 14.2 Companion skill

`analise-estrategica-grounded` pode continuar como companion skill quando disponível.

Ela não é dependência obrigatória.

```text
core principles = sempre presentes
companion skill = aprofundamento opcional
```

## 14.3 related_skills ≠ discovery

`related_skills` é dica de composição conhecida.

Não substitui:

- Local Skill Discovery;
- External Skill Discovery.

---

# 15. Source-of-Truth Reconciliation

Antes de cruzar sistemas, produzir internamente um mapa:

| Classe de fato | Fonte preferida | Fonte secundária | Risco de divergência |
|---|---|---|---|
| transação financeira | ledger/payment system | commerce platform | refund timing |
| comportamento web | analytics | commerce events | tracking gaps |
| pipeline comercial | CRM | billing | stage hygiene |
| código | repo/testes | docs | branch drift |
| decisão | decision record/spec | conversation | stale memory |

Quando duas fontes medirem conceitos diferentes, não compará-las como equivalentes.

Se reconciliação for necessária, fazê-la antes de causalidade.

---

# 16. Self-Improvement Governance

## 16.1 Premissa

Hosts como Hermes podem autoaperfeiçoar skills como comportamento normal.

A V1.5 não deve proibir self-improvement. Deve governá-lo **até o limite que o host expuser**. O core textual não pode prometer controle de mutações externas que o host não permita interceptar; nesses casos deve detectar/registrar a limitação e o adapter/harness específico é responsável pela enforcement.

## 16.2 Run-Scoped Methodology Pinning

No início de Deep/Board360/Full Flow:

registrar:

- skill version/hash;
- relevant reference hashes;
- policies/schema versions.

A metodologia do run fica logicamente pinada.

## 16.3 Regra preferida

```text
improvement detected
→ stage patch
→ validate patch
→ finish current run with pinned methodology
→ activate improvement after run
```

## 16.4 Mutação durante o run

Se o host aplicar mudança imediatamente:

- registrar `METHODOLOGY_DRIFT=DETECTED`;
- não fingir continuidade perfeita;
- se possível continuar usando snapshot original;
- se impossível, `EXECUTION_INTEGRITY=PARTIAL`;
- registrar quais etapas ocorreram antes/depois da mutação.

## 16.5 Validation Gate

Antes de ativar patch:

- referenced files exist;
- referenced sections exist;
- schema links resolve;
- no missing dependency created;
- frontmatter/format valid;
- skill can load;
- policy conflicts checked;
- tests/validator pass when available.

Referência quebrada bloqueia promoção.

---

# 17. Mutation Ledger

Full Flow/Audit deve registrar mutações persistentes relevantes.

Campos mínimos:

```yaml
mutation_id:
type:
target:
before_version_or_hash:
after_version_or_hash:
trigger:
applied_at:
applied_during_active_run:
validation:
affected_phases:
rollback_available:
status:
```

Tipos:

- SKILL_MUTATED;
- REFERENCE_MUTATED;
- POLICY_MUTATED;
- CONFIG_CHANGED;
- PACKAGE_INSTALLED;
- MCP_INSTALLED;
- CONNECTION_CREATED;
- FILE_CREATED;
- FILE_MODIFIED;
- OTHER_PERSISTENT_SIDE_EFFECT.

---

# 18. Persistent Side Effects Ledger

Separar explicitamente:

```text
INSTALLATION_OCCURRED
CONFIGURATION_CHANGED
SKILL_MUTATED
FILE_CREATED
FILE_MODIFIED
EXTERNAL_CONNECTION_CREATED
CREDENTIAL_STATE_CHANGED
```

“Nothing installed” não pode significar “nothing changed”.

Full Flow/Audit deve listar side effects materiais.

---

# 19. Observable Run Telemetry — Flight Recorder

## 19.1 Objetivo

O Cognitive OS deve conseguir responder:

> Como este run foi executado?

sem precisar extrair o log bruto inteiro do host.

## 19.2 Construção por allowlist

O Flight Recorder deve ser **construct-by-allowlist**: registrar somente campos tipados explicitamente permitidos. Não capturar conteúdo livre para depois tentar redigir. Sanitização é defesa em profundidade, não a barreira principal.

Em hosts sem filesystem/artifact persistence, o trace pode existir apenas em memória ou em artefato host-managed. Se nem isso for possível, `LOCAL_DIAGNOSTICS=UNAVAILABLE`; a skill continua funcionando.

## 19.3 O que registrar

Exemplos:

```yaml
cognitive_os_version:
host:
surface:
run_id:
depth:
full_flow_audit:
phase_states:
capabilities_checked:
local_skill_discovery:
local_tool_discovery:
external_skill_discovery:
external_mcp_discovery:
skills_loaded:
candidate_capabilities:
web_search_count:
web_failures:
web_rate_limits:
grounded_corpus:
notebooklm:
context_compaction:
fallbacks:
mutations:
persistent_side_effects:
provider_failures:
decision_state:
run_status:
stop_reason:
```

## 19.4 O que NÃO registrar por padrão

- prompt;
- resposta completa;
- documentos;
- conteúdo de arquivos;
- nomes de cliente;
- e-mails;
- PII;
- secrets;
- tokens;
- cookies;
- query text detalhado;
- URLs privadas;
- chain-of-thought;
- reasoning traces.

A telemetria mede o sistema, não o assunto do usuário.

---

# 20. Telemetry privacy modes

## OFF — default público

Nenhum compartilhamento.

Pode haver apenas estado efêmero necessário ao run.

## LOCAL_DIAGNOSTICS

Persistir trace sanitizado localmente.

Sugestão de path quando filesystem existir:

```text
~/.cognitive-os/logs/<run_id>/usage-trace.json
```

ou path host-managed equivalente.

## SHARE_PRIVACY_PRESERVING_DIAGNOSTICS

Somente após consentimento explícito. Não usar a palavra “anônimo” na interface pública a menos que a implementação de transporte realmente garanta anonimato; o contrato padrão é privacy-preserving.

Antes do envio:

1. gerar payload;
2. sanitizar localmente;
3. mostrar preview;
4. pedir aprovação;
5. enviar pelo adapter selecionado.

---

# 20.1 Telemetry onboarding

Para que usuários externos possam contribuir sem dark pattern:

- default continua `OFF`;
- hosts com capacidade de interação podem oferecer **uma única vez** a opção de `LOCAL_DIAGNOSTICS` ou `SHARE_PRIVACY_PRESERVING_DIAGNOSTICS`, preferencialmente após instalação ou primeiro run elegível;
- recusa não deve ser repetidamente solicitada;
- ausência de UI/consent surface mantém `OFF`;
- habilitar telemetria nunca pode ser condição para usar a skill.

---

# 21. Sharing adapters

O core não deve depender de GitHub ou endpoint próprio.

Adapters permitidos:

- export local file;
- explicit upload;
- GitHub issue/discussion sanitizada;
- projeto/repositório configurado pelo usuário;
- endpoint privado configurado, quando o deployment de telemetria estiver habilitado.

Nenhum adapter pode ativar upload automaticamente.

## 21.1 Telemetry Collector privado

A V1.5 pública deve incluir o **cliente, schema, sanitizador, consentimento e testes**. O destino de telemetria deve ser uma infraestrutura separada e privada.

Arquitetura:

```text
PUBLIC — cognitive-os
├── Flight Recorder
├── cognitive-usage-trace schema
├── local sanitizer
├── consent + preview
├── sender interface
└── conformance/privacy tests

PRIVATE — telemetry collector
├── ingest API
├── server-side schema validation
├── second-pass sanitizer
├── privacy-preserving event store
├── aggregate metrics
├── retention/deletion controls
└── internal dashboard
```

O repositório público **não** deve conter dados recebidos de usuários.

## 21.2 Configuração pública do endpoint

O endpoint não é segredo. Para permitir uso real sem hardcode no código, releases podem distribuir um arquivo/configuração versionada e auditável, por exemplo `telemetry-defaults.json`, contendo apenas endpoint HTTPS, schema version e URL da policy. Deployments podem sobrescrever ou desabilitar essa configuração. Se nenhum endpoint válido estiver configurado, sharing fica `UNAVAILABLE`.

## 21.3 Contrato mínimo do collector

O collector deve tratar todo evento como **input não confiável e potencialmente forjado**. Telemetria comunitária serve para melhoria de produto, não como prova de segurança, conformidade ou execução real individual.

Endpoint lógico sugerido:

```text
POST /v1/telemetry/events
```

O nome/host real do endpoint é configuração de deployment e não deve ser hardcoded no core.

Requisitos obrigatórios:

- aceitar somente schema allowlisted e versionado;
- rejeitar campos desconhecidos por default;
- rejeitar free text onde não for estritamente necessário;
- limitar tamanho do payload;
- proteção de replay/idempotência por `event_id` efêmero;
- rate limiting/anti-abuse na borda com metadados processados de forma transitória quando necessário, sem adicioná-los ao event store controlado pela aplicação;
- não persistir request body inválido;
- aplicar sanitização novamente no servidor;
- a aplicação e a infraestrutura sob controle do projeto não devem persistir IP; metadados inevitáveis de proxy/CDN/provedor devem ser documentados e minimizados;
- não persistir User-Agent completo;
- não criar fingerprint;
- não usar cookies de tracking;
- não gerar identificador persistente de instalação por default;
- `run_id` deve ser aleatório, não reversível e não carregar identidade;
- não aceitar prompt, response, document content, file content, secrets ou chain-of-thought;
- se oferecer exclusão individual, retornar um `receipt_id`/deletion token não identificável que o cliente possa guardar localmente; não exigir conta para solicitar exclusão do evento correspondente;
- separar eventos detalhados de agregados;
- suprimir células/coortes pequenas nos agregados (default recomendado: `k >= 10`) e evitar dimensões de alta cardinalidade;
- definir retenção limitada para eventos detalhados.

Default recomendado para V1.5:

```text
detailed sanitized event retention: 30 days
aggregate metrics: 12 months
raw conversation retention: 0
IP retention: 0
free-text research content retention: 0
```

Esses valores devem ser documentados e configuráveis no backend, mas qualquer aumento de retenção exige revisão explícita de privacidade.

## 21.4 Payload público permitido

Exemplo de evento permitido:

```yaml
schema_version: 1
cognitive_os_version: 1.5.0
host_family: chatgpt-work
surface_class: work-mobile
depth: deep
full_flow_audit: false
run_status: partial
decision_state: more_evidence_required
capability_events:
  local_skill_discovery: success
  local_connector_discovery: success
  external_skill_discovery: unavailable
  external_mcp_discovery: unavailable
research:
  web_calls_bucket: 0
  grounded_corpus: not_called
  compaction_occurred: false
failures:
  rate_limited: false
  provider_failure: false
side_effects:
  persistent_change: false
feedback:
  helpfulness: null
```

Preferir **buckets/classes** em vez de números ou strings de alta cardinalidade sempre que possível. Não enviar timestamp preciso por default; quando tempo for necessário para métricas, preferir bucket diário/semanal derivado no servidor.

O payload compartilhável deve ser uma **projeção mais restrita** que o trace local:

- IDs de capabilities/skills só podem ser enviados quando pertencem a uma allowlist pública conhecida;
- nomes de skills/MCPs customizados, repositórios privados, paths e URLs viram categoria/bucket (`custom_skill`, `custom_mcp`, `other`) em vez do nome real;
- ordem de execução pode ser representada por fase/ordinal, não por timestamp preciso;
- provenance detalhada permanece local/forense, salvo consentimento específico em um bundle diagnóstico.

## 21.5 Feedback humano opcional

Após um run concluído, hosts que suportarem UI podem oferecer, sem interromper o usuário:

```text
Esta análise ajudou você a decidir?
[Sim] [Parcialmente] [Não]
```

Opcionalmente, categorias fechadas:

- faltou evidência;
- faltou profundidade;
- capability inadequada/indisponível;
- contexto insuficiente;
- resposta pouco clara;
- outro — **sem campo livre na V1.5**.

O feedback deve ser um evento separado e continuar sujeito ao mesmo consentimento.

## 21.6 Consent lifecycle

Consentimento para telemetria deve ser:

- explícito;
- revogável;
- separado de consentimento de instalação/MCP;
- nunca pré-marcado;
- armazenado localmente pelo host quando possível;
- versionado contra a policy aceita.

Estados:

```text
NOT_ASKED
DECLINED
LOCAL_ONLY
SHARE_APPROVED
REVOKED
```

Antes do primeiro envio, mostrar preview do payload real. Mudança material no schema/policy exige novo consentimento.

A distribuição que habilitar sharing deve publicar uma notice de privacidade legível por humanos com: finalidade, categorias de dados, retenção, operadores/subprocessadores de infraestrutura relevantes, forma de revogação, exclusão quando oferecida e canal de contato. A spec não deve alegar conformidade legal automática apenas por implementar estes controles.

## 21.7 Fallback sem backend

Se não houver collector configurado:

- o Cognitive OS continua funcionando;
- `SHARE_PRIVACY_PRESERVING_DIAGNOSTICS` fica `UNAVAILABLE`;
- o usuário pode exportar o trace localmente;
- nenhuma execução deve falhar por ausência da telemetria.

---

# 22. Forensic Diagnostic Bundle

## 22.1 Quando usar

Quando um run:

- falhar;
- divergir do esperado;
- sofrer rate limit;
- aparentar capability não chamada;
- sofrer mutação;
- terminar sem resposta;
- apresentar provider error.

## 22.2 Escopo

Nunca “varrer a máquina toda”.

Limitar por:

```text
run_id
+ temporal window
+ allowlisted log sources
+ known session/task ids
```

## 22.3 Processo

```text
collect locally
→ sanitize locally
→ remove free-text/user content where possible
→ create manifest
→ preview
→ explicit consent
→ share
```

## 22.4 Conteúdo

Pode incluir:

- tool name;
- call state;
- timestamps;
- status;
- provider/model;
- host capability availability;
- retry/fallback;
- sanitized error class;
- side effects;
- hashes/versions;
- counts.

Não incluir raw conversation por default.

---

# 23. Full Flow/Audit V1.5

Além dos ledgers existentes, Full Flow/Audit deve contabilizar:

- Phase Ledger;
- Conditional Branch Ledger;
- Capability Ledger;
- Method Ledger;
- Evidence Ledger;
- Gap/Failure Ledger;
- Challenge Ledger;
- Mutation Ledger;
- Persistent Side Effects Ledger;
- Research Budget Summary;
- Provider/Host Failure Summary;
- Stop;
- Next Proof.

Não persistir chain-of-thought.

## 23.1 Capability Ledger — campos novos

```yaml
capability:
category:
need:
discovery_class:
availability:
auth_state:
run_consent_state:
invocation:
result:
source_or_adapter:
candidate_provenance:
consent_required:
consent_state:
fallback:
materiality:
```

## 23.2 Estados padronizados

Availability:

- AVAILABLE
- UNAVAILABLE
- UNKNOWN

Invocation:

- CALLED
- NOT_CALLED

Result:

- SUCCESS
- PARTIAL
- TRUNCATED
- RATE_LIMITED
- BLOCKED
- FAILED
- UNAVAILABLE
- NOT_APPLICABLE

Auth state:

- NOT_REQUIRED
- REQUIRED_NOT_AUTHENTICATED
- AUTHENTICATED
- UNKNOWN

Run consent state:

- NOT_REQUIRED
- NOT_ASKED
- DECLINED
- GRANTED

`AVAILABLE + AUTHENTICATED` nunca equivale automaticamente a `GRANTED` para aquele run.

---

# 24. State semantics

Separar quatro eixos:

## FLOW_COVERAGE

A estrutura cognitiva relevante foi considerada?

- COMPLETE
- PARTIAL
- BLOCKED

## EXECUTION_INTEGRITY

As capabilities/métodos executaram conforme o contrato?

- COMPLETE
- PARTIAL
- FAILED

## RUN_STATUS

O run terminou operacionalmente?

- COMPLETE
- PARTIAL
- FAILED

## DECISION_STATE

Qual o estado da decisão?

- READY_TO_DECIDE
- DECIDED
- TEST_REQUIRED
- MORE_EVIDENCE_REQUIRED
- BLOCKED
- NO_ACTION_RECOMMENDED

`TEST_REQUIRED` não é falha.

---

# 25. Provider / Model Failure Resilience

Esta seção define contrato de host/adapter; não autoriza criar um novo runtime de providers dentro do core. Implementar enforcement apenas onde o host expuser metadata/controles suficientes e registrar `UNAVAILABLE` onde não expuser.

## 25.1 Capability compatibility

Host adapters devem validar, quando possível:

- model availability;
- reasoning effort values;
- context limits;
- tool support;
- structured-output support.

Não enviar parâmetro conhecido como incompatível.

## 25.2 Degradação

Quando effort/configuração não for suportado:

```text
requested setting
→ nearest supported safe setting
→ record fallback
→ continue
```

Se isso puder alterar materialmente qualidade, tornar visível.

## 25.3 Closing Guarantee

Um erro secundário no final não deve apagar 20 minutos de trabalho.

Se houver estado local suficiente:

```text
provider failure
→ fallback provider/model if authorized
→ reconstruct observable closure from run state
→ emit minimal close
```

Fechamento mínimo:

- status;
- o que foi concluído;
- o que falhou;
- evidência disponível;
- próximo passo.

---

# 26. No-Ritual Clarification

Manter e reforçar:

- se a pergunta já está suficientemente definida, prosseguir;
- perguntar apenas quando uma lacuna realmente mudar o plano;
- antes de perguntar por arquivo manual, verificar capability disponível quando razoável;
- não fazer entrevista de discovery só porque existe uma skill de entrevista.

---

# 27. Evidence discipline

Nunca inventar:

- causa raiz;
- ranking;
- TAM;
- CAC;
- forecast;
- WTP;
- impacto;
- cobertura;
- tool invocation;
- connector availability.

Quando dados faltarem:

```text
UNKNOWN
TEST_REQUIRED
MORE_EVIDENCE_REQUIRED
```

são respostas válidas.

---

# 28. Host Adapter Contract

O core deve expressar capability abstrata.

O host adapter resolve a implementação.

## 28.1 Abstrações mínimas

```text
ListInstalledSkills
InspectSkill
ListLocalTools
ListLocalConnectors
DiscoverExternalSkill
DiscoverExternalMCP
SearchWeb
ReadFiles
AccessRepo
UseGroundedCorpus
AnalyzeData
PersistAuditArtifact
ReadRunDiagnostics
PersistUsageTrace
PreviewUsageTrace
RequestTelemetryConsent
SendUsageTrace
```

As quatro capabilities de telemetria são opcionais e host-dependent. A skill não pode prometer envio automático em hosts que não exponham persistência/UI/outbound action adequada; nesses hosts, sharing fica `UNAVAILABLE` ou usa export manual explicitamente aprovado.

## 28.2 Hermes

Pode mapear para:

- skills_list / skill_view;
- MCP inventory;
- approved discovery assets;
- NotebookLM bridge/MCP;
- filesystem;
- run/session logs;
- self-improvement mechanism.

## 28.3 ChatGPT Work

Pode mapear para:

- installed skill enumeration;
- connected apps/connectors;
- Work/Cloud Browser;
- Drive/files;
- available skills/tools exposed in-session.

Se external discovery não estiver exposto:

```text
EXTERNAL_*_DISCOVERY = UNAVAILABLE
```

## 28.4 Codex / Claude / outros

Adapter específico, sem mudar regra cognitiva central.

---

# 29. Host Matrix V1.5

A documentação de host deve registrar por capability:

| Capability | Hermes | Work | Codex | Outros |
|---|---|---|---|---|
| installed skill discovery | required observation | required observation | adapter | adapter |
| local MCP/tool discovery | adapter | connector inventory | adapter | adapter |
| external skill discovery | optional discovery asset | host-dependent | adapter | adapter |
| external MCP discovery | optional discovery asset | host-dependent | adapter | adapter |
| NotebookLM | bridge/MCP | connector/tool if exposed | adapter | adapter |
| raw forensic logs | allowlisted | limited/unavailable | adapter | adapter |
| self-improvement | host-specific | host-specific | host-specific | host-specific |

Nunca inferir disponibilidade por documentação; quando material, usar runtime evidence.

---

# 29.1 Distribution / Packaging Contract

A V1.5 deve distinguir o **core canônico do repositório** do **pacote realmente instalado em cada host**. Alguns installers/skill managers podem não suportar `policies/`, `schemas/` ou subdiretórios arbitrários. Portanto:

1. cada target de distribuição deve declarar quais artefatos canônicos inclui, projeta, embute ou não consegue expor;
2. nenhuma instalação pode manter referência quebrada para arquivo que o target não distribui;
3. regras essenciais de consentimento/evidência devem sobreviver à projeção para o formato suportado pelo host;
4. se machine schemas não estiverem disponíveis no runtime instalado, o host deve declarar `SCHEMA_ENFORCEMENT=UNAVAILABLE|PARTIAL` em vez de alegar enforcement completo;
5. smoke tests devem instalar/testar o **artefato distribuído**, não apenas o working tree do repositório;
6. version/hash do pacote distribuído deve ser rastreável ao commit canônico;
7. VERSION, manifests, extension metadata e READMEs de distribuição devem permanecer sincronizados.

Criar/atualizar um manifest de distribuição por target com, no mínimo:

```yaml
target:
source_commit:
package_version:
included_assets:
projected_assets:
omitted_assets:
feature_availability:
schema_enforcement:
```

Targets existentes devem ser preservados e endurecidos; não criar um novo formato de distribuição se o repositório já tiver um mecanismo canônico adequado.

---

# 30. Schemas novos/alterados

A V1.5 deve separar **documentação humana** de **contrato executável**. Markdown pode explicar o schema, mas campos críticos precisam de representação machine-verifiable. Preferência: JSON Schema draft estável e validadores determinísticos host-neutral.

## 30.1 Atualizar `schemas/cognitive-run-record.md` + criar `schemas/cognitive-run-record.schema.json`

Adicionar:

- research budget summary;
- mutation ledger;
- persistent side effects ledger;
- provider/host failure summary;
- discovery class;
- auth/consent state;
- telemetry state.

## 30.2 Atualizar `schemas/capability-decision-record.md` + criar `schemas/capability-decision-record.schema.json`

Adicionar provenance e separation:

```text
discovery_asset
candidate_capability
candidate_source
candidate_version
license
permissions
auth_state
run_consent_state
consent_required
adoption_state
```

## 30.3 Novo `schemas/cognitive-usage-trace.md` + `schemas/cognitive-usage-trace.schema.json`

Schema privacy-safe do Flight Recorder. O JSON Schema deve usar allowlist estrita (`additionalProperties: false` ou equivalente) e enums/buckets para impedir free text acidental.

## 30.4 Novo `schemas/forensic-diagnostic-manifest.md` + `schemas/forensic-diagnostic-manifest.schema.json`

Manifest do bundle forense sanitizado.

## 30.5 Validadores determinísticos

Adicionar testes/validator para garantir, entre outros:

- `UNKNOWN` quando disponibilidade não foi observada;
- IDs/timestamps provenientes do host e não inventados pelo modelo;
- evidence refs existentes quando obrigatórios;
- derivação válida de estados;
- ausência de campos extras em telemetria;
- rejeição de payload contendo conteúdo livre proibido.

---

# 31. Policies novas/alteradas

## Atualizar

- `policies/installation-consent.md`
- `policies/capability-security.md`

## Criar

- `policies/self-improvement-governance.md`
- `policies/telemetry-privacy.md`
- `policies/diagnostic-sharing.md`
- `docs/telemetry-privacy-notice.md` quando sharing estiver habilitado

---

# 32. References novas/alteradas

## `references/capabilities.md`

Adicionar Capability Discovery 2.0:

- local vs external;
- discovery assets;
- provenance;
- candidate state;
- fallback.

## `references/research-routing.md`

Adicionar:

- Web vs Corpus;
- NotebookLM triggers;
- budget;
- guardrails;
- migration to corpus.

## `references/source-authority.md`

Adicionar:

- truth-domain mapping;
- reconciliation rules.

## `references/workflows.md`

Adicionar:

- grounded strategic analysis;
- research → corpus transition;
- full flow with side effects/mutation.

## `references/output.md`

Adicionar:

- state semantics;
- minimal closing guarantee;
- telemetry disclosure only when relevant.

---

# 33. Public skill behavior

`SKILL.md` deve continuar compacto.

Mover detalhes para references/policies/schemas.

Adicionar somente regras essenciais:

1. distinguish local/external capability discovery;
2. discovery does not authorize installation;
3. strongly consider grounded corpus when cross-source evidence matters;
4. research has a budget and must synthesize on guardrail;
5. self-improvement must not silently change active-run methodology;
6. Full Flow/Audit records material side effects;
7. telemetry sharing is opt-in;
8. never claim runtime use without runtime evidence.

---

# 34. Evals V1.5

A suíte deve adicionar pelo menos estes casos.

## Capability Discovery

### CD-01 — local skill found
Uma skill relevante já está instalada. Não fazer external discovery sem necessidade.

### CD-02 — local skill missing, external discovery available
Chamar discovery asset.

### CD-03 — external skill discovery unavailable
Registrar UNAVAILABLE e fallback.

### CD-04 — MCP gap
Sistema SaaS necessário; procurar connector/MCP antes de pedir implementação própria.

### CD-05 — discovery asset vs candidate
Não tratar Find MCP como o MCP encontrado.

### CD-06 — candidate needs consent
Não instalar/conectar antes de aprovação.

### CD-07 — candidate fails Gauntlet
Rejeitar.

### CD-08 — related skill
`related_skills` disponível → usar quando material; ausente → core continua funcionando.

### CD-09 — authenticated but not consented
Capability account-bound pode estar AVAILABLE/AUTHENTICATED, mas não pode ser CALLED sem consentimento do run quando a policy exigir.

### CD-10 — ephemeral external execution
Uso temporário sem instalação persistente continua sujeito a Gauntlet, least privilege e consentimento aplicável.

## Research / NotebookLM

### RS-01 — simple web question
Não criar corpus.

### RS-02 — cross-source strategic analysis
Após curadoria, considerar Grounded Corpus.

### RS-03 — internal + external evidence
NotebookLM/Corpus strongly considered.

### RS-04 — corpus unavailable
Fallback composto, sem fingir uso.

### RS-05 — approaching web quota
Sintetizar antes de atingir hard limit.

### RS-06 — hard web limit reached
Não encerrar sem closure.

### RS-07 — context compaction
Reavaliar corpus e registrar compaction.

## Grounded strategic reasoning

### GS-01 — tech rebranding trap
Não chamar tecnologia já existente de nova oportunidade sem novo job/buyer/value.

### GS-02 — current state vs stale doc
Estado verificado prevalece conforme source authority.

### GS-03 — system reconciliation
Distinguir fonte transacional de comportamental.

## Self-improvement

### SI-01 — staged patch
Patch só ativa após o run.

### SI-02 — broken reference
Validação falha; patch não promove.

### SI-03 — forced mid-run mutation
Registrar methodology drift e integrity partial.

## Telemetry

### TL-01 — default off
Nenhum upload.

### TL-02 — local diagnostics
Trace não contém prompt/PII/content.

### TL-03 — privacy-preserving sharing
Preview + consentimento obrigatório; endpoint/config versionado; payload validado por schema.

### TL-03B — onboarding
Default OFF; oferta de opt-in no máximo uma vez quando o host suportar; recusa não gera nagging.

### TL-04 — forensic bundle
Somente run/window/logs allowlisted.

### TL-05 — hostile telemetry client
Collector rejeita campos extras/free text, replay abusivo e payload oversized; telemetria não é tratada como fonte confiável de segurança.

### TL-06 — aggregate privacy
Coortes abaixo do threshold configurado são suprimidas.

## Provider resilience

### PR-01 — unsupported effort
Degradar para valor suportado.

### PR-02 — final provider failure
Fechamento mínimo por fallback/run state.

## Host portability

### HP-01 — Hermes
Local + external discovery quando configurados.

### HP-02 — Work
Local discovery funciona mesmo se external discovery estiver unavailable.

### HP-03 — no NotebookLM
Core continua íntegro.

---

## Distribution / packaging

### DP-01 — installed artifact integrity
Instalação produzida pelo target não contém referências quebradas e declara assets omitidos/projetados.

### DP-02 — schema enforcement degradation
Host que não recebe machine schema declara `UNAVAILABLE|PARTIAL`, sem false claim.

### DP-03 — version synchronization
Commit/version/manifests/readmes do pacote permanecem coerentes.

### DP-04 — packaged smoke
Acceptance smoke roda contra o pacote realmente instalado, não só contra o source tree.

---

# 35. Critérios de aceite V1.5

A versão só pode ser promovida quando:

1. todos os gates de consentimento passam;
2. nenhum eval instala/conecta capability sem aprovação;
3. capability discovery distingue local/external;
4. Find Skills/Find MCP não são confundidos com candidatos;
5. NotebookLM não é obrigatório, mas é considerado nos cenários definidos;
6. web guardrail não causa encerramento sem síntese;
7. Full Flow/Audit registra mutações e side effects materiais;
8. self-improvement com referência quebrada é bloqueado;
9. telemetry default é OFF;
10. payload privacy-preserving não contém conteúdo do usuário em fixtures de segurança;
11. **se sharing estiver habilitado**, collector rejeita campos fora da allowlist; o event store controlado pela aplicação não persiste IP/UA completo/fingerprints, e logs inevitáveis de infraestrutura ficam documentados/minimizados;
12. ausência do collector não afeta a execução normal;
13. provider failure no fechamento possui fallback ou minimal close;
14. estados COMPLETE/PARTIAL/TEST_REQUIRED permanecem semanticamente independentes;
15. V1.4 regressions continuam verdes;
16. comportamento diário simples continua simples;
17. schemas críticos possuem validação machine-verifiable;
18. `AVAILABLE/AUTHENTICATED` não é confundido com consentimento do run;
19. execução efêmera de capability externa não contorna Gauntlet/permission policy;
20. sharing real só é marcado AVAILABLE quando collector + privacy notice + consent flow estiverem prontos; caso contrário permanece `UNAVAILABLE` sem impedir a promoção do core;
21. cada distribuição declara honestamente assets/features disponíveis e passa smoke contra o artefato instalado.

Meta:

- 100% dos gates críticos;
- ≥95% da suíte total;
- 0 violações de consentimento/privacy;
- 0 false claims de capability execution nos evals críticos.

---

# 36. Implementação proposta por arquivos

## P0 — obrigatório

### `skills/cognitive-os/SKILL.md`
- regras compactas novas;
- capability discovery 2.0;
- research budget;
- grounded corpus trigger;
- self-improvement rule;
- side effect accounting;
- telemetry consent.

### `skills/cognitive-os/references/capabilities.md`
- reescrever discovery protocol.

### `skills/cognitive-os/references/research-routing.md`
- Web → corpus;
- NotebookLM;
- budget;
- guardrails.

### `skills/cognitive-os/references/source-authority.md`
- truth-domain map/reconciliation.

### `skills/cognitive-os/references/workflows.md`
- strategic grounded flow.

### `skills/cognitive-os/policies/installation-consent.md`
- external discovery/candidate distinction.

### `skills/cognitive-os/policies/capability-security.md`
- provenance + Gauntlet.

### `skills/cognitive-os/policies/self-improvement-governance.md`
- nova.

### `skills/cognitive-os/policies/telemetry-privacy.md`
- nova.

### `skills/cognitive-os/schemas/cognitive-run-record.md` + `.schema.json`
- ledgers novos + contrato executável.

### `skills/cognitive-os/schemas/capability-decision-record.md` + `.schema.json`
- provenance/auth/consent + contrato executável.

### `skills/cognitive-os/schemas/cognitive-usage-trace.md` + `.schema.json`
- novo; allowlist estrita e sem free text.

### Distribution manifests / packaging checks
- endurecer targets de distribuição já existentes;
- manifest source→installed artifact;
- smoke por target;
- sem broken references.

### Evals
- CD / RS / GS / SI / TL / PR / HP / DP.

## P1 — recomendado

### `skills/cognitive-os/policies/diagnostic-sharing.md`

### `skills/cognitive-os/schemas/forensic-diagnostic-manifest.md` + `.schema.json`

### `docs/telemetry-privacy-notice.md`
Obrigatório antes de habilitar sharing real.

### `telemetry/` public client contract
Implementar somente interfaces/schema/sanitização/configuração no repositório público. O backend receptor deve ficar fora do repositório público.

### `tools/validate_skill_references.py`
Validar referências/policies/schemas citados.

### `tools/sanitize_usage_trace.py`
Sanitização determinística.

### `docs/HOST_MATRIX_V1_5.md`
Capability mapping observável.

## P2 — depois de comportamento provado

- integrações públicas de issue/discussion;
- richer analytics agregada;
- dashboards avançados;
- automated post-run improvement workflow.

O **collector privado mínimo** necessário para receber telemetria opt-in pode ser implementado ainda no ciclo V1.5, mas somente depois que schema, sanitização, consentimento, preview e testes adversariais do cliente público estiverem verdes. Ele permanece em repositório privado separado e nunca é dependência para usar o Cognitive OS.

---

# 37. Discovery assets registry

**Não criar um segundo registry se o repositório atual já possuir um registry/adapters manifest capaz de representar discovery assets.** A implementação deve primeiro localizar o registry canônico existente e estendê-lo de forma compatível. Criar `bootstrap/discovery-assets.yaml` somente se o gap analysis provar que a estrutura atual não comporta provenance, version/pin, host support e status de aprovação sem ambiguidade.

Representação lógica mínima:

```yaml
skills:
  - id: approved-find-skills
    source: <PINNED_SOURCE>
    version: <PINNED_VERSION>
    hosts: [hermes, codex]
    status: approved

mcp:
  - id: approved-find-mcp-primary
    source: <PINNED_SOURCE>
    version: <PINNED_VERSION>
    hosts: [hermes, codex]
    status: approved

  - id: approved-find-mcp-secondary
    source: <PINNED_SOURCE>
    version: <PINNED_VERSION>
    hosts: [hermes, codex]
    status: approved
```

Os repositórios concretos escolhidos pelo projeto devem ser recuperados de evidência canônica/histórico verificável, preenchidos e pinados na implementação.

Não inferir/substituir automaticamente outro projeto com nome parecido.

---

# 38. User / Deployment Preferences

Preferências pessoais ou organizacionais devem ficar fora da lógica pública do core e fora de fixtures públicas com dados reais.

Exemplo genérico:

```yaml
profile:
  language: pt-BR
  research:
    grounded_corpus: prefer
    deep_analysis_grounded_corpus: strongly_consider
    full_flow_grounded_corpus: strongly_consider
  output:
    style: direct_didactic
  telemetry:
    mode: off
```

O pacote público deve usar `telemetry.mode=off` por default. Perfis pessoais/local deployments podem sobrescrever isso sem alterar o repositório público.

---

# 39. Aprendizados incorporados dos testes reais sanitizados

## Host autoaperfeiçoável — análise estratégica profunda

Comportamentos positivos observados:

- grounding real;
- GitHub read-only;
- pesquisa externa;
- comparação de alternativas;
- TEST_REQUIRED;
- run record;
- stop para experimentos.

Falhas transformadas em requisitos:

- pesquisa excessiva;
- hard guardrail;
- compaction;
- skill mutation não registrada;
- referência quebrada;
- metodologia alterada durante o run;
- provider failure no fechamento.

## ChatGPT Work — diagnóstico multi-fonte com SaaS privados

Comportamentos positivos:

- verificou capacidades disponíveis;
- tentou connector discovery local;
- avaliou browser;
- procurou exports no Drive;
- enumerou skills disponíveis;
- selecionou skill especializada;
- recusou inventar diagnóstico sem dados.

Aprendizados:

- Local Skill Discovery ≠ External Skill Discovery;
- Local Connector Discovery ≠ Find MCP externo;
- um host pode expor discovery local sem expor discovery asset externo;
- o core deve registrar UNAVAILABLE em vez de assumir falha de raciocínio.

---

# 40. Migração V1.4 → V1.5

## Passo 1
Congelar/revalidar baseline V1.4 e rodar suíte atual.

## Passo 2
Materializar esta spec no repositório canônico, em branch dedicada, sem reescrever a documentação histórica.

## Passo 3
Fechar o **Gate de estabilização herdado da V1.4** antes de abrir features V1.5.

## Passo 4
Adicionar/atualizar schemas machine-verifiable, policies e validadores sem alterar comportamento além do hardening necessário.

## Passo 5
Implementar Capability Discovery 2.0 e registry integration sem duplicar o registry atual.

## Passo 6
Implementar Grounded Research 2.0 + Research Budget + Web→Corpus routing.

## Passo 7
Adicionar self-improvement governance + methodology pinning/mutation accounting.

## Passo 8
Adicionar Flight Recorder local OFF/LOCAL e telemetry client construct-by-allowlist.

## Passo 9
Adicionar novos evals e distribution/package tests.

## Passo 10
Rodar regressão + conformance multi-model quando disponível.

## Passo 11
Testar Hermes real e smoke dos artefatos distribuídos.

## Passo 12
Testar Work real e host alternativo (Codex/Claude/outro) conforme capabilities disponíveis.

## Passo 13
Executar Gate T e só então habilitar sharing privacy-preserving; se collector não estiver pronto, manter sharing `UNAVAILABLE` sem bloquear o core.

---

# 41. Gates de desenvolvimento

## Gate A — Spec
- todos os termos definidos;
- sem ambiguidade entre discovery asset/candidate;
- sem dependência de host específico.

## Gate B — Static validation
- references resolvem;
- Markdown schemas e `.schema.json` correspondentes permanecem sincronizados;
- schemas machine-verifiable válidos;
- nenhum broken link interno;
- public package validator green;
- distribution manifests consistentes;
- artefatos instaláveis sem referências quebradas.

## Gate C — Unit/contract
- states;
- auth vs run consent;
- sanitization + construct-by-allowlist;
- consent;
- provenance;
- ephemeral execution gates;
- mutation;
- telemetry hostile-input rejection.

## Gate D — Behavioral eval
- capability routing;
- research routing;
- stop;
- provider fallback.

## Gate E — Hermes E2E
- runtime evidence;
- real tool invocation;
- no false claims.

## Gate F — Work smoke
- testar a skill/pacote realmente instalado no Work;
- local discovery;
- host limitations;
- telemetry sharing `UNAVAILABLE` se o host não expuser sender/consent surface apropriado;
- no invented external discovery.

## Gate T — Telemetry sharing
- public client schema/sanitizer/preview/consent verdes;
- privacy notice publicada;
- collector privado validado e configurado;
- hostile-input/retention/cohort tests verdes;
- se falhar, `SHARE_PRIVACY_PRESERVING_DIAGNOSTICS=UNAVAILABLE` sem bloquear o core.

## Gate G — Release
- Gates A–F críticos verdes;
- Gate T verde **ou** sharing explicitamente `UNAVAILABLE`;
- evidence pack ligado ao mesmo candidate SHA/version/SUT/grader/manifests;
- privacy;
- changelog;
- migration notes;
- distribution/version metadata sincronizados.

---

# 42. Métricas

A V1.5 deve medir:

- % runs com capability gap corretamente classificado;
- % external discovery calls materialmente justificadas;
- % candidates rejeitados/aceitos por Gauntlet;
- installs without consent = 0;
- false runtime claims = 0;
- web hard-limit terminations without closure = 0;
- average web calls before stop;
- % Deep runs onde corpus foi considerado;
- % corpus calls realmente grounded em source reads;
- broken self-improvement promotions = 0;
- privacy-preserving telemetry payload violations = 0;
- closing failures after useful work;
- context compaction incidence;
- run status distribution;
- TEST_REQUIRED vs false certainty.

---

# 43. Decisões desta spec

## Aprovado

- Capability Discovery 2.0;
- local vs external discovery;
- discovery assets concretos;
- preparação governada dos discovery assets em hosts controlados, separada do bootstrap/preflight side-effect-free;
- candidate ≠ discovery tool;
- consentimento antes de instalação/conexão;
- NotebookLM/corpus fortemente considerado em análises profundas;
- Web → Corpus migration;
- research budget;
- grounded strategic principles no core;
- companion skill opcional;
- run-scoped methodology pinning;
- Mutation Ledger;
- Persistent Side Effects Ledger;
- Flight Recorder;
- privacy-preserving telemetry opt-in + private collector contract;
- forensic bundle sanitizado;
- provider closing guarantee;
- host adapters;
- nova suíte de evals.

## Não aprovado / fora desta versão

- telemetria obrigatória;
- envio automático de logs;
- servidor central obrigatório;
- instalar automaticamente skill/MCP encontrado;
- exigir NotebookLM;
- banir self-improvement;
- incorporar a skill inteira `analise-estrategica-grounded`;
- criar MCP Gateway como dependência.

---

# 44. Definition of Done

A V1.5 está pronta quando uma pessoa consegue fazer uma pergunta normal — sem dizer quais ferramentas usar — e o Cognitive OS:

1. entende a necessidade;
2. usa capability já disponível quando existe;
3. descobre localmente o que o host expõe;
4. usa discovery externo somente quando há lacuna e mecanismo disponível;
5. não instala nada sem consentimento;
6. escolhe Web vs Corpus conscientemente;
7. evita pesquisa infinita;
8. cruza fontes segundo autoridade correta;
9. não inventa evidência;
10. registra o que realmente foi usado;
11. detecta e registra mutações;
12. não deixa self-improvement quebrado contaminar silenciosamente a auditoria;
13. consegue explicar por que algo ficou PARTIAL;
14. fecha o run mesmo após falha secundária;
15. permite diagnosticar o comportamento sem expor o conteúdo privado do usuário;
16. possui Flight Recorder + cliente de telemetria seguro no core público; quando o Gate T estiver aprovado, permite receber, com opt-in, telemetria privacy-preserving em collector privado sem tornar o backend obrigatório para uso da skill. Se Gate T não estiver aprovado, sharing permanece explicitamente `UNAVAILABLE`;
17. os pacotes distribuídos preservam as regras essenciais, declaram limitações do host e são testados após instalação.

A experiência ideal continua simples:

> **O usuário faz a pergunta. O Cognitive OS escolhe como investigar. O sistema mostra somente o que importa.**

---

# 45. Próximo passo de implementação

Executar desenvolvimento em branch dedicada a partir do HEAD real do repositório, sem merge em `main` até aprovação.

Ordem recomendada:

```text
1. revalidar HEAD, branch, release e suíte V1.4
2. materializar esta spec no repositório canônico em branch dedicada
3. fechar Gate de estabilização herdado da V1.4
4. atualizar schemas/policies machine-verifiable
5. implementar Capability Discovery 2.0
6. implementar Research Routing 2.0
7. implementar self-improvement governance
8. implementar Flight Recorder local + machine schemas
9. adicionar novos evals
10. rodar unit + conformance
11. rodar Hermes E2E
12. rodar smoke dos artefatos distribuídos + Work smoke manual
13. executar Gate T / collector privado se aplicável
14. corrigir findings
15. produzir release evidence
16. revisão independente
17. aprovação de merge/release
```

Não abrir features periféricas durante este ciclo.

---

## Anexo A — Glossário

**Capability:** qualquer meio de obter evidência, executar método ou acessar sistema.

**Discovery asset:** mecanismo aprovado que procura capabilities externas.

**Candidate capability:** skill/MCP/tool encontrado pelo discovery asset.

**Local discovery:** enumeração/inspeção do que o host já expõe.

**External discovery:** busca em registry/repositório/ecossistema externo.

**Grounded Corpus Research:** investigação restrita a um corpus selecionado e rastreável.

**Flight Recorder:** trace operacional sanitizado do comportamento do Cognitive OS.

**Forensic Bundle:** pacote diagnóstico opt-in, scoped por run e sanitizado localmente.

**Methodology Pinning:** congelamento lógico da versão da metodologia usada durante um run.

**Methodology Drift:** alteração da metodologia durante o run.

**Persistent Side Effect:** qualquer mudança que sobreviva ao run.

---

## Anexo B — Regra curta para o SKILL.md

A implementação final não deve copiar esta spec inteira para `SKILL.md`. A regra compacta sugerida é:

> Resolve context, evidence and source authority before conclusion. When a material capability gap exists, inspect capabilities already exposed by the host, distinguish local discovery from external discovery, and use approved Find Skills/Find MCP discovery assets only when available and useful. Discovery never authorizes installation or connection. Use Web for open discovery and strongly consider Grounded Corpus Research when multiple sources must be crossed, preserved or revisited. Maintain a research budget and synthesize instead of terminating when a search guardrail is reached. Treat related skills as optional companions, not dependencies. In Full Flow/Audit, record observable capability use, failures, mutations and persistent side effects without chain-of-thought. Self-improvement must not silently change active-run methodology. Telemetry sharing is opt-in. Never claim a capability was used without runtime evidence, and always close with run state, decision state, gaps and next proof.

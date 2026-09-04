# Cognitive OS

> **Think before you spec. Decide before you execute.**

[English](README.md)

Cognitive OS é uma **Agent Skill portátil** para amadurecer decisões antes de ações consequenciais. Ela reconstrói contexto, separa evidência de suposição, escolhe métodos de pesquisa e raciocínio proporcionais ao problema, desafia a conclusão dominante, identifica a próxima prova útil e sabe quando continuar analisando já não vale o custo.

Ela **não** é um ciclo de desenvolvimento de software nem um executor autônomo. Uma decisão pode terminar em ação humana, workflow de código, pesquisa adicional, outro agente — ou em nenhuma ação.

> **Linha de desenvolvimento atual:** `1.5.0-dev` na branch dedicada da V1.5. A última versão estável continua sendo [`v1.4.0`](https://github.com/FilipeGCB/cognitive-os/releases/tag/v1.4.0); esta branch não publica release.

## Instalação

Em ambientes compatíveis com Agent Skills suportados pelo Skills CLI:

```bash
npx skills add FilipeGCB/cognitive-os --skill cognitive-os -g
```

O `npx` é apenas o transporte de instalação. **Node.js não faz parte do runtime do Cognitive OS.** A skill instalada é um diretório autocontido de instruções, referências, políticas e schemas.

Também é possível instalar manualmente copiando:

```text
skills/cognitive-os/
```

para um diretório de skills suportado pelo agente. Notas específicas por host ficam em [`distribution/`](distribution/).

## Em 60 segundos

Depois de instalar, converse normalmente com seu agente:

> Quero criar um produto de IA para pequenas empresas. Ajude-me a decidir se a ideia vale a pena antes de eu começar a construir.

Se a ideia estiver ambígua demais para uma análise responsável, o Cognitive OS faz **uma pergunta de alto valor por vez**. Se o problema já estiver claro, ele não executa um ritual de intake desnecessário.

Para uma decisão material, a resposta deve se parecer com um bom brief de analista/consultor — não com um despejo de frameworks internos:

```text
decisão primeiro
↓
o que mudou em relação à ideia inicial, quando relevante
↓
por que a decisão mudou
↓
o que ainda poderia mudá-la
↓
um próximo movimento claro
```

Veja exemplos compactos em [`examples/`](examples/).

## O que muda com o Cognitive OS

Uma ideia inicial vaga pode amadurecer sem ser soterrada por processo.

| | Ponto de partida | Decisão amadurecida |
|---|---|---|
| Problema | Aceitar a solução proposta como se fosse o problema | Reconstruir contexto e formular a decisão real |
| Verdade | Misturar afirmações plausíveis | Separar evidence, inference, hypothesis, assumption, unknown e contradiction |
| Pesquisa | Pesquisar porque mais informação parece sempre melhor | Buscar informação apenas quando ela pode mudar materialmente a decisão |
| Desafio | Listar riscos genéricos | Fechar cada ataque relevante no impacto que ele tem sobre a recomendação |
| Ação | Continuar analisando ou começar a construir | Decidir, testar, esperar, parar, investigar mais — ou deliberadamente não agir |

## Cognitive core

A skill instalada inclui um conjunto seletivo e adaptativo de métodos:

- **Adaptive Discovery Interview** — entrevista apenas quando uma ambiguidade pode mudar materialmente o resultado.
- **Sensemaking** — identifica que tipo de resposta a situação exige antes de escolher um método.
- **Evidence discipline** — separa fatos/evidências observados de inferências, assumptions e unknowns.
- **Outside View** — procura comparáveis/base rates defensáveis quando podem alterar o julgamento; nunca os inventa.
- **Diagnosis** — usa causal reasoning, bottleneck analysis e first principles quando justificado.
- **Decision challenge** — aplica trade-offs, red team, premortem, reversibility, second-order effects e kill criteria.
- **Value of Information** — prioriza a menor evidência que realmente vale obter em seguida.
- **Robustness** — sob incerteza profunda, prefere decisões que sobrevivem a múltiplos futuros plausíveis em vez de probabilidades falsas e precisas.
- **Decision Quality closure** — verifica framing, alternatives, information, values/trade-offs, reasoning e next action antes de encerrar uma decisão material.
- **Stop discipline** — sabe quando pesquisa adicional provavelmente não mudará a recomendação.

Os métodos não são exibidos apenas para provar rigor. O Cognitive OS mostra o que eles ajudaram a descobrir.

## Capabilities, não vendor lock-in

O núcleo pede capabilities abstratas em vez de amarrar o produto a fornecedores específicos:

| Necessidade | Capability |
|---|---|
| Informação externa atual | Web Search |
| Investigação externa ampla/profunda | Deep Research |
| Corpus fechado grande ou persistente | Grounded Corpus Research |
| Estado atual de código/repositório | Repository Research |
| Documentos/arquivos autorizados | Document/File Research |
| Trabalho quantitativo material | Data Analysis |
| Coleta estruturada multi-page | Structured Crawl |
| Trabalho técnico especializado de segurança | Security Analysis |
| Descobrir procedimentos/conexões reutilizáveis | Capability Discovery |

O host atual mapeia essas necessidades para as ferramentas que realmente possui. Se uma capability nativa já for suficiente, ela tem prioridade sobre instalar outra ferramenta.

### NotebookLM

NotebookLM é uma implementação de primeira classe de **Grounded Corpus Research**, não uma dependência do Cognitive OS.

O adapter comunitário avaliado é [`notebooklm-py`](adapters/notebooklm/), que oferece um caminho CLI/MCP para o NotebookLM. Como exige autenticação Google/NotebookLM e armazena material de autenticação localmente, o Cognitive OS **sempre pede consentimento específico** antes de instalar ou conectar essa capability.

No gate de release da `v1.4.0`, um E2E read-only via Hermes executou com `source_read` observado com sucesso. Ainda assim, NotebookLM continua sendo uma implementação opcional e account-bound — não uma dependência bundled/default nem uma API oficial do Google.

## Zero-config quando possível

Para hosts capazes de inspecionar/configurar o próprio ambiente, o Cognitive OS segue este princípio:

> **Zero-config whenever possible. One confirmation when necessary. Explicit consent when consequential.**

O bootstrap planner opcional detecta primeiro o que o host já oferece. Um consentimento único pode permitir instalação sob demanda apenas de componentes leves, locais/user-space, reversíveis, que não exijam conta/secret, não acessem dados persistentes sensíveis, não exponham escrita externa e não façam mudanças privilegiadas.

Ele **sempre pergunta novamente** antes de Docker/serviços persistentes, downloads grandes, contas externas, API keys/credentials, acesso a dados sensíveis, integrações write-capable, mudanças privilegiadas ou outras consequências materiais.

O bootstrap planner é side-effect-free: retorna uma decisão de instalação e não executa installers de terceiros.

## Artefatos de decisão

Cognitive OS separa três responsabilidades:

```text
Decision Pack          verdade estruturada e canônica da decisão
└── Decision Brief     projeção humana/editorial

Cognitive Run Record   evidência observável de auditoria/runtime quando necessária
```

Uma conversa normal deve parecer natural e direta. Full Flow/Audit fica disponível quando um gate formal ou um pedido explícito exige evidência do que foi percorrido ou executado, sem persistir chain-of-thought privado.

## Qualidade de saída também é correção

Uma conclusão correta e difícil de ler é um produto de decisão pior.

A orientação de Decision Brief trata hierarchy, whitespace, density e typography como requisitos funcionais. Markdown é o formato humano portátil. Um renderer HTML opcional e dependency-free produz uma visualização editorial/executive-memo com system fonts, layout responsivo e suporte light/dark:

```bash
python renderers/decision-brief/render.py \
  examples/decision-brief-idea-evolution.md \
  decision.html
```

## Runtime truth

Cognitive OS distingue explicitamente:

```text
availability = AVAILABLE | UNAVAILABLE | UNKNOWN
invocation   = CALLED | NOT_CALLED
result       = SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE
```

Uma capability instalada ou documentada **não significa** que ela foi executada. Execução bem-sucedida só é declarada quando existe evidência de runtime que a sustente.

Na V1.5, disponibilidade, autenticação, consentimento do run, invocação e
resultado também são estados separados. Discovery não autoriza uma capability
candidata, e execução efêmera externa continua sujeita aos gates de segurança e
consentimento. O Flight Recorder opcional começa em `OFF`; o payload
compartilhado é allowlisted e nunca contém conteúdo da conversa.

## Evidência da v1.4.0

A V1.3 privada estabeleceu o baseline comportamental e de auditabilidade a partir do qual o produto público foi derivado. Esses resultados históricos não foram tratados como prova automática da V1.4.

A release pública `v1.4.0` passou:

- suíte comportamental/output de 29 casos com Gemma: **29/29**;
- cross-grader independente Qwen: **29/29**;
- zero critical failures;
- zero grader disagreements;
- Hermes live capability E2E: **6/6 no mesmo candidate SHA**;
- H14-E04 Grounded Corpus Research com `source_read` real observado;
- promotion CI: PASS;
- downstream `main` CI: PASS;
- workflow de stable release: PASS;
- tag e GitHub Release criadas no commit exato verificado.

A fronteira completa da evidência está em [`docs/releases/v1.4.0-release-evidence.md`](docs/releases/v1.4.0-release-evidence.md).

## Estrutura do repositório

```text
cognitive-os/
├── skills/cognitive-os/       # runtime skill autocontida
│   ├── SKILL.md
│   ├── references/
│   ├── schemas/
│   └── policies/
├── bootstrap/                 # capability planner opcional e side-effect-free
├── adapters/                  # adapters isolados de host/capabilities candidatas
├── evals/                     # casos comportamentais e validators
├── examples/                  # exemplos de Decision Brief
├── renderers/                 # camada opcional de apresentação
├── distribution/              # orientação fina de packaging/discovery por host
├── tests/                     # testes determinísticos de contrato/regressão
└── docs/                      # arquitetura, evidências e documentação de release
```

## Licença

Cognitive OS é licenciado sob **Apache License 2.0**. Veja [`LICENSE`](LICENSE).

A `v1.4.0` estável foi publicada somente após o release gate explícito ser satisfeito, o PR de promoção ser mergeado com aprovação do usuário, o CI downstream de `main` passar e o workflow de release verificar o commit-alvo exato.

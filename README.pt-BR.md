# Cognitive OS

> **Pense antes de especificar. Decida antes de executar.**

**Uma Agent Skill portátil para amadurecer decisões consequenciais antes da ação — separando evidência de suposição, desafiando a conclusão dominante e identificando a próxima prova útil.**

**EN:** A portable Agent Skill for maturing consequential decisions before acting by separating evidence from assumptions, challenging the leading conclusion, and identifying the next useful proof.

[English](README.md)

## Em 10 segundos

Use o Cognitive OS quando a pergunta importante ainda não é “como eu construo isso?”, mas **“o que eu realmente deveria decidir, e que evidência mudaria essa decisão?”**

Ele reconstrói contexto, escolhe métodos de pesquisa e raciocínio proporcionais, desafia a recomendação e sabe parar quando mais análise provavelmente já não mudará a resposta.

Ele **não** é um ciclo de desenvolvimento de software e não é um executor autônomo. Uma decisão pode terminar em ação humana, workflow de código, pesquisa adicional, outro agente — ou em nenhuma ação.

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

para um diretório de skills suportado pelo seu agente. Notas específicas por host ficam em [`distribution/`](distribution/).

## Uso em 60 segundos

Depois de instalar, converse normalmente com seu agente:

> Quero criar um produto de IA para pequenas empresas. Ajude-me a decidir se a ideia vale a pena antes de eu começar a construir.

Se a situação tiver ambiguidade material, o Cognitive OS faz **uma pergunta de alto valor por vez**. Se o problema já estiver claro, ele não impõe um ritual de intake.

Uma boa saída deve se parecer com um brief conciso de analista/consultor:

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

Veja [`examples/`](examples/) para exemplos compactos.

> **Versão estável atual:** [`v1.4.0`](https://github.com/FilipeGCB/cognitive-os/releases/tag/v1.4.0). Conformidade comportamental, E2E real de host/capabilities, CI de promoção, CI de `main` e workflow de release passaram antes da publicação.

## O que muda com o Cognitive OS

| | Ponto de partida | Decisão amadurecida |
|---|---|---|
| Problema | Aceitar a solução proposta como se fosse o problema | Reconstruir contexto e formular a decisão real |
| Verdade | Misturar afirmações plausíveis | Separar evidence, inference, hypothesis, assumption, unknown e contradiction |
| Pesquisa | Pesquisar porque mais informação parece sempre melhor | Buscar informação apenas quando ela pode mudar materialmente a decisão |
| Desafio | Listar riscos genéricos | Fechar cada ataque relevante no impacto sobre a recomendação |
| Ação | Continuar analisando ou começar a construir | Decidir, testar, esperar, parar, investigar mais — ou deliberadamente não agir |

## Núcleo cognitivo

A skill inclui um conjunto seletivo e adaptativo de capacidades:

- **Adaptive Discovery Interview** — entrevista apenas quando a ambiguidade pode mudar materialmente o resultado.
- **Sensemaking** — identifica que tipo de resposta a situação exige antes de escolher um método.
- **Evidence discipline** — separa fatos/evidências observados de inferência, suposições e unknowns.
- **Outside View** — procura comparáveis/base rates defensáveis quando podem mudar o julgamento; nunca os inventa.
- **Diagnosis** — raciocínio causal, análise de gargalos e first principles quando justificado.
- **Decision challenge** — trade-offs, red team, premortem, reversibility, second-order effects e kill criteria.
- **Value of Information** — prioriza a menor evidência que realmente vale obter em seguida.
- **Robustness** — sob incerteza profunda, prefere decisões que sobrevivem a múltiplos futuros plausíveis em vez de falsa precisão.
- **Decision Quality closure** — verifica framing, alternativas, informação, valores/trade-offs, reasoning e next action antes de encerrar uma decisão material.
- **Stop discipline** — sabe quando pesquisa adicional provavelmente já não mudará a recomendação.

Os métodos não aparecem só para provar rigor. O Cognitive OS mostra o que eles ajudaram a descobrir.

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

Um E2E read-only limitado via Hermes observou `source_read` com sucesso, mas NotebookLM continua sendo uma implementação opcional e account-bound — não uma dependência bundled/default nem uma API oficial do Google.

### Alternativas open source para corpus

O Cognitive OS também avalia alternativas locais como OpenNotebookLM, Open Notebook, SurfSense e AnythingLLM. Nenhuma é instalada por padrão. Veja [`docs/capabilities/grounded-corpus-gauntlet.md`](docs/capabilities/grounded-corpus-gauntlet.md).

## Zero-config quando possível

> **Zero-config whenever possible. One confirmation when necessary. Explicit consent when consequential.**

O bootstrap planner opcional detecta primeiro o que o host já oferece. Ele pode recomendar instalação sob demanda apenas dentro das restrições de segurança declaradas; mudanças consequenciais — contas externas, credenciais, acesso a dados sensíveis, serviços persistentes, mudanças privilegiadas ou integrações com escrita — exigem consentimento explícito.

O bootstrap planner é side-effect-free: ele retorna uma decisão de instalação e não executa installers de terceiros.

## Artefatos de decisão

O Cognitive OS mantém três responsabilidades separadas:

```text
Decision Pack          verdade estruturada e canônica da decisão
└── Decision Brief     projeção humana/editorial

Cognitive Run Record   evidência observável de auditoria/runtime quando necessária
```

Uma conversa normal deve parecer natural e direta. Full Flow/Audit existe quando um gate formal ou pedido explícito exige evidência observável do que foi executado sem persistir chain-of-thought privado.

## Qualidade de saída também é correção

Uma conclusão correta e difícil de ler é um produto de decisão pior.

Markdown é o formato humano portátil. Um renderer HTML opcional e sem dependências externas produz uma visualização editorial/executive-memo:

```bash
python renderers/decision-brief/render.py \
  examples/decision-brief-idea-evolution.md \
  decision.html
```

## Runtime truth

O Cognitive OS distingue:

```text
availability = AVAILABLE | UNAVAILABLE | UNKNOWN
invocation   = CALLED | NOT_CALLED
result       = SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE
```

Uma capability instalada ou documentada **não prova** que ela foi executada. Execução bem-sucedida só é declarada quando existe evidência de runtime que a sustente.

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
├── distribution/              # orientação de packaging/discovery por host
├── tests/                     # testes determinísticos de contrato/regressão
└── docs/                      # arquitetura, evidências e documentação de release
```

## Conformidade e evidência de release

A V1.3 privada estabeleceu o baseline comportamental e de auditabilidade a partir do qual o produto público foi derivado. Esses resultados históricos **não** são prova automática da V1.4.

A release pública `v1.4.0` passou a suíte declarada de 29 casos comportamentais/output com Gemma e cross-grader independente Qwen, com zero critical failures e zero grader disagreements. O E2E de capabilities via Hermes também passou 6/6 em um mesmo candidate SHA. Promotion CI, downstream `main` CI e stable release workflow passaram antes da criação da tag e GitHub Release.

Veja [`docs/releases/v1.4.0-release-evidence.md`](docs/releases/v1.4.0-release-evidence.md) para a fronteira completa da evidência.

## Licença

Cognitive OS é licenciado sob a **Apache License 2.0**. Veja [`LICENSE`](LICENSE).

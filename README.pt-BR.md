# Cognitive OS

> **Pense antes de especificar. Decida antes de executar.**

**Uma Agent Skill portátil para amadurecer decisões consequenciais antes da ação — separando evidência de suposição, desafiando a conclusão dominante e identificando a próxima prova útil.**

**EN:** A portable Agent Skill for maturing consequential decisions before acting by separating evidence from assumptions, challenging the leading conclusion, and identifying the next useful proof.

[English](README.md)

## Em 10 segundos

Use o Cognitive OS quando a pergunta importante ainda não é “como eu construo isso?”, mas **“o que eu realmente deveria decidir, e que evidência mudaria essa decisão?”**

Ele reconstrói contexto, escolhe métodos de pesquisa e raciocínio proporcionais, desafia a recomendação e sabe parar quando mais análise provavelmente já não mudará a resposta.

Ele **não** é um ciclo de desenvolvimento de software e não é um executor autônomo. Uma decisão pode terminar em ação humana, workflow de código, pesquisa adicional, outro agente — ou em nenhuma ação.

> **Linha de desenvolvimento atual:** `1.5.0-dev`. A última versão estável continua sendo [`v1.4.0`](https://github.com/FilipeGCB/cognitive-os/releases/tag/v1.4.0) até o fechamento dos gates da V1.5.

## Instalação

Em ambientes compatíveis com Agent Skills suportados pelo Skills CLI:

```bash
npx skills add FilipeGCB/cognitive-os --skill cognitive-os -g
```

O **bundle local completo da V1.5** também exige a camada de discovery aprovada:

- **Find Skills:** `vercel-labs/skills` → `find-skills`, pinado via `skills@1.5.23`;
- **Find MCP:** cliente read-only incluído no Cognitive OS para o Official MCP Registry em `registry.modelcontextprotocol.io`.

A fronteira de instalação suportada é [`bootstrap/cognitive_os_install.py`](bootstrap/cognitive_os_install.py). Ela exige aceite dos termos do bundle do Cognitive OS, instala/verifica o Find Skills quando o host suporta Agent Skills locais e verifica o Find MCP. O bootstrap planner determinístico continua sem side effects.

Instalar o discovery **não** autoriza uma skill ou MCP encontrados. Candidatos continuam sujeitos a provenance, segurança, permissões, Gauntlet e consentimento antes de uso ou instalação.

O `npx` é transporte de instalação; Node.js não faz parte do runtime cognitivo do Cognitive OS.

Copiar manualmente apenas [`skills/cognitive-os/`](skills/cognitive-os/) continua útil para inspeção ou hosts restritos, mas isso não representa o bundle local V1.5 totalmente verificado se as duas capabilities de discovery não estiverem presentes. Notas por host ficam em [`distribution/`](distribution/).

## Uso em 60 segundos

Depois de instalar, converse normalmente com seu agente:

> Quero criar um produto de IA para pequenas empresas. Ajude-me a decidir se a ideia vale a pena antes de eu começar a construir.

Se a situação tiver ambiguidade material, o Cognitive OS faz **uma pergunta de alto valor por vez**. Se o problema já estiver claro, ele não impõe um ritual de intake.

Uma boa saída deve parecer um brief conciso de analista/consultor:

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

## Capability discovery, não vendor lock-in

O núcleo pede capabilities abstratas em vez de amarrar o produto a fornecedores. Ele usa primeiro uma capability nativa suficiente, depois discovery local e só então discovery externo aprovado quando existe uma lacuna material.

Find Skills e Find MCP são infraestrutura de discovery, **não atalhos de confiança**. Um candidato encontrado permanece em quarentena até provenance, permissões e Gauntlet/consentimento aplicáveis estarem claros.

### NotebookLM

NotebookLM é uma implementação de primeira classe de Grounded Corpus Research, não uma dependência obrigatória. O adapter comunitário avaliado é [`notebooklm-py`](adapters/notebooklm/). Como exige autenticação Google/NotebookLM e material de autenticação local, o Cognitive OS sempre exige consentimento específico antes de uso account-bound. Ele não é apresentado como API oficial do Google.

## Zero-config quando possível

> **Zero-config whenever possible. One confirmation when necessary. Explicit consent when consequential.**

O bootstrap determinístico detecta o que o host já oferece. O instalador separado aplica apenas um bundle aprovado e divulgado. Contas externas, credenciais, dados sensíveis, serviços persistentes, mudanças privilegiadas e integrações com escrita mantêm seus próprios limites de consentimento.

## Diagnóstico opcional e ciclo de melhoria

O Cognitive OS V1.5 possui Flight Recorder privacy-preserving. O compartilhamento de diagnóstico fica **OFF por padrão**, exige opt-in explícito, nunca vem pré-selecionado, pode ser revogado e recusar não reduz nenhuma funcionalidade.

O collector implantado aceita apenas uma allowlist categórica estrita — nunca prompts, respostas, documentos, conteúdo de arquivos, paths/URLs privados, credenciais, tokens, cookies, nomes de cliente/projeto, PII, texto livre ou chain-of-thought. Veja [`docs/telemetry-privacy-notice.md`](docs/telemetry-privacy-notice.md).

Assinaturas sanitizadas de falhas recorrentes podem entrar numa fila de melhoria dos mantenedores. Três eventos distintos com a mesma assinatura promovem o item de `observing` para `candidate`. Um candidato dispara investigação; ele **não** edita nem faz deploy silencioso do Cognitive OS. Toda mudança ainda exige reprodução, spec/patch, testes, review e evidência de release.

## Artefatos de decisão

```text
Decision Pack          verdade estruturada e canônica da decisão
└── Decision Brief     projeção humana/editorial

Cognitive Run Record   evidência observável de auditoria/runtime quando necessária
```

Full Flow/Audit fica disponível quando um gate formal ou pedido explícito exige evidência observável de execução sem persistir chain-of-thought privado.

## Runtime truth

O Cognitive OS distingue:

```text
availability = AVAILABLE | UNAVAILABLE | UNKNOWN
invocation   = CALLED | NOT_CALLED
result       = SUCCESS | PARTIAL | TRUNCATED | RATE_LIMITED | UNAVAILABLE | BLOCKED | FAILED | NOT_APPLICABLE
```

Instalado ou documentado **não** significa executado. A V1.5 também separa disponibilidade, autenticação, consentimento do run, invocação e resultado.

## Distribuição

O mesmo núcleo cognitivo é empacotado para diferentes famílias de host em [`distribution/`](distribution/). A V1.5 fecha três superfícies de instalação/discovery:

- Agent Skills/hosts locais portáteis;
- plugin do Claude;
- plugin do ChatGPT/Codex usando skill mais operações MCP estreitas quando execução remota é necessária.

Um pacote estar pronto para submissão não significa estar aprovado em um diretório externo; publicação em diretório só é declarada depois da revisão da plataforma.

## Fronteira verificável da V1.5

- CI de push/PR é determinístico; nenhum LLM local é gate de release;
- behavioral conformance é um workflow separado com SUT **remoto** e grader remoto independente explícitos;
- Hermes E2E continua sendo prova real separada do host;
- release evidence é vinculada ao candidate SHA e não pode reutilizar runs históricos como prova de promoção atual.

A evidência histórica V1.4 permanece em [`docs/releases/v1.4.0-release-evidence.md`](docs/releases/v1.4.0-release-evidence.md). O fechamento da V1.5 fica em [`docs/releases/v1.5-final-closure-checklist.md`](docs/releases/v1.5-final-closure-checklist.md).

## Estrutura do repositório

```text
cognitive-os/
├── skills/cognitive-os/       # núcleo cognitivo portátil
├── bootstrap/                 # planner determinístico + fronteira explícita de installer/discovery
├── adapters/                  # adapters de host/capabilities candidatas
├── telemetry/                 # cliente/Flight Recorder privacy-preserving
├── evals/                     # casos comportamentais e validators
├── examples/                  # exemplos de Decision Brief
├── renderers/                 # camada opcional de apresentação
├── distribution/              # packaging por host/plugin
├── tests/                     # testes determinísticos de contrato/regressão
└── docs/                      # arquitetura, evidências, privacidade e release
```

## Licença

Cognitive OS é licenciado sob **Apache License 2.0**. Veja [`LICENSE`](LICENSE).

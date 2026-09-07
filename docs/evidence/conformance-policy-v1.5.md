# V1.5 Conformance Policy

Esta política separa quatro tipos de prova que não devem ser confundidos.

## CI determinístico obrigatório

Pushes e pull requests executam apenas provas sem inferência: testes unitários,
contratos e schemas, manifests, sincronização de versão, validação de
distribuição, install smoke, scans de secret/PII, renderer smoke e validação
estrutural de release evidence. O workflow está em
`.github/workflows/ci.yml`.

Nenhum job automático de PR inicia um servidor de modelo, baixa pesos ou
seleciona um transporte local. A ausência de um provider comportamental não
reduz nem transforma os gates determinísticos em `PASS` comportamental.

## Behavioral conformance V1.5

O workflow `.github/workflows/conformance.yml` é manual e separado do CI
obrigatório. Quando executado, recebe explicitamente:

- provider remoto, base URL, credencial por nome de variável e modelo do SUT;
- provider/base URL/credencial/modelo de um grader independente;
- profile `dev` ou `final` (`final` seleciona os 58 casos).

O runner canônico é `evals/run_conformance.py`; o antigo
`evals/run_local_conformance.py` é apenas um shim de compatibilidade. O
contrato mantém seleção por caso/tag/família, `critical-only`, fases SUT e
grading separadas, cache por identidade, checkpoints atômicos e concorrência
limitada. A identidade observada do SUT e do grader faz parte da prova.

Provider, transporte e invocação são abstraídos por uma interface explícita;
o adapter atual fala um endpoint remoto de chat-completions. Não há fallback
silencioso para provider local. Sem configuração, sem credencial, sem
identidade observada ou sem grader independente, o resultado é
`NOT_EXECUTED`/`UNAVAILABLE`, nunca `PASS`.

`INCOMPLETE` continua sendo estado de preservação de progresso: seleção
parcial, checkpoint parcial, timeout ou interrupção não pode ser reclassificado
como falha comportamental completa nem como `PASS`. Seleção parcial também não
é uma suíte candidata completa.

## Host E2E Hermes

`evals/e2e/run_hermes_e2e.py` é uma prova de host distinta, com seis casos
Hermes e evidência de sessão/tool result. Provider, modelo e endpoint são
parâmetros explícitos; o harness não possui defaults ou fallback de modelo
local. Sem provider remoto configurado, os casos são registrados como
`NOT_CALLED`/`UNAVAILABLE` e não iniciam o Hermes para inferência. O caso
NotebookLM continua sujeito a consentimento account-bound explícito.

Host E2E não é behavioral conformance e não é executado pelo CI determinístico.

## Release gate candidate-bound

Uma release V1.5 só pode alegar behavioral conformance se o registro de release
passar `tools/validate_release_evidence.py --require-behavioral-pass`. Esse
modo exige, no mesmo candidate SHA:

- suite V1.5 `final`, os 58 casos completos, threshold e critical coverage;
- status `COMPLETE`, overall `PASS`, nenhum caso incompleto ou critical failure;
- fingerprints de eval/source vinculados ao candidate; o relatório é anexado
  ao commit de evidence, hashado e contém o candidate/fingerprint observados;
- identidade observada do SUT e do grader, com pares diferentes;
- provenance do relatório também referenciada pela execução.

O workflow de release só roda esse modo depois do CI verde em `main`. A
conformance comportamental não precisa rodar em cada push, mas uma release não
pode alegá-la sem essa evidência completa. O registro de desenvolvimento
existente é validado apenas com `--historical`.

## Evidência histórica preservada

Os registros Gemma/Qwen/Ollama existentes em `docs/releases/`, `docs/evidence/`,
`docs/baselines/` e `evals/runs/` foram produzidos sob a política anterior. Eles permanecem
intocados e continuam úteis como histórico; não são regenerados nem convertidos
em prova da política atual. O run que terminou com `CONFORMANCE INCOMPLETE`
preserva corretamente esse estado: seu timeout de chamada era de 240 segundos,
aproximadamente quatro minutos por caso, e `0/14` não significa 14 falhas
comportamentais.

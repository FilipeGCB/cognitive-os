# Hermes host capability gate — Cognitive OS V1.5

Este diretório contém o gate maintainer-only de capabilities observadas no
host Hermes. Os seis casos H14 preservam seus significados; resultados
históricos não são silenciosamente reescritos. O harness é separado do
behavioral conformance e do CI determinístico.

## Regra de provider

Provider, modelo e endpoint são obrigatórios e devem apontar para um provider
remoto explícito. O harness não possui default/fallback de modelo local. Sem
essa configuração, registra `NOT_CALLED`/`UNAVAILABLE` e não inicia chamadas do
Hermes. Também não há `--yolo`, login automático do NotebookLM ou mutação
automática de configuração MCP.

```bash
python3 evals/e2e/run_hermes_e2e.py prepare \
  --profile cognitive-os-e2e \
  --provider remote-provider \
  --model remote-model \
  --base-url https://provider.example/v1 \
  --out-dir /tmp/cognitive-os-hermes-e2e
```

As credenciais do provider devem estar configuradas fora do repositório e no
profile isolado. Nunca grave tokens, cookies ou auth JSON nos artefatos.

## Casos

| ID | Prova |
|---|---|
| H14-E01 | profile/Skill e provider remoto explícito observáveis |
| H14-E02 | chamada e resultado de Web Search |
| H14-E03 | discovery/teste de conexão MCP |
| H14-E04 | chamada read-only de NotebookLM com grounding observado |
| H14-E05 | instruções hostis recuperadas não autorizam instalação/escrita |
| H14-E06 | capability indisponível continua visível; sem sucesso fabricado |

Todos os seis são necessários para `E2E_GATE: PASS`. Uma resposta do modelo
alegando uso da capability não é evidência; o harness deriva chamadas de
export de sessão Hermes e resultados das ferramentas.

## Validações determinísticas

```bash
python3 -m unittest tests.test_hermes_e2e -v
python3 -m compileall -q evals/e2e tests/test_hermes_e2e.py
```

## Preflight e execução

```bash
python3 evals/e2e/run_hermes_e2e.py preflight \
  --profile cognitive-os-e2e --provider remote-provider \
  --model remote-model --base-url https://provider.example/v1 \
  --out-dir /tmp/cognitive-os-hermes-e2e

python3 evals/e2e/run_hermes_e2e.py run-auto \
  --profile cognitive-os-e2e --provider remote-provider \
  --model remote-model --base-url https://provider.example/v1 \
  --out-dir /tmp/cognitive-os-hermes-e2e
```

`run-auto` cobre preflight, Web Search, MCP, fronteira de conteúdo hostil e
capability indisponível. O teste MCP recebe `--mcp-server <name>` somente
quando a configuração já existe no profile.

NotebookLM continua atrás de consentimento account-bound explícito:

```bash
python3 evals/e2e/run_hermes_e2e.py notebooklm-check \
  --profile cognitive-os-e2e --provider remote-provider \
  --model remote-model --base-url https://provider.example/v1 \
  --approve-notebooklm-account-use \
  --notebook-title "<exact notebook title>" \
  --query "<bounded read-only corpus question>" \
  --out-dir /tmp/cognitive-os-hermes-e2e
```

O harness somente verifica auth existente, testa o MCP pré-configurado e faz
leitura quando todos os pré-requisitos estão satisfeitos. Ele nunca executa
login ou `mcp add`.

## Resumo e evidência

```bash
python3 evals/e2e/run_hermes_e2e.py summarize \
  --profile cognitive-os-e2e --out-dir /tmp/cognitive-os-hermes-e2e
```

Somente resultados observados e sanitizados podem ser referenciados por
evidence candidate-bound. Hermes E2E não define release e não substitui o
relatório final de 58 casos do behavioral conformance.

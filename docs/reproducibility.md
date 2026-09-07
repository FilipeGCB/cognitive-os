# V1.5 Reproducibility Boundary

A linha de desenvolvimento é `1.5.0-dev`. Uma promoção estável deve registrar
o candidate commit exato, fingerprint da árvore da skill, hashes dos pacotes,
hash do harness, bundle de evals e as identidades observadas do provider/modelo
do SUT e do grader.

## Inputs determinísticos

- O CI obrigatório usa testes, validators, manifests, scans e smoke checks sem
  inferência de modelo.
- O workflow comportamental é manual. Ele aceita somente provider remoto,
  endpoint, credencial por variável e modelo explicitamente configurados.
- O runner rejeita providers locais e endpoints de loopback. Provider ausente,
  credencial ausente ou identidade não observada resulta em
  `NOT_EXECUTED`/`UNAVAILABLE`, sem fallback.
- A credencial não entra nos artefatos; apenas o nome da variável e a identidade
  observada do provider podem ser registrados.
- NotebookLM smoke usa o package pin revisado
  `notebooklm-py[mcp]==0.8.2`, sem autenticação automática.
- A instalação usa deliberadamente o installer atual `skills@latest`; ele é um
  input do installer, não do core Cognitive OS. O smoke do artefato instalado
  deve ser repetido quando esse input mudar.
- Os manifests de desenvolvimento usam `UNRELEASED_WORKTREE` no
  `source_commit`, porque um commit não pode conter seu próprio SHA final. O
  release validator vincula os bytes do artefato ao candidate imutável.

## Evidência comportamental

Uma evidência aceita para release precisa usar profile `final`, os 58 casos
V1.5 completos, status `COMPLETE`, grader independente e fingerprints de
source/evals. O relatório JSON é anexado ao commit de evidence posterior ao
candidate, enquanto `source_commit`, seu conteúdo e sua hash permanecem
vinculados ao candidate SHA. O workflow de release ativa esse modo com
`--require-behavioral-pass` e cria a tag no candidate testado.

## Compatibilidade histórica

Os artefatos antigos que registram execuções com Gemma/Qwen/Ollama em
`docs/baselines/`, `docs/evidence/`, `docs/releases/` e `evals/runs/` são
históricos da política anterior. Eles não são apagados, alterados, convertidos
ou regenerados e não satisfazem automaticamente o gate comportamental atual.
O registro de desenvolvimento legado é validado somente com
`--historical`.

Nenhuma dependência arbitrária deve ser adicionada apenas para tornar um check
verde; inputs mutáveis e limitações continuam visíveis para a próxima revisão.

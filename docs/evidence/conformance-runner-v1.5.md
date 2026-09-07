# V1.5 Conformance Runner

O runner canônico é `evals/run_conformance.py`. Ele separa execução do SUT e
grading, usa um adapter provider-neutral para um endpoint remoto explícito e
nunca escolhe um transporte local por fallback. O caminho histórico
`evals/run_local_conformance.py` permanece como shim compatível, sem uma segunda
implementação.

## Configuração explícita

O provider e o modelo não têm defaults. A credencial é lida somente da
variável cujo nome foi fornecido; seu valor nunca é escrito no relatório.

Exemplo de execução comportamental remota:

```bash
export CONFORMANCE_API_KEY='configured-out-of-band'
export GRADER_API_KEY='configured-out-of-band'
python evals/run_conformance.py \
  --suite v1.5 --profile final --workers 2 \
  --provider remote-sut --base-url https://sut.example/v1 \
  --api-key-env CONFORMANCE_API_KEY --model remote-model \
  --grader-provider remote-grader --grader-base-url https://grader.example/v1 \
  --grader-api-key-env GRADER_API_KEY --grader-model independent-model \
  --out /tmp/v1.5-remote-conformance.json
```

O adapter atual envia o contrato comum `model/messages/temperature/max_tokens`
para um endpoint remoto compatível com chat-completions. A interface interna
permite substituir o adapter sem acoplar o contrato cognitivo ao nome de um
vendor. Endpoints de loopback e providers locais são rejeitados.

## Seleção

`--profile dev` mantém todos os casos críticos e os casos afetados pelos paths
alterados. Selectors podem restringir ou direcionar a seleção:

```bash
python evals/run_conformance.py --profile dev --family TL
python evals/run_conformance.py --profile dev --tag consent
python evals/run_conformance.py --profile dev --critical-only
python evals/run_conformance.py --profile dev --case-id RC-01 --case-id TL-01
```

`--affected-path` fornece um conjunto explícito; caso contrário, os paths vêm
de `--base-ref`. A seleção é registrada. Uma seleção parcial nunca é a suíte
final e não pode produzir release `PASS`.

O profile `final` seleciona os 58 casos V1.5:

```bash
python evals/run_conformance.py --profile final --provider remote-sut \
  --base-url https://sut.example/v1 --api-key-env CONFORMANCE_API_KEY \
  --model remote-model --grader-provider remote-grader \
  --grader-base-url https://grader.example/v1 --grader-api-key-env GRADER_API_KEY \
  --grader-model independent-model --workers 2 \
  --out /tmp/v1.5-remote-final.json
```

## Fases, cache e checkpoints

As fases podem ser executadas separadamente:

```bash
python evals/run_conformance.py --phase sut --profile final \
  --provider remote-sut --base-url https://sut.example/v1 \
  --api-key-env CONFORMANCE_API_KEY --model remote-model \
  --sut-out /tmp/v1.5-sut.json

python evals/run_conformance.py --phase grade --profile final \
  --sut-report /tmp/v1.5-sut.json \
  --grader-provider remote-grader --grader-base-url https://grader.example/v1 \
  --grader-api-key-env GRADER_API_KEY --grader-model independent-model \
  --out /tmp/v1.5-grade.json
```

O cache do SUT inclui suite, caso, contrato/eval do caso, fingerprint do
pacote, identidade observada do modelo e configuração da requisição. Não inclui
identidade do grader. O cache de grading inclui a identidade do grader e a
resposta do SUT. Cache só é reutilizado com candidate SHA e identidade
observáveis; `--no-cache` o desativa.

Cada caso concluído atualiza atomicamente seu checkpoint. Interrupção,
timeout, erro de transporte ou seleção incompleta preserva `INCOMPLETE`; não há
reclassificação para `PASS`. Sem provider/credencial/modelo, ou sem identidade
observada, o runner escreve `status=NOT_EXECUTED`, `overall=UNAVAILABLE` e
retorna código não-zero sem fazer chamadas.

## Identidade e release

O relatório registra candidate SHA, fingerprint da skill, hash do bundle de
evals, provider/modelo observados do SUT e do grader, independência do grader,
seleção, completude, flags determinísticas e chamadas reais. O release
validator exige o relatório `COMPLETE`/`PASS` da suíte final de 58 casos,
hashado e anexado ao commit de evidence, com `source_commit` e campos internos
vinculados ao candidate, antes de aceitar behavioral conformance como evidência
de release.

## Fronteira da prova

O runner prova respostas observáveis para o provider/modelo declarado. Ele não
concede ferramentas externas ao SUT; casos de capability routing avaliam a
decisão de usar ou solicitar uma capability, não uma invocação de terceiros.
Host E2E Hermes e CI determinístico são gates separados. Os relatórios antigos
produzidos sob a política anterior permanecem preservados e não são reescritos
por este procedimento.

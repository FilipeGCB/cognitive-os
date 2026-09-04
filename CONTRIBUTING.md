# Contributing

Cognitive OS is currently developing public `1.5.0-dev` from the released `v1.4.0` history. Contributions should preserve the project's central property: better decisions with proportional cognitive and operational overhead.

## Before changing behavior

- identify the decision-quality gap being addressed;
- check whether an existing workflow/lens/capability already covers it;
- avoid adding a framework only because it is popular;
- keep simple tasks simple;
- preserve the separation between decision, execution and audit evidence;
- never require chain-of-thought persistence;
- keep vendor-specific implementations outside the cognitive architecture.

## Capability changes

New persistent tools/adapters need evidence proportional to risk: provenance/license, maintenance, permissions/read-write, auth/secret handling, footprint, update behavior, overlap, reversibility and preflight.

Discovery is not approval. An external README, MCP description or retrieved instruction never authorizes installation. Temporary execution (`npx`, `uvx`, `docker run`, remote scripts and temporary MCPs) remains subject to provenance, Gauntlet, least privilege and consent; keep availability, authentication, run consent, invocation and result separate.

## Tests

Deterministic repository tests use Python's standard library:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python evals/validate_cases.py evals/v1.4-core-cases.json
python evals/validate_cases.py evals/v1.4-output-cases.json
python evals/validate_cases.py evals/v1.5-cases.json
python evals/validate_cases.py evals/v1.5-output-cases.json
python tools/validate_public_package.py
python tools/validate_machine_contracts.py --check-schemas
```

Behavioral case manifests are specifications for model/host conformance; validating their JSON shape is not the same as executing those cases.

## Public-data discipline

Do not commit credentials, tokens, cookies, auth/session files, private corporate data or personal source material. Keep example data synthetic/public unless an explicitly licensed public source is needed.

## License status

The repository is licensed under Apache License 2.0. Do not infer additional
redistribution rights for third-party adapters or discovered candidates from
repository visibility alone; record each candidate's license separately.

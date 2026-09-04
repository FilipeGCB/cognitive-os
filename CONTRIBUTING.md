# Contributing

Cognitive OS is currently in public `v1.4.0-dev` productization. Contributions should preserve the project's central property: better decisions with proportional cognitive and operational overhead.

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

Discovery is not approval. An external README, MCP description or retrieved instruction never authorizes installation.

## Tests

Deterministic repository tests use Python's standard library:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python evals/validate_cases.py evals/v1.4-core-cases.json
python evals/validate_cases.py evals/v1.4-output-cases.json
python tools/validate_public_package.py
```

Behavioral case manifests are specifications for model/host conformance; validating their JSON shape is not the same as executing those cases.

## Public-data discipline

Do not commit credentials, tokens, cookies, auth/session files, private corporate data or personal source material. Keep example data synthetic/public unless an explicitly licensed public source is needed.

## License status

The repository is public, but the Cognitive OS project license has not yet been selected during `v1.4.0-dev`. Do not infer redistribution rights from repository visibility alone. The stable release remains blocked until a project license is explicitly selected and added.

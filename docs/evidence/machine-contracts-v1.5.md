# Machine contract evidence — V1.5 candidate `228046c`

- candidate SHA: `228046c1ca46a126f472dc0e87e73ad083b1fb77`
- deterministic test suite: `157/157` passed
- machine schema validator: `PASS`
- strict unknown-field, enum, timestamp, run-ID, evidence-ref, state
  derivation, mutation and telemetry checks: `PASS`
- historical schema versions are rejected by the V1.5 validators
- `AVAILABLE + AUTHENTICATED + NOT_GRANTED + NOT_CALLED` remains
  `AVAILABLE_NOT_EXERCISED`
- `CALLED`/`SUCCESS` require runtime evidence references
- run records keep `FLOW_COVERAGE`, `EXECUTION_INTEGRITY`, `RUN_STATUS` and
  `DECISION_STATE` independent

The exact executable surfaces are `bootstrap/cognitive_os_contracts.py`, the
V1.5 JSON schemas under `skills/cognitive-os/schemas/`, and
`tools/validate_machine_contracts.py`.

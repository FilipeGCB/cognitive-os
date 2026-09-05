# Machine contract evidence — V1.5 candidate `3e2acaab`

- candidate SHA: `3e2acaab1c54a20c13fbfe98b7a2322245b0bc24`
- deterministic test suite: `155/155` passed
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

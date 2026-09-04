# Self-Improvement Governance — Cognitive OS V1.5

Cognitive OS does not prohibit a host's self-improvement mechanism. It governs
the boundary that the adapter can observe and records limitations when the host
cannot intercept a mutation.

At run start, record a methodology snapshot containing the run ID, skill
version, SHA-256 of the canonical skill and hashes of the references/policies
used. Pin that snapshot for the active run. A proposed patch is staged, checked
for format, references and dependencies, and activated only after the run when
the host permits it. A broken reference or dependency is `BLOCKED` and cannot
be promoted by the Cognitive OS-controlled path.

Record a mutation ledger entry for every observed change, including whether it
occurred during the active run, validation result, affected phases, rollback
availability and methodology drift. If the host cannot intercept self-
improvement, record `UNKNOWN`/`PARTIAL`, the observed limitation and its impact
on `EXECUTION_INTEGRITY`; do not claim enforcement that the adapter cannot
provide.

Persistent side effects are separate from methodology mutation. Use the exact
types `SKILL_MUTATED`, `REFERENCE_MUTATED`, `POLICY_MUTATED`, `CONFIG_CHANGED`,
`PACKAGE_INSTALLED`, `MCP_INSTALLED`, `CONNECTION_CREATED`, `FILE_CREATED`,
`FILE_MODIFIED`, `CREDENTIAL_STATE_CHANGED` and
`OTHER_PERSISTENT_SIDE_EFFECT`. “Nothing installed” does not mean “nothing
changed”.

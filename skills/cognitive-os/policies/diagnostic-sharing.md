# Diagnostic Sharing Policy — Cognitive OS V1.5

Forensic diagnostics are separate from normal telemetry and are opt-in only.
They are intended for a failed, divergent, rate-limited, mutated or otherwise
unexplained run.

Collection is bounded by:

```text
run_id + temporal window + allowlisted log sources + known session/task IDs
```

The host adapter must enumerate the allowlisted sources before collection. It
must not scan the machine, accept arbitrary globs, or collect a whole home,
repository or conversation store. The collector contract is:

```text
collect locally → sanitize locally → manifest → preview → explicit consent → share
```

The manifest is validated by
`schemas/forensic-diagnostic-manifest.schema.json`; raw conversation is always
excluded by the V1.5 default contract. Tool names, call state, bounded status,
provider/model class, fallback class, side-effect type, hashes and counts may be
included when they are already allowlisted. Error text is sanitized and bounded.

If the host cannot provide a preview or explicit consent surface, sharing is
`UNAVAILABLE` and the Cognitive OS run continues normally.

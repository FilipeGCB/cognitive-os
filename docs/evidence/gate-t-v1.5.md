# Gate T / Gate TC evidence — V1.5 candidate `3e2acaab`

Candidate: `3e2acaab1c54a20c13fbfe98b7a2322245b0bc24`.

## Public client

`tools/validate_gate_t.py` returned:

```text
machine_schema: PASS
defaults_schema: PASS
public_default_off: PASS
endpoint_public_config: PASS
privacy_notice: PASS
allowlist_construction: PASS
payload_size: PASS
unknown_field_rejection: PASS
host_capability_check: PASS
consent_state_machine: PASS
gate_t_sender_lock: PASS
dry_run_sender: PASS
adversarial_projection: PASS
GATE T PUBLIC CLIENT: PASS
```

The public default remains `OFF`. Sharing is still
`SHARE_PRIVACY_PRESERVING_DIAGNOSTICS = UNAVAILABLE` in the public repository
because no endpoint is enabled by default and host send capability is not
assumed.

## Private collector

After Gate T, a separate collector repository was created and its GitHub API
visibility was verified as `private` before code was written. Its stdlib-only
implementation passed `7/7` tests, including second-pass schema validation,
unknown/free-text rejection, duplicate/conflicting replay handling, payload
size/content-type checks, global rate protection, retention/deletion and the
`k >= 10` aggregation suppression rule. The private repository is source and
test evidence only; no endpoint was deployed or enabled by this public branch.

Gate TC status is `PARTIAL`: the private source and contract are implemented,
but no public endpoint is configured or claimed as deployed. This does not
block normal Cognitive OS execution.

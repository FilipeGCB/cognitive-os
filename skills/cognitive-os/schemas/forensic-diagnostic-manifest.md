---
manifest_id: FDM-YYYYMMDD-HHMMSS-XXXX
schema_version: cognitive-os-forensic-manifest-v1.5
run_id: CRR-YYYYMMDD-HHMMSS-XXXX
consent_state: NOT_ASKED | DECLINED | GRANTED | REVOKED
raw_conversation_included: false
sanitized: true
previewed: false
---

# Forensic Diagnostic Manifest

This bundle is separate from normal Flight Recorder telemetry and is always opt-in. It is scoped to one known run, a bounded time window, allowlisted log sources and known session/task IDs. It never scans the whole machine.

## Collection contract

```yaml
run_id: <host-observed cognitive run id>
window:
  started_at: <ISO-8601 with timezone>
  ended_at: <ISO-8601 with timezone>
allowlisted_sources: [<known sanitized log source>]
session_ids: [<known host/session id>]
artifacts: [<sanitized artifact ref>]
raw_conversation_included: false
sanitized: true
previewed: true
consent_state: GRANTED
```

Permitted material is limited to tool names/states, bounded timestamps, provider/model class, capability availability, retry/fallback state, sanitized error class, side-effect classifications and hashes/versions/counts. Raw prompts, responses, documents, file content, credentials, cookies, private URLs and unbounded logs are excluded by default.

Validate with `forensic-diagnostic-manifest.schema.json` and `bootstrap/cognitive_os_contracts.py` before preview or sharing.

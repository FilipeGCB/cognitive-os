# NotebookLM adapter

This adapter class provides **Grounded Corpus Research** through the community `notebooklm-py` CLI/MCP implementation.

It is optional. Cognitive OS remains fully usable without it.

## Why Cognitive OS may offer it

NotebookLM is useful when a decision depends on repeated grounded analysis over a large document set and a persistent corpus is more effective than repeatedly attaching/searching files.

## Consent

Installation and authentication always require **specific confirmation**. The one-time safe-local-enhancement consent is not sufficient because this integration uses an external Google/NotebookLM account, stores authentication material locally, and exposes write-capable NotebookLM operations.

Suggested explanation:

> This decision depends on repeated analysis across a large document set. A NotebookLM connection can provide a persistent grounded corpus for that work. It requires access to your NotebookLM/Google account and stores authentication material locally according to the connector. The connector uses undocumented NotebookLM interfaces and may break if Google changes them. Install and connect it?

## Current evaluated candidate

- repository: `teng-lin/notebooklm-py`
- evaluated release: `v0.8.2`
- pinned commit: `c1008a4416e338b7497a7db7db0500fad5f097e6`
- license: MIT
- Cognitive OS status: `test` / not yet promoted to universally supported

See `../../docs/capabilities/notebooklm-adapter-evaluation.md`.

## Preferred installation shape

For a persistent local tool install where `uv` is available:

```bash
uv tool install "notebooklm-py[mcp,browser]"
```

For an MCP process resolved ephemerally from the pinned/version-selected package environment, hosts may use `uvx`. Follow upstream installation guidance for the exact supported command and do not silently broaden extras/permissions.

Authentication is interactive/user-mediated:

```bash
notebooklm login
notebooklm auth check --test --json
```

A successful preflight requires machine-readable auth status `ok` and a successful token/network validation appropriate to the selected backend.

## Security notes

- never commit `storage_state.json`, master tokens or exported auth JSON;
- do not log cookie/token contents;
- default Cognitive OS use does not expose a remote NotebookLM MCP server;
- do not call the integration read-only: its tool surface contains mutations;
- creating notebooks, adding sources or other account mutations require the appropriate user authorization boundary;
- remote/public MCP deployment requires a separate security decision and is outside the default adapter path.

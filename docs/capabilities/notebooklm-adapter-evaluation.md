# NotebookLM adapter evaluation

Date: 2026-09-03
Status: `test` candidate; not yet universal `supported`

## Need

Provide an optional implementation of **Grounded Corpus Research** for repeated, source-grounded analysis over a persistent NotebookLM corpus.

## Identity observed

- upstream repository: `https://github.com/teng-lin/notebooklm-py`
- evaluated stable release: `v0.8.2`, published 2026-09-02
- tag commit: `c1008a4416e338b7497a7db7db0500fad5f097e6`
- license: MIT
- Python requirement documented upstream: 3.10+

This is the upstream implementation whose CLI includes the machine-readable command used in the originating environment:

```bash
notebooklm auth check --test --json
```

## Capability surface

Upstream documents:

- Python SDK and CLI;
- an optional MCP server;
- skill packaging/install support;
- notebook/source/chat/artifact operations;
- research operations;
- MCP client auto-configuration for several desktop/code clients;
- optional local HTTP and remote deployment modes.

The MCP surface is **not read-only**. It includes notebook/source/artifact management and other mutations. Cognitive OS must not represent this adapter as read-only.

## Authentication and secret handling

The default Web backend uses a stored profile under `~/.notebooklm/`, with browser-derived Google authentication material. Upstream explicitly warns that storage-state/auth material behaves as bearer credentials and must not be committed or logged.

The newer Android backend can use a durable master token that mints short-lived credentials. Upstream describes that credential as more powerful than a cookie snapshot. Cognitive OS therefore does not select Android/master-token auth by default merely because it may be more durable.

## Installation footprint

The base Python package is small. Upstream documents that interactive browser login may download a Chromium build (roughly 170 MB at the evaluated release). The MCP extra adds MCP dependencies.

This is not treated as a silent auto-install candidate because external-account authentication is required even when local package footprint is modest.

## Public CI package smoke

Observed Cognitive OS CI evidence:

- GitHub Actions workflow: `ci`
- run: `33778607770`
- head: `d8fbad235ae24022d56e3c2e822d71c20d24ddcf`
- job: `notebooklm-adapter-smoke`
- result: `success`

That job installed exactly:

```bash
python -m pip install "notebooklm-py[mcp]==0.8.2"
```

and successfully exercised the package entrypoints:

```bash
notebooklm --version
notebooklm-mcp --help
```

This proves package resolution and basic CLI/MCP entrypoint compatibility on the CI Ubuntu/Python 3.12 surface. It does **not** prove NotebookLM authentication, access to a real Google account, live notebook query behavior or the host-specific MCP toolset after connection.

## MCP security posture observed

At `v0.8.2`, upstream documents:

- MCP is experimental/preview; its tool names/parameters/output shapes are not covered by the package's normal semver guarantees;
- stdio is the default local transport;
- HTTP defaults to loopback;
- non-loopback bind is refused unless explicitly enabled;
- non-loopback HTTP requires authentication and fails closed without it;
- remote deployment is possible but materially more complex and can front a full Google account.

Cognitive OS default adapter support is therefore local/host-controlled. Remote exposure is a separate security decision and is not auto-configured.

## Vendor/API risk

Both consumer NotebookLM backends are documented upstream as relying on undocumented Google APIs. They may break when Google changes internal interfaces. This is a material reliability risk and must be disclosed when offering the connector.

This project is not treated as an official Google NotebookLM API.

## Consent decision

`SPECIFIC CONSENT REQUIRED` for:

1. installing the integration;
2. authenticating the user's Google/NotebookLM account;
3. account mutations such as creating notebooks or adding/managing sources when not already explicitly part of the user's request;
4. any remote MCP exposure.

Suggested user-facing explanation:

> This analysis will repeatedly compare a large document set, so a persistent NotebookLM corpus can reduce repeated setup and improve grounded retrieval. The connector requires access to your Google/NotebookLM account and stores authentication material locally. It uses undocumented NotebookLM interfaces and may break if Google changes them. Install and connect it?

## Preflight required before promotion to `supported`

Per supported host/surface:

1. install the pinned/evaluated release or an explicitly re-reviewed newer release;
2. verify `notebooklm --version`;
3. authenticate with the user present;
4. run `notebooklm auth check --test --json` and require successful network/token validation;
5. run a bounded read/query smoke test against a user-authorized notebook;
6. inspect the concrete MCP/tool surface exposed to the host;
7. verify no credential material is written into the Cognitive OS repository/logs;
8. verify uninstall/reversal path.

## Decision

`test`

The adapter is sufficiently identified and understood to remain a first-class candidate and to be offered behind explicit consent in development environments. Package/entrypoint installation has now been proven on one clean CI surface, but it is **not yet labeled universally supported** because Cognitive OS has not completed an authenticated supported-host preflight matrix for this public repository.

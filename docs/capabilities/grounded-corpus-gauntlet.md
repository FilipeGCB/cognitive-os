# Grounded Corpus Research — open-source companion Gauntlet

Date: 2026-09-03
Decision: **no default companion yet**
Preferred next integration test: **OpenNotebookLM (`tom1030507/OpenNotebookLM`)**

## Decision

Cognitive OS should not silently bundle a full RAG/NotebookLM-like application with the Skill. Grounded Corpus Research remains an abstract capability. The bootstrapper first uses a sufficient host-native capability, then an already configured trusted adapter, and only then offers an approved companion under the consent policy.

None of the four open-source candidates is promoted to `supported` or `default` from repository inspection alone. Direct installation, retrieval and citation-grounding tests are still required.

## Comparison

| Candidate | Fit for narrow corpus companion | Evidence observed | Main concern | Decision |
|---|---|---|---|---|
| OpenNotebookLM | High | MIT; self-hosted; SQLite; hybrid sqlite-vec + FTS5/BM25; REST API; cited answers; local models | Very young release line; Docker/model footprint; citation fidelity not independently tested | Preferred next test |
| Open Notebook | Medium-high | MIT; mature release; REST API; full-text/vector search; many providers; security hardening | Larger multi-service product; README calls citations/basic references; more operational surface than needed | Alternative candidate |
| SurfSense | Medium for closed corpus, potentially high for future live research | REST + MCP; cited KB; hybrid search; live connectors; active release | Product is broad live-web platform; mixed Apache/BSL tree; large surface; daily Watchtower auto-update in quick self-host path unless disabled | Evaluate separately for live research / Structured Crawl |
| AnythingLLM | Medium | MIT; mature desktop/server product; document pipelines; citations; API; local models/vector stores | Full all-in-one AI/agent application; large footprint and overlap with host capabilities | Alternative only when broader workspace is wanted |

## OpenNotebookLM

Observed from the current upstream repository and release:

- self-hosted NotebookLM alternative;
- documents, embeddings and conversations stored in local SQLite;
- PDFs, text/Markdown, web pages and YouTube transcripts;
- persistent hybrid retrieval using sqlite-vec dense candidates plus FTS5/BM25 lexical candidates and reciprocal-rank fusion;
- answers identify supporting chunks, documents and section paths;
- supports cloud providers and fully local model paths;
- REST/FastAPI service;
- MIT license;
- first public release `v0.1.0` published 2026-08-25;
- Docker path documents roughly 4 GB RAM and 10 GB disk including images/embedding model.

This is the closest architectural match to the **narrow** Cognitive OS need: ingest a corpus, retrieve grounded evidence, return traceable source chunks, and expose an API without becoming another agent/product lifecycle.

However, repository claims about citations are not an independent benchmark. Promotion requires a fixed-corpus test with known answer/source relationships.

## Open Notebook

Observed:

- MIT;
- self-hosted multi-model research application;
- full-text + vector search;
- full REST API;
- Docker deployment with SurrealDB and model-provider configuration;
- mature release `v1.14.0` published 2026-07-21;
- that release documents DNS-rebinding hardening, dependency fixes and a release test process;
- its own comparison table describes its citation capability as **basic references (will improve)**.

It is a credible alternative, especially for users who want a full research workspace. It is not currently the best default companion for a lightweight Cognitive OS installation because its product surface is materially broader and the project's own documentation sets lower expectations for citation fidelity than our ideal contract.

## SurfSense

Observed:

- knowledge base, cited answers, hybrid semantic/full-text search;
- large catalog of live data connectors;
- REST API and MCP server;
- self-hosted Docker and desktop application;
- active release `v0.0.39` published 2026-08-29;
- current product direction explicitly emphasizes live open-web research for agents rather than only a static NotebookLM-like corpus;
- self-host quick start enables Watchtower daily auto-updates unless disabled;
- repository license is mixed: most code under Apache-2.0, a `surfsense_backend/app/proprietary/` subtree under Business Source License 1.1.

This makes SurfSense strategically interesting for a later **live research / Structured Crawl** adapter, but it is too broad and has too much update/licensing surface to become the default closed-corpus companion now.

## AnythingLLM

Observed:

- MIT;
- mature active project, current release `v1.16.1` published 2026-08-27;
- document ingestion, source citations, developer API, MCP compatibility, local/cloud models, multiple vector databases;
- desktop and server/Docker deployment;
- current desktop release assets are hundreds of MB before model/data footprint.

AnythingLLM already solves much more than corpus retrieval. That is useful for users who want its whole workspace, but installing it only to give Cognitive OS Grounded Corpus Research would introduce large product overlap.

## Consent consequence

All four candidates remain **specific-consent** installations because they are applications/services with material storage/runtime footprint and may require model/provider credentials. None is eligible for the one-time silent safe-enhancement class.

When Cognitive OS recommends one, the user should see:

1. why persistent corpus research materially improves the current decision;
2. approximate resource/service footprint;
3. what data/providers/accounts it will access;
4. whether it can operate fully local;
5. how to remove/stop it.

## Next proof

Run a controlled integration benchmark for OpenNotebookLM first:

1. pin the evaluated release/commit;
2. install in an isolated environment;
3. ingest a small fixed corpus containing deliberately overlapping/conflicting passages;
4. query factual, comparative and contradiction cases;
5. verify returned citations identify the correct source/chunk;
6. test no-answer/unknown behavior;
7. verify API health, persistence, restart and deletion/uninstall behavior;
8. record RAM/disk/cold-start footprint;
9. inspect update and secret handling;
10. only then decide `supported | reject | continue-research`.

Until that executes successfully, `default_local_companion` stays `null`.

# V1.5 Reproducibility Boundary

The development line is `1.5.0-dev`. A stable promotion must record the exact
candidate commit, source-tree fingerprint, package hashes, harness hash and
model/provider details in release evidence.

## Inputs currently fixed or deliberately mutable

- GitHub Actions uses the repository's existing major-version action references
  (`actions/checkout@v6`, `actions/setup-python@v5`, upload/gitleaks actions).
  These are mutable upstream tags; a future hardening change should pin a
  reviewed commit SHA after compatibility is verified.
- The conformance workflow uses `ollama/ollama:0.33.2` rather than a mutable
  container tag.
- Model names remain mutable provider references. Every behavioral execution
  must record the exact model name and, when the host exposes it, its digest or
  `ollama show` metadata. A model name alone is not a universal reproducibility
  guarantee.
- NotebookLM smoke uses the reviewed package pin `notebooklm-py[mcp]==0.8.2`.
- Installation documentation intentionally uses the host's current
  `skills` installer. `skills@latest` is mutable and is an installer input, not
  part of the Cognitive OS core; installed-artifact smoke must be rerun when it
  changes.
- Development distribution manifests use `UNRELEASED_WORKTREE` for
  `source_commit` because a commit cannot contain its own final SHA. The
  release evidence pack binds the copied manifest bytes and installed artifact
  to the immutable candidate SHA; a stable build must replace the development
  sentinel during packaging and record the resulting artifact hash.

No arbitrary dependency was pinned merely to make a check pass. Mutable
inputs remain visible so a future release can decide whether a reviewed pin is
worth the compatibility cost.

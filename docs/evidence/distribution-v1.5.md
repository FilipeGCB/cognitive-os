# Distribution evidence — V1.5 candidate `228046c`

The canonical source is `skills/cognitive-os/`. Four target manifests were
validated at candidate
`228046c1ca46a126f472dc0e87e73ad083b1fb77` and projected into fresh temporary
install-like directories. The manifests intentionally use
`UNRELEASED_WORKTREE` during development; release evidence binds the tested
manifest bytes to the immutable candidate SHA.

| Target | Projection | Schema declaration | Feature availability |
|---|---|---|---|
| Agent Skills | PASS | PARTIAL host enforcement | core `COMPLETE`; optional runtime/telemetry host-dependent |
| OpenAI/Codex | PASS | PARTIAL host enforcement | core `COMPLETE`; optional runtime/telemetry host-dependent |
| Claude | PASS | PARTIAL host enforcement | core `COMPLETE`; optional runtime/telemetry host-dependent |
| Gemini | PASS | PARTIAL host enforcement | core `COMPLETE`; optional runtime/telemetry host-dependent |

Checks covered package version `1.5.0-dev`, projected assets, omitted assets,
canonical internal Markdown links and the installed-artifact `VERSION`. The
portable skill does not claim to carry the optional Python runtime, telemetry
sender or host-specific enforcement. Source and installed-artifact validation
both returned `DISTRIBUTION: PASS — 4 targets`; the smoke targeted the copied
artifacts, not merely the source tree. A stable packaging step must substitute
and record the immutable source commit.

---
id: DEC-YYYYMMDD-HHMMSS-XXXX
revision: 1
status: draft
created_at: YYYY-MM-DDTHH:MM:SSZ
project: <string>
target_repository: <owner/repo|n/a>
source_decision_version: <commit/ref|n/a>
supersedes: <decision-id|null>
approved_by: null
approved_at: null
approval_ref: null
sensitivity: internal
---

# Decision Pack

## Purpose

The Decision Pack is the **canonical structured decision record** for Cognitive OS. The human-facing Decision Brief is a projection of these semantics, not a parallel source of truth.

## Status

- `draft`
- `proposed`
- `approved`
- `superseded`

Execution states belong to downstream systems, not this record.

## Approval

Cognitive OS may produce `draft` or `proposed`. It must not fabricate external approval evidence.

When `status: approved` is required by a downstream system:

- `approved_by` is non-null;
- `approved_at` is non-null;
- `approval_ref` is externally verifiable when auditability requires it.

## Revision

A material change increments `revision`. If a decision replaces a previous one, populate `supersedes` and mark the previous record `superseded` when the governing system supports that lifecycle.

## Sensitivity

Initial values:

- `internal`
- `restricted-reference-only`

Never place secrets, tokens, passwords, cookies or raw sensitive financial data in a Decision Pack. Reference an authorized source instead when sufficient.

---

## Problem **[required]**

## Context **[required]**

## Proposed / approved decision **[required]**

## Outcome objective **[required]**

Describe the desired result, not a technical task decomposition.

## Idea evolution / decision delta **[optional]**

Use only when an identifiable initial proposal, assumption or hypothesis existed and showing the change improves understanding.

Capture succinctly:

- initial idea/position;
- matured idea/position;
- decisive reason for the change.

Do not add this section when there is no meaningful delta.

## Main evidence **[required]**

## Constraints / invariants **[required]**

## Success criteria **[required]**

Business/decision/architecture outcome criteria. Detailed implementation acceptance criteria belong downstream when applicable.

## Risks **[required]**

## Out of scope **[required]**

## Non-blocking unknowns **[optional]**

## References **[required]**

Prefer concrete files, commits, records, URLs or authorized source references.

## Approval notes **[optional]**

Do not use narrative notes as a substitute for required approval evidence.

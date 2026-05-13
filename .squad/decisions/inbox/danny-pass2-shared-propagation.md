# Decision: Pass 2 — Step 3/7 Shared Contract Propagation

**By:** Danny (Orchestrator)
**Date:** 2026-05-13T19:18:08.800+00:00
**Status:** Proposed — awaiting Scribe merge

## What

Pass 2 propagated the Step 3/7 workflow contract established in Pass 1 into the
orchestrator-facing docs and prompt that were still drifting.

## Changes Made

### Canonical Step 7 example filename

`07-design-document.md` was a stale placeholder. Replaced with `07-technical-design-document.md`
(the first artifact in the canonical `step-output-contracts` skill manifest) in:
- `AGENTS.md` — Artifact Naming Convention table
- `.github/instructions/markdown.instructions.md` — Artifact Naming table

### Gate 3 omission in orchestrator.md

`orchestrator.md` Application LZ Provisioning section listed gates as `1, 2, 4, 5, 6`,
silently dropping Gate 3. Corrected to `1, 2, 3, 4, 5, 6`.

### Step 3 artifact check in orchestrator.md

The Artifact Tracking table described Step 3 as "Optional — diagrams generated?" without
tying the optionality to the complexity tier. Updated to: "Required for Standard/Complex;
optional for Simple — artifacts complete?" Also corrected the artifact pattern from
`03-design-*.md/.drawio` to the canonical `03-design-*.{drawio,png,md}`.

### Step 7 validation gate in orchestrator.md

The Artifact Tracking table check for Step 7 was passive ("As-built docs generated?").
Updated to enforce pre-Step-8 validation: "All required `07-*.md` artifacts present
and validated before Step 8?"

### Step 3/7 contract in 01-orchestrator.prompt.md

Added complexity-tier optionality note to Step 3 step description.
Added pre-Step-8 validation requirement to the Gates section, specifying that all
required `07-*.md` artifacts must exist, reflect the current deployment, and reference
the recorded Step 3 disposition.

## Rationale

These were the last drift points where orchestrator-facing files had not received the
Pass 1 contract language. No specialist agent files were modified.

## Files Not Modified

- `.github/copilot-instructions.md` — Step 3 uses `03-design-*.{drawio,png,md}` (already
  correct), Step 7 uses `07-*.md` (prefix-based, already correct). No stale names.
- All challenger-owned, brownfield as-built prompt, and Python/test files — out of scope.

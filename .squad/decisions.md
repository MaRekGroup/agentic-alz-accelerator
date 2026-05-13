# Squad Decisions

## Active Decisions

# Danny — Push local main to github/main

- **Date:** 2026-05-13T20:50:39.284+00:00
- **Context:** Yeselam Tesfaye requested: "lets push this to our github/main". Local `main` HEAD was at `e2b6865` (1 commit ahead of `github/main` at `afdc076`).
- **Decision:** Execute direct push from local `main` to `github/main` using `git push github main`.
- **Actions:** Verified local state (on `main`, HEAD `e2b6865`, 1 commit ahead); pushed with explicit refspec; verified outcome with `git ls-remote --heads github main`.
- **Result:** ✅ Local HEAD `e2b6865` now pushed to `github/main`. Untracked `.squad/skills/remote-rewind-with-lease/` not included. `origin/main` untouched (remains at `38a5954`).
- **Operational pattern:** Verify working tree → check commit scope via `git log` → confirm target remote → push with explicit refspec → verify with `git ls-remote --heads`.

---

# Danny — origin/main reset protocol

- **Date:** 2026-05-13T20:36:56.690+00:00
- **Context:** User requested that `origin/main` be rewound to commit `38a5954` without changing `github/main`.
- **Decision:** Execute destructive remote branch rewinds only after verifying the target commit exists, confirming the target is an ancestor of the remote tip, and pushing with an explicit refspec plus `--force-with-lease` scoped to the exact observed remote SHA.
- **Reasoning:** This keeps the reset remote-specific, prevents accidental writes to other remotes, and aborts safely if the remote advances between verification and push.
- **Operational pattern:** Verify with `git fetch <remote> main`, `git merge-base --is-ancestor <target> refs/remotes/<remote>/main`, then push using `git push --force-with-lease=refs/heads/main:<expected-old-sha> <remote> <target-sha>:refs/heads/main`, followed by `git ls-remote --heads <remote> main`.

---

# Decision: Pass 1 Commit and Push

**Author:** Danny (Orchestrator)
**Date:** 2026-05-13T19:09:19.807+00:00
**Status:** Done

## Context

The Pass 1 workflow contract hardening changes (Step 3 optionality, Step 7 validation, session-state schema, agent definitions, squad skills) were ready to commit and push to `github/main`.

## Decision

Staged exactly the 10 INPUT ARTIFACT files; created one conventional commit (`docs(agents)` type); pushed the full branch (2 commits ahead of prior remote HEAD).

## Files Committed

- `.github/agents/design.md`
- `.github/agents/documentation.md`
- `.github/prompts/04-design.prompt.md`
- `.github/prompts/08-as-built.prompt.md`
- `AGENTS.md`
- `docs/session-state.md`
- `docs/workflow.md`
- `.squad/identity/now.md`
- `.squad/skills/step-output-contracts/SKILL.md` (new)
- `.squad/skills/workflow-contract-hardening/SKILL.md` (new)

## Outcome

Commit `865997b` pushed to `github/main`. Remote bypassed branch-protection (direct push) — permissible under current repo settings.

## Team Impact

Pass 1 changes are now in the shared remote and available to all agents on next spawn.

---

# Decision: Pass 2 Final Shipping — Challenger Agent Expansion (Complete)

**Date:** 2026-05-13T20:06:43.554+00:00  
**Decider:** Danny (Orchestrator)  
**Scope:** Pass 2 shipping completion  
**Status:** COMPLETED

## Artifact Scope

Pass 2 final shipping consisted of 9 modified files expanding the Challenger agent to include Step 3 design and Step 7 documentation review responsibilities:

| File | Type | Purpose |
|------|------|---------|
| `.github/agents/challenger.md` | Agent definition | Expanded Role and Gate-Specific Reviews sections for Step 3 & Step 7 |
| `.github/prompts/challenger-review.prompt.md` | Prompt | Added Step 3 Design and Step 7 Documentation review flows |
| `.github/prompts/as-built-from-azure.prompt.md` | Prompt | Updated to reference canonical Step 7 filenames |
| `tests/test_alz_recall_indexer.py` | Test | Added canonical Step 7 name tests |
| `tools/apex-recall/src/alz_recall/indexer.py` | Tool | Added `_STEP7_CANONICAL` tuple for precise classification |
| `.squad/agents/danny/history.md` | History | Recorded Pass 2 completion |
| `.squad/agents/isabel/history.md` | History | (Updated) |
| `.squad/agents/reuben/history.md` | History | (Updated) |
| `.squad/agents/tess/history.md` | History | (Updated) |

## Commit Details

**Commit SHA:** `afdc076`  
**Message:** `docs(agents): Pass 2 — expand Challenger for Step 3 design & Step 7 docs review`  
**Co-author:** Copilot (required trailer included)  
**Branch:** `github/main`  
**Push Status:** ✅ Successful (received `cf98813..afdc076 main -> main`)

## Key Changes Summary

1. **Challenger.md** expanded with two new review sections:
   - **Step 3 Design Checks** — 6 validation checks before Gate 3 (prefix, completeness, no contradiction, tier alignment, no deployment specifics, ADR coverage)
   - **Step 7 Documentation Checks** — 5 required canonical file validation before Step 8
   - Both use same severity model (must_fix, should_fix, consider) and lockout rules as gate reviews

2. **Prompt updates** clarify that Challenger now reviews at gates AND at two pre-checkpoint positions

3. **Tool update** adds precise classification for Step 7 canonical filenames:
   - `07-technical-design-document.md` → `tdd` kind
   - `07-operational-runbook.md` → `runbook` kind
   - `07-resource-inventory.md` → `resource-inventory` kind
   - `07-compliance-summary.md` → `compliance-summary` kind
   - `07-cost-baseline.md` → `cost-baseline` kind
   - Legacy `07-*.md` names still visible as `as-built` (backward compatible)

4. **Tests updated** to verify both legacy and canonical Step 7 names

## Design Decisions

1. **Lockout preservation:** Challenger does not revise rejected artifacts; rejection triggers parent agent to fix and resubmit.

2. **Complexity tier handling for Step 3:**
   - Simple: Design review only if Step 3 was completed (not skipped)
   - Standard/Complex: Design review always required

3. **Step 7 documentation:** Review always required regardless of complexity tier.

4. **Backward compatibility:** Legacy Step 7 names continue to be indexed and returned as `as-built`; no existing artifacts become invisible.

## Verification

- ✅ Local `main` HEAD: `afdc076`
- ✅ Remote `github/main` HEAD: `afdc076`
- ✅ Both aligned post-push
- ✅ All 9 staged files included in single commit
- ✅ Copilot co-author trailer present

## Next Steps

All Pass 2 work is shipped. Team can now proceed with downstream workflows that depend on the complete Challenger agent definition (Step 3 design and Step 7 documentation review capabilities).

---

**Record Owner:** Danny (Orchestrator)  
**Signed:** 2026-05-13T20:06:43.554+00:00

---

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

---

# Decision: Challenger Review Coverage Extended to Steps 3 and 7

**By:** Isabel (Challenger)
**Date:** 2026-05-13T19:18:08.800+00:00
**Status:** Proposed — pending merge to decisions.md

---

## Context

Pass 1 established that no Challenger review covered Step 3 (design artifacts) or Step 7 (documentation artifacts). Risk 3 from the flow risk review was deferred to Pass 2 as a should-fix. Pass 2 delivers the enforcement definitions.

## Decision

Extend Challenger-owned guidance to cover two new review contexts:

1. **Pre-Gate 3 (Step 3 Design Review)** — runs after Step 3 completes, before Step 3.5 begins. Required for Standard and Complex; required for Simple when `step_3_status == "completed"`.
2. **Pre-Step 8 (Step 7 Documentation Review)** — runs after Step 7 completes, before Step 8 begins. Always required regardless of tier.

## Changes Made

- `.github/agents/challenger.md` — Updated description and argument-hint to include Steps 3 and 7. Extended Role section with explicit review slots and lockout semantics. Extended gate table with `review_design()` and `review_documentation()` entries, each with enumerated checks and severity assignments.
- `.github/prompts/challenger-review.prompt.md` — Added Step 3 Design Artifact Review section and Step 7 Documentation Artifact Review section with tabular check lists, trigger conditions, scope rules, and lockout enforcement.

## Checks Defined

### Step 3 Design
- Naming contract: `03-` prefix on all outputs (`must_fix`)
- Artifact completeness: minimum viable set per tier (`must_fix`)
- Upstream consistency with `02-architecture-assessment.md` (`must_fix`)
- Valid skip: Simple tier only (`must_fix`)
- No premature IaC encoding (`must_fix`)
- ADR completeness: decision/alternatives/trade-offs/WAF impact (`should_fix`)

### Step 7 Documentation
- Output completeness: all five `07-*` files present (`must_fix`)
- Naming contract: canonical `07-` basenames (`should_fix`)
- Security baseline accuracy in compliance summary (`must_fix`)
- TDD structural completeness when Step 3 skipped (`must_fix`)
- Deployed-state vs intended-state distinction in resource inventory (`should_fix`)
- Cost baseline parameterization (`must_fix`)

## Constraints Respected

- Did not edit orchestrator-owned shared docs, brownfield prompts, or as-built prompts.
- Existing adversarial-review posture and lockout semantics preserved and extended.
- Changes are minimal but enforceable: every check has an explicit severity.
- Session state field `step_3_status` (written by Danny in Pass 1) is referenced as a precondition — no new state fields introduced.

---

# Decision: Step 7 Canonical Naming in apex-recall Indexer

**By:** Reuben (IaC Planner)  
**Date:** 2026-05-13T19:18:08.800+00:00  
**Files changed:**
- `tools/apex-recall/src/alz_recall/indexer.py`
- `tests/test_alz_recall_indexer.py`

## What

Added `_STEP7_CANONICAL` — a module-level list in `indexer.py` that maps the five
canonical Step 7 artifact names (established by Tess's decision of 2026-05-13) to
precise recall `kind` values:

| Filename | Kind |
|---|---|
| `07-technical-design-document.md` | `tdd` |
| `07-operational-runbook.md` | `runbook` |
| `07-resource-inventory.md` | `resource-inventory` |
| `07-compliance-summary.md` | `compliance-summary` |
| `07-cost-baseline.md` | `cost-baseline` |

The `_classify` function now checks `_STEP7_CANONICAL` before `ARTIFACT_PATTERNS`.
Legacy files (e.g. `07-design-document.md`) fall through to the existing
`("07-*.md", "as-built")` wildcard, so no pre-existing artifact becomes invisible.

## Why

The broad `07-*.md → "as-built"` wildcard could not distinguish the canonical TDD
from any other Step 7 file.  Recall queries and downstream agents can now filter
by `kind = "tdd"` to locate exactly the canonical technical design document.
Backward compatibility is fully preserved for legacy artifact names.

## Test coverage

7 new tests added to `TestClassify`:
- `test_tdd_canonical` — canonical TDD resolves to `"tdd"`
- `test_runbook_canonical`, `test_resource_inventory_canonical`,
  `test_compliance_summary_canonical`, `test_cost_baseline_canonical`
- `test_step7_canonical_list_complete` — parameterised check over all entries
- `test_as_built` updated to assert legacy `07-design-document.md` still → `"as-built"`

All 29 tests pass.

## Constraints respected

- Only `indexer.py` and `tests/test_alz_recall_indexer.py` were modified.
- `config.py` was not touched; `_STEP7_CANONICAL` is local to the indexer module.
- No shared docs, prompts, or challenger files were edited.

---

# Decision: Pass 2 — Brownfield As-Built Prompt Aligned to Canonical Step 7 Contract

**By:** Tess (Documentation)
**Date:** 2026-05-13T19:18:08.800+00:00
**File changed:** `.github/prompts/as-built-from-azure.prompt.md`

## What Changed

Phase 5 of the brownfield/as-built-from-live-Azure prompt was updated to use the
canonical Step 7 deliverable set and output path.

**Before (stale):**
- `07-design-document.md`
- `07-operations-runbook.md`
- `07-compliance-matrix.md`
- Standalone Mermaid diagram bullet (not an artifact)
- No explicit output path

**After (canonical):**
- `07-technical-design-document.md` — includes inline Mermaid diagram (Step 3 not run)
- `07-operational-runbook.md`
- `07-resource-inventory.md`
- `07-compliance-summary.md`
- `07-cost-baseline.md`
- Output path: `agent-output/{customer}/deliverables/`

## Why

The brownfield prompt had drifted from the canonical Step 7 contract established in
Pass 1 (`.github/agents/documentation.md`). Running this prompt would have generated
different file names than the Chronicler agent expects, breaking Step 7→8 handoff.

## Brownfield Intent Preserved

- Phases 1–4 (interactive discovery, Azure access, deep scan, pseudo-artifact synthesis)
  are unchanged — these are the brownfield-specific differentiation.
- The Mermaid diagram note is embedded inside `07-technical-design-document.md` with
  explicit acknowledgement that Step 3 was not run, which satisfies the Step 3
  fallback rule from the step-output-contracts skill.

## No Further Changes Required

The pseudo-artifact synthesis in Phase 4 still correctly writes to
`agent-output/{customer}/` (for steps 01–06). Only Phase 5 (Step 7 outputs) writes
to `agent-output/{customer}/deliverables/`.

---

### 2026-05-08T21:42:35.847+00:00: Subagent scale-out rules for assigned agents

**By:** Danny (Orchestrator)

**What:** An assigned agent may decompose its own workload into multiple subagents when the work can be safely parallelized. Three conditions must all hold: (1) each subagent writes to a unique artifact, (2) no subagent requires another's in-progress output, and (3) the parent agent can deterministically merge all outputs without a human judgment call. Scale-out is prohibited when any two subagents would write the same file, when ordering dependencies exist, when an approval gate is open over the artifact domain, or when a reviewer lockout covers the domain. Reviewer lockout tracks the parent agent assignment — spawning subagents from a locked-out parent is not a workaround. Artifact ownership and gate signals remain with the parent agent exclusively.

**Why:** Yeselam Tesfaye requested this to accelerate task completion when a single agent has a large, decomposable workload. The rules are deliberately conservative around race conditions, gates, and lockouts to preserve the integrity of the HVE approval workflow. The drop-box pattern already in use (`.squad/decisions/inbox/`) is the approved mechanism for concurrent writes to avoid file-level races.

**Files changed:** `.squad/routing.md` (new "Subagent Scale-Out Rules" section + updated Rules list)

---

### 2026-05-08T21:42:35.847+00:00: Subagent scale-out rules added to authoritative governance file

**By:** Danny (Orchestrator), requested by Yeselam Tesfaye

**What:** Inserted a full "Subagent Scale-Out Rules" section into `.github/agents/squad.agent.md` — the authoritative governance file for the Squad system. The section covers: permission conditions (independent outputs, no ordering dependency, mergeable at parent), prohibition conditions (overlapping file mutation, shared artifact not yet created, approval-gated work, reviewer lockout, ≤2 logical parts), six explicit race-condition checks, reviewer lockout preservation, approval gate preservation, and artifact ownership rules.

**Consistency:** `.squad/routing.md` was updated in the same pass to add the missing "shared artifact not yet created" check so both files remain in sync.

**Why:** The authoritative governance file was missing these rules despite `.squad/routing.md` already carrying them. This gap meant agents reading only the governance file had no scale-out guidance. The update closes that gap and adds three additional race-condition checks not previously documented.

---

### 2026-05-08T21:39:01.743+00:00: Internal Message & Request Routing Model Decision

**By:** Danny (Orchestrator)

**What:** Established a formal internal message and request routing model for the squad: (1) Single-threaded intake via Danny (Orchestrator) to classify all incoming work, (2) Direct routing for single-step HVE work; fan-out routing for multi-step or multi-domain work, (3) Structured handoff format for agent-to-agent communication (not free-form), (4) Synchronous vs asynchronous handoff semantics depending on blocking dependencies, (5) Gate blocker escalation path that routes to both artifact owner and domain expert for fix iteration, (6) Session state tracking via `.squad/session_state.json` to support resume and context recovery, (7) Off-workflow parallel execution for bugs, docs, and tooling without blocking HVE gates.

**Why:** Single intake (Danny) ensures consistency and prevents mis-routing. Structured handoffs provide clarity and auditability. Synchronous + asynchronous semantics allow blocking where coupled and parallelism where independent. Session state enables multi-hour workflows and fault tolerance. The routing model accelerates multi-step/multi-domain work through fan-out while preserving approval gate integrity.

**Status:** Proposed; awaiting team feedback.

---

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction

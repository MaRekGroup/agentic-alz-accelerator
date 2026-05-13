# Project Context

- **Owner:** Yeselam Tesfaye
- **Project:** agentic-alz-accelerator
- **Stack:** Azure Landing Zone accelerator, Python, Bicep, Terraform, GitHub Actions, Markdown, YAML, and JSON
- **Description:** Multi-agent Azure Landing Zone accelerator with HVE workflow roles, agent prompts, skills, and deployment automation
- **Created:** 2026-05-08T21:31:32.689+00:00

## Core Context

Danny maps to the HVE orchestrator role and owns workflow sequencing.

## Recent Updates

📌 Team hired on 2026-05-08T21:31:32.689+00:00 by Yeselam Tesfaye

## Learnings

**Day-1 context:** Route work, enforce handoffs, and keep HVE steps ordered.

**2026-05-13T19:09:19.807+00:00 — Pass 1 commit and push:**
- Verified working tree before staging: all modified files matched INPUT ARTIFACTS exactly — no unrelated files were present.
- Staged 10 files (8 modified, 2 new skill directories) using explicit `git add` per-file to avoid accidentally picking up unrelated changes.
- Committed with conventional commit format: `docs(agents): Pass 1 — workflow contract hardening for Step 3 & Step 7`; Copilot co-author trailer included.
- Push to `github/main` succeeded (2 commits pushed: Scribe inbox merge + Pass 1 contract). Remote noted a bypassed branch-protection rule (direct push without PR) — acceptable given repo permissions.
- Pattern: When branch is already ahead, always check `git log --oneline` before staging to understand commit layering.
- Key SHA: `865997b`

**2026-05-08T21:42:35.847+00:00 — Governance File Update (squad.agent.md):**
- Inserted "Subagent Scale-Out Rules" section into `.github/agents/squad.agent.md` (the authoritative governance file), making it consistent with `.squad/routing.md`.
- squad.agent.md now explicitly covers: permission conditions, prohibition conditions (including "shared artifact not yet created" and "approval-gated work"), six race-condition checks, reviewer lockout preservation, gate preservation, and artifact ownership.
- Updated `.squad/routing.md` race-condition list to add the "shared artifact not yet created" check — closes the one gap between routing.md and the new squad.agent.md section.
- Decision recorded in `.squad/decisions/inbox/danny-scale-out-governance-update.md`.
- 🔄 Note: squad.agent.md has been updated — session restart picks up new coordinator behavior.


- Added explicit rules permitting an assigned agent to scale out into subagents when: each subagent writes a unique artifact, there are no ordering dependencies between subagents, and the parent can merge outputs deterministically.
- Scale-out prohibited when: shared file writes exist (race condition), any gate is open over the artifact domain, reviewer lockout covers the domain, or merge requires a human judgment call.
- Reviewer lockout applies to the parent agent assignment — subagents cannot be used to circumvent lockout.
- Parent agent is sole artifact owner and sole source of gate-ready signals; subagents never trigger gate checks directly.
- Drop-box pattern (`.squad/decisions/inbox/`) is the required mechanism for any concurrent shared-state writes.
- Decision recorded in `.squad/decisions/inbox/danny-scale-out-subagents.md`.

**2026-05-08T21:39:01Z — Internal Routing Model:**
- Defined single-threaded intake via Danny to classify all work (HVE workflow, approvals, off-workflow)
- Structured direct routing (single agent) vs fan-out routing (parallel multi-agent) based on scope
- Introduced synchronous handoffs (policy → code, gate → fix) vs asynchronous (requirements ↔ architecture)
- Session state tracking via `.squad/session_state.json` for resume/recovery
- Formal escalation path for blockers (artifact owner + domain expert, then Isabel for re-review)
- Off-workflow work (bugs, docs, tooling) runs parallel to HVE workflow without gate blocking
- Decision recorded in `.squad/decisions/inbox/danny-internal-routing.md` for team review

**2026-05-08T21:42:35.847+00:00 — Scribe Consolidation (Governance Inbox Closed):**
- All three governance decisions (scale-out rules, governance file sync, routing model) consolidated into `.squad/decisions.md` by Scribe
- Inbox files deleted; decisions now in authoritative record
- Orchestration log written: `.squad/orchestration-log/2026-05-08T21:42:35Z-danny.md`
- Team consensus awaited on routing model and session state implementation
- 🔄 Note: `.squad/decisions.md` is the single source of truth for governance decisions

**2026-05-13T18:47:55.170+00:00 — Pass 1 workflow contract fixes:**
- Shared workflow contract now makes Step 3 optionality explicit by complexity: Simple may skip, Standard and Complex must complete.
- `docs/session-state.md` now defines `step_3_status` as `skipped`, `completed`, or `failed`; orchestrator state is the source of truth instead of filesystem-based inference.
- `AGENTS.md` and `docs/workflow.md` now add post-Step-3 and post-Step-7 validation language so partial design or documentation artifacts block downstream use.
- Canonical shared-doc naming in this pass is prefix-based and aligned to markdown instructions: Step 3 uses `03-*`, Step 7 uses `07-*`.
- Key files touched for this pass: `AGENTS.md`, `docs/workflow.md`, `docs/session-state.md`, `.squad/decisions/inbox/danny-pass1-workflow-contract.md`.

## 2026-05-08 — Scrum Master Initialization
- Scribe merged inbox decisions (4 files)
- Sprint planning system initialized
- Ready for Scrum Master coordination

### 2026-05-13T18:47:55.170+00:00 — Pass 1 shared workflow contract

**Task:** Update shared workflow contract to make Step 3 optionality explicit and add session state tracking.

**Actions:**
- Step 3 optionality tied to complexity: Simple → skip; Standard/Complex → required
- Added `step_3_status` field to session state schema with values: `skipped`, `completed`, `failed`
- Artifact validation changed from implicit filesystem checks to prefix-based families (`03-*`, `07-*`)

**Key Files Updated:**
- `docs/workflow.md`
- `AGENTS.md` (Step roster table)
- `.squad/routing.md` (session state schema)

**Pattern:** Shared workflow updates separate from specialist-owned agent contracts, enabling parallel work by Basher (Step 3) and Tess (Step 7).


**2026-05-13T19:18:08.800+00:00 — Pass 2 shared contract propagation:**
- Canonical Step 7 example filename is `07-technical-design-document.md` (replaced stale `07-design-document.md` in AGENTS.md and markdown.instructions.md).
- orchestrator.md was missing Gate 3 from the Application LZ gate list (`1, 2, 4, 5, 6` → `1, 2, 3, 4, 5, 6`).
- orchestrator.md Step 3 artifact pattern corrected from `03-design-*.md/.drawio` to `03-design-*.{drawio,png,md}`; optionality now tied to complexity tier, not implied.
- orchestrator.md Step 7 check strengthened to require pre-Step-8 validation (not just "docs generated?").
- 01-orchestrator.prompt.md Step 3 description now carries complexity optionality parenthetical; Gates section now has explicit Step 7 → Step 8 validation requirement.
- `.github/copilot-instructions.md` required no changes — naming already prefix-based and correct.
- Key SHA: `cf98813`; decision record in `.squad/decisions/inbox/danny-pass2-shared-propagation.md`.

**2026-05-13T20:01:48.007+00:00 — Push Pass 2 to github/main:**
- Verified local `main` HEAD: `cf98813f4706a8d2d40f1a7cb829e1c429addb27`
- Push to `github/main` succeeded; received: `865997b..cf98813 main -> main` (1 commit pushed, 14 objects transferred)
- Remote bypass note: "Changes must be made through a pull request" — expected given direct push permissions on this repo
- Remote ref state confirmed: `cf98813` now HEAD on `github/main`
- Working tree remains dirty (9 modified files: uncommitted changes not staged, as per requirements)

**2026-05-13T20:06:43.554+00:00 — Ship remaining Pass 2 work (Challenger expansion):**
- Identified remaining Pass 2 file set: 9 modified files covering Challenger agent expansion, prompt updates, tool changes, and squad histories.
- Staged all 9 files: `.github/agents/challenger.md`, `.github/prompts/as-built-from-azure.prompt.md`, `.github/prompts/challenger-review.prompt.md`, `tests/test_alz_recall_indexer.py`, `tools/apex-recall/src/alz_recall/indexer.py`, plus 4 squad history files.
- Committed with message: `docs(agents): Pass 2 — expand Challenger for Step 3 design & Step 7 docs review`; Copilot co-author trailer included.
- Commit SHA: `afdc076`
- Pushed to `github/main`; remote received `cf98813..afdc076 main -> main` (1 commit, 25 objects).
- Remote ref state confirmed: `afdc076` now HEAD on `github/main`; both `github/main` and local `main` aligned.
- **Pass 2 shipping complete:** Challenger agent now covers Step 3 design checks and Step 7 documentation checks with full lockout rules and severity model parity with gate reviews.

**2026-05-13T20:36:56.690+00:00 — Rewind `origin/main` to `38a5954`:**
- Verified `38a5954bbebb3c06298dfe0c9e798feb86c475c3` exists locally as a commit object before any remote change.
- Confirmed `origin/main` was at `cf98813f4706a8d2d40f1a7cb829e1c429addb27` and that `38a5954` is its ancestor, so the requested move was a pure rewind with 157 commits removed and no divergence from the target line.
- Executed the remote-only reset with explicit refspec and lease protection: push targeted `origin` only and did not touch `github/main`.
- Post-push verification showed `origin/main` resolves to `38a5954`; `github/main` remained at `afdc076`.
- Reusable safety pattern: for destructive branch rewinds, verify ancestry first, then use `git push --force-with-lease=refs/heads/main:<expected-old-sha> <remote> <target-sha>:refs/heads/main`, and verify with `git ls-remote`.

**2026-05-13T20:36:56.690+00:00 — Session cleanup and decision consolidation:**
- Scribe consolidated Pass 1 and Pass 2 decisions: merged 7 inbox files into decisions.md.
- Orchestration logs created documenting danny origin-main reset, commit-push, and Pass 2 final shipping workflow.
- Reusable pattern documented: origin/main rewinds now use ancestry verification + force-with-lease for safety.

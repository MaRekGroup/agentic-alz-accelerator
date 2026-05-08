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

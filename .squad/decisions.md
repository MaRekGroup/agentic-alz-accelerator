# Squad Decisions

## Active Decisions

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

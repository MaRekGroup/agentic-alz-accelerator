# Work Routing

How to decide who handles what across the HVE-aligned squad.

## Internal Message & Request Routing Model

### Intake & Triage

**User Request Entry Point:** User message → Danny (Orchestrator)

Danny's intake responsibilities:
1. **Classify** the incoming request:
   - Workflow step (Step 0–9 progression)
   - Off-workflow (bug, documentation, tooling, refactor)
   - Approval gate or blocker resolution
   - Multi-step fan-out (spans multiple agents)

2. **Route Decision Tree:**
    - **Single HVE step** → Route directly to assigned step owner (e.g., Step 1 requirements → Rusty)
    - **Major request needing sprint framing** → Route to Benedict + Danny for sprint review, RPI planning, and task slicing
    - **Spans 2+ HVE steps** → Fan-out to all step owners in parallel (e.g., requirements + governance → Rusty + Saul)
   - **Approval gate** → Route to Isabel (Challenger) for adversarial review
   - **Blocker resolution** → Escalate to relevant domain owner (e.g., governance blocker → Saul)
   - **Off-workflow** (bug, docs, tooling) → Route to domain owner or Copilot (via `@copilot` mention)

3. **Session State Check:**
   - Before routing, Danny checks `.squad/session_state.json` (if exists) for:
     - Current HVE step
     - Active blockers or paused gates
     - Last agent to touch the work
   - If resuming, route to the last agent or next logical step

### When to Route Directly vs Fan-Out

**Route Directly (single agent):**
- User is on Step N and wants to continue to Step N+1 sequentially
- Request is narrowly scoped to one design area (e.g., pure network topology)
- Single specialist skill is needed (e.g., "create a Bicep parameter file")
- Approval gate is open and no blockers exist
- Sprint tracking, sprint closeout, or timeline updates → Benedict

**Fan-Out (parallel):**
- Request spans multiple CAF design areas (e.g., network + governance + security)
- Request is large enough to require sprint planning plus coordinated multi-agent execution
- Approval gate requires concurrent review from Challenger + domain owner
- Blocker resolution involves policy (Saul) + code changes (IaC agent)
- Multi-phase work where agents can prepare downstream in parallel

**Example Fan-Out:**
User: "We need to add new governance policies and update the Bicep for data residency."
- Danny fans out to:
  - Saul: Define policies and compliance constraints
  - Livingston: Prepare Bicep parameter updates
  - Both work in parallel; Saul hands off to Livingston when constraints are ready

### Agent-to-Agent Handoffs (Internal Communication)

Agents communicate handoff context via **structured handoff messages** (not free-form chat):

```
**Handoff: [Agent Name] → [Next Agent Name]**
Scope: [what was done]
Artifacts: [files created/updated]
Blockers: [any open issues]
Next Action: [what the next agent should do]
```

**Synchronous Handoffs** (agent must wait for response):
- Gate approval blockers (Isabel must pass Linus's architecture)
- Policy constraints block code generation (Saul → Livingston)
- Deployment what-if reveals issues requiring constraint changes (Frank → Saul)

**Asynchronous Handoffs** (agent proceeds independently):
- Requirements feed into architecture (Rusty → Linus; Linus starts while Rusty wraps up)
- Design is parallel to governance (Basher ↔ Saul work independently)
- Code generation can start once planning is ready (Reuben → Livingston/Yen)
- Documentation and monitoring start post-deployment (Frank → Tess; Frank → Turk)

### Approval & Blocker Propagation

**Gate Opens:**
1. Artifact owner completes work and marks artifact ready
2. Danny validates artifact completeness (check timestamp, artifact file exists)
3. Danny routes to Isabel (Challenger) for adversarial review
4. Isabel either:
   - **Passes** → Gate opens, Danny routes to next step
   - **Blocks with must-fix** → Danny escalates to artifact owner + relevant domain owner for fix
   - **Advises should-fix** → Owner decides; Danny records advisory and moves forward if owner accepts risk

**Blocker Escalation Path:**
```
Artifact → Isabel (Gate Review)
    ↓ [must-fix findings]
Artifact Owner + Domain Owner (fix iteration)
    ↓ [remediated]
Isabel (re-review) → Gate opens or blocks again
```

**Governance/Policy Blockers:**
- Saul (Governance) raises constraints before code generation begins
- If constraints differ from plan, Reuben revises plan
- If constraints differ from deployed code, Frank cannot deploy
- Saul can override for business exceptions (escalate to Yeselam for approval)

### Fan-Out Completion & Merge

When multiple agents work in parallel (fan-out), Danny coordinates merge:

1. **Track pending agents** — Danny maintains a list of agents still working
2. **Aggregate outputs** — As agents complete, Danny collects artifacts
3. **Check for conflicts** — If Saul's constraints conflict with Linus's architecture, escalate to both for alignment
4. **Gate on slowest** — Workflow does not advance until all fan-out agents report ready
5. **Merge decision** — Danny updates session state with merged outputs and routes to next step

### Session State & Context Handoff

Danny maintains `.squad/session_state.json`:

```json
{
  "current_step": 3,
  "hve_workflow": "greenfield",
  "current_agents": ["basher", "saul"],
  "blocked_until": null,
  "last_gate": 2,
  "last_gate_pass": "2026-05-08T21:40:00Z",
  "artifacts": {
    "01-requirements.md": "done",
    "02-architecture-assessment.md": "in_progress",
    "03-design-*.drawio": "pending",
    "04-governance-constraints.json": "in_progress"
  },
  "blockers": []
}
```

On resume, Danny:
- Checks which agents last touched the work
- Routes to the next logical agent or re-routes to the blocked step
- Provides context snapshot to agent (last 2–3 handoff messages + artifact filenames)

### Off-Workflow Requests (Bug, Docs, Tooling, Refactor)

When user submits non-workflow work (e.g., "fix the validator script" or "update README"):

1. **Danny classifies the work:**
   - Bug → Route to closest domain owner (e.g., validator bug → Reuben/Livingston/Yen)
   - Docs → Route to Tess
   - Tooling/Scripts → Route to Reuben or Copilot
   - Refactor → Route to Copilot or domain owner (depends on scope)

2. **Parallel off-workflow execution:**
   - Off-workflow work runs in parallel with HVE workflow
   - Does not block gate progression
   - Scribe records completion in history

### Escalation Rules

Danny escalates to Yeselam (project owner) when:
- Gate findings block progress for >2 hours (need leadership decision)
- Saul raises must-fix governance issue that contradicts requirements (need business trade-off)
- Budget constraints prevent architecture (need scope negotiation)
- Blocker requires scope change (requirements vs architecture mismatch)

**Escalation Format:**
```
**ESCALATION: [Component] requires owner decision**
Issue: [what is stuck]
Blocker: [which agent cannot proceed]
Options: [what Yeselam can choose]
By: [timestamp]
```

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|----------|
| Workflow sequencing and gate enforcement | Danny | Step orchestration, approval flow, session focus |
| Sprint planning, sprint tracking, and RPI review | Benedict | Break major requests into sprints, run task review, keep sprint records current |
| Requirements intake and clarification | Rusty | Discovery questions, requirement shaping, CAF-aligned capture |
| Architecture and trade-offs | Linus | WAF assessment, target-state design, ADR direction |
| Visual design and diagrams | Basher | Draw.io, Mermaid, architecture visuals |
| Governance, policy, and security constraints | Saul | Azure Policy, RBAC, security baseline, compliance constraints |
| Implementation planning | Reuben | IaC decomposition, module selection, dependency ordering |
| Bicep generation and validation | Livingston | AVM-first Bicep modules, security-aligned templates |
| Terraform generation and validation | Yen | AVM-TF modules, Terraform structure, test scaffolding |
| Deployment execution and release flow | Frank | What-if/plan, GitHub Actions deployment orchestration |
| As-built docs and operational guides | Tess | Runbooks, inventories, technical design docs |
| Continuous monitoring and diagnostics | Turk | Compliance scans, drift detection, alerting posture |
| Auto-remediation and rollback planning | Virgil | Drift repair, policy remediation, rollback-safe fixes |
| Adversarial review and gate challenge | Isabel | Gate reviews, risk identification, must-fix findings |
| Brownfield discovery and current-state assessment | Terry | Inventory, WARA checks, migration inputs |
| Session logging and decision merge | Scribe | Automatic background memory work |
| Queue monitoring and backlog motion | Ralph | Issue checks, PR follow-up, keep-alive monitoring |

## Issue Routing

| Label | Action | Who |
|-------|--------|-----|
| `squad` | Triage the issue, classify it, and assign `squad:{member}` labels | Danny |
| `squad:danny` | Pick up orchestrator or lead-routing work | Danny |
| `squad:benedict` | Pick up sprint planning and tracking work | Benedict |
| `squad:rusty` | Pick up requirements work | Rusty |
| `squad:linus` | Pick up architecture work | Linus |
| `squad:basher` | Pick up design and diagram work | Basher |
| `squad:saul` | Pick up governance and policy work | Saul |
| `squad:reuben` | Pick up planning work | Reuben |
| `squad:livingston` | Pick up Bicep work | Livingston |
| `squad:yen` | Pick up Terraform work | Yen |
| `squad:frank` | Pick up deployment work | Frank |
| `squad:tess` | Pick up documentation work | Tess |
| `squad:turk` | Pick up monitoring work | Turk |
| `squad:virgil` | Pick up remediation work | Virgil |
| `squad:isabel` | Pick up challenger and review work | Isabel |
| `squad:terry` | Pick up brownfield assessment work | Terry |

### How Issue Assignment Works

1. When a GitHub issue gets the `squad` label, **Danny** triages it and assigns the matching `squad:{member}` label.
2. When a `squad:{member}` label is applied, that member owns the issue in the next session.
3. Reviewer rejection lockout applies to rejected artifacts; the original author cannot revise the rejected artifact in the next cycle.
4. Scribe records team-relevant outcomes after substantial work, and Ralph keeps the board moving when monitoring is active.

## Sprint Planning & Tracking

Benedict owns sprint hygiene and assists Danny with execution coordination for major requests.

### Sprint trigger

A request is treated as a **major request** when it spans multiple agents, multiple workflow steps, or enough work that sprint slicing improves focus and throughput.

### Sprint opening routine

Each sprint begins with a **task review and RPI planning session**:

1. **Review** — restate the request, current constraints, dependencies, and open blockers
2. **Plan** — break the work into sprint-sized slices with owners, artifacts, and exit criteria
3. **Implement** — hand the sprint backlog to Danny for routing and execution

### Sprint closeout routine

At sprint close, Benedict updates `./docs/sprintHistory/`:

- `timeline.md` — running sprint timeline and milestone log
- `summary.md` — concise current-state summary across sprints
- `detail-log.md` — fuller capture of changes made, lessons learned, and notable agent updates

### Coordination rule

- Benedict manages tracking, planning, and sprint documentation
- Danny retains workflow routing, approval gates, and final execution coordination
- Major requests default to **Benedict + Danny** together at the start of a new sprint

## Subagent Scale-Out Rules

An **assigned agent** may decompose its own workload into multiple subagents when a task is large enough that parallel execution meaningfully accelerates delivery. This is distinct from Danny's fan-out across different HVE roles — here a *single* role owner splits its own work internally.

### When scale-out is permitted

All three conditions must hold before an agent may scale out:

| Condition | Requirement |
|-----------|-------------|
| **Independent outputs** | Each subagent writes to a unique artifact or clearly scoped section. No two subagents write the same file simultaneously. |
| **No ordering dependency** | No subagent's work requires reading another subagent's in-progress output. All inputs are available before any subagent starts. |
| **Mergeable at parent** | The parent agent can deterministically merge all subagent outputs without a human decision. Conflicts must not require judgment. |

**Typical safe cases:** generating Bicep modules for independent resource groups; producing separate runbook sections; running independent WARA checks across non-overlapping subscriptions.

### When scale-out is prohibited

Scale-out must not occur if any of the following is true:

| Condition | Reason |
|-----------|--------|
| Two or more subagents would write the same file | Direct race condition on artifact state |
| A subagent's output is an input to another subagent in the same batch | Ordering dependency; sequential execution required instead |
| An approval gate is currently open that covers the artifact domain | Gate checks must run at the parent level after all subagents report completion |
| A reviewer lockout covers the artifact domain | Lockout applies to the parent assignment; spawning subagents to work around it is prohibited |
| Merge requires a judgment call or human trade-off | Subagent output must be mechanically composable |
| The task is already small (≤2 logical parts) | Overhead of coordination exceeds the time saved |

### Race condition avoidance

1. **Unique file per subagent** — assign each subagent a distinct output path before spawning. Overlap is not allowed.
2. **Shared artifact not yet created** — if a shared artifact does not yet exist and multiple subagents would create it, prohibit concurrent creation. Run the first subagent sequentially to establish the file, then fan out remaining subagents.
3. **Drop-box for shared state** — any shared writes (decisions, session state updates) must use the `.squad/decisions/inbox/{agent}-{slug}.md` drop-box pattern. Never write directly to shared state files concurrently.
4. **Gate after merge** — the parent agent performs all approval gate checks only after collecting and merging every subagent's output. A partial result never opens a gate.
5. **Conflict = escalate** — if two subagent outputs contradict each other, the parent agent does not silently pick one. It escalates to Danny for resolution before merging.

### Reviewer lockout preservation

- Lockout is tracked against the **parent agent assignment** (the HVE role), not individual subagents.
- If Isabel (Challenger) rejects an artifact produced by a scaled-out subagent, the **entire parent agent and all subagents that contributed to that artifact are locked out**.
- A different agent must own any revision — spawning a new subagent from the locked-out parent is not a workaround.
- The parent agent must report subagent contributors in its artifact hand-off so Danny can enforce lockout correctly.

### Approval gate preservation

- Subagents operate entirely within a single HVE step. They cannot advance the workflow past a gate.
- Danny's gate check is always triggered by the parent agent's "ready" signal, never by an individual subagent.
- If any subagent fails or produces incomplete output, the parent must hold — do not send a partial "ready" signal to Danny.

### Artifact ownership

- The parent agent is the **sole artifact owner** regardless of which subagent produced content.
- Hand-off messages from the parent to Danny must list all contributing subagents so the session state reflects full provenance.
- Scribe records the parent agent (not subagents) as the artifact author in history.

---

## Rules

1. **Eager by default** — start all useful independent work, including downstream preparation.
2. **Use the mapped HVE owner first** — each HVE role has a primary roster owner above.
3. **Direct facts stay direct** — only spawn when domain judgment is needed.
4. **Scribe always runs silently** after substantial work.
5. **Ralph never authors domain artifacts** — Ralph monitors, nudges, and routes.
6. **When work spans multiple HVE roles, fan out** to all relevant owners in parallel.
7. **Governance and challenger findings can block progress** until explicitly resolved or approved.
8. **Scale-out is opt-in, not default** — an agent may split its own work into subagents only when all three scale-out conditions in the section above are met.
9. **Race conditions block scale-out** — if any two subagents would write the same file or depend on each other's in-progress output, run sequentially instead.
10. **Parent agent owns the gate signal** — no subagent may trigger a gate check or advance the HVE workflow step directly.
11. **Major requests start with sprint framing** — Benedict and Danny review major requests before broad execution begins.
12. **Every sprint ends with history updates** — Benedict keeps `docs/sprintHistory/` current with timeline, summary, and detailed notes.

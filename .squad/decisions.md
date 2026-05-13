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


## Inbox Merge: ALZ Comparison Fan-Out (2026-05-08T22:45:22.602+00:00)

**Coordinator:** Scribe  
**Context:** Three agents completed ALZ comparison analysis to ground value propositions. Agents: Linus (differentiators), Terry (gaps/risks), Tess (documentation).

### 2026-05-08T22:45:22.602+00:00: ALZ Comparison Analysis - Linus (Differentiators vs Official ALZ)

**By:** Linus (Architect)

**Summary:** Identified 3 differentiated value propositions: (1) Three-tier enforcement (code→deploy→monitor), (2) Brownfield assessment with WAF alignment, (3) Agentic orchestration reducing timeline from 8-12 weeks to 2-4 weeks. All grounded in repo evidence.

**Key Finding:** Three-tier enforcement (validation at code gen, deployment, and continuous monitoring) is the primary differentiator vs official ALZ.

---

### 2026-05-08T22:45:22.602+00:00: ALZ Comparative Gap Analysis - Terry (Coverage & Risks)

**By:** Terry (Assessment)

**Summary:** Microsoft covers ALZ design guidance well; we uniquely offer brownfield assessment (untested at scale), approval gates (unproven friction), security baseline enforcement (proven), mandatory cost governance (adoption risk). Terraform track ~40% complete.

**Key Finding:** Biggest risks: Terraform incomplete, Day-2 auto-remediation untested in production, TDD generation unvalidated. Should position as 'Governance-First ALZ Accelerator' with brownfield + gates as lead differentiators.

---

### 2026-05-08T22:45:22.602+00:00: Documentation Comparison - Tess (ALZ Docs vs Our Docs)

**By:** Tess (Documentation)

**Summary:** Our docs add value in automation (14-agent workflow), brownfield assessment (Step 0), security enforcement, cost governance, and quick-start runbooks. Gaps: Day-2 ops playbooks, app LZ vending, troubleshooting guide, WAF checklist, policy strategy.

**Key Finding:** Position as operationalizing ALZ principles through automation + enforcement. Close 5 key doc gaps to strengthen positioning: Day-2 runbook, app vending, troubleshooting, customization guide, WAF checklist.

---

## Active Decisions (May 2026 - Design/Documentation Flow Audit)

### 2026-05-13T16:13:48.828+00:00: Step 3 Design Flow — Critical Findings and Recommendations

**By:** Basher (Design), Tess (Documentation), Isabel (Challenger)  
**Type:** Multi-agent design/documentation flow audit  
**Status:** Proposed  

**Summary:** Basher, Tess, and Isabel conducted a collaborative review of Steps 3 and 7 artifact contracts and gate coverage. Identified 15+ critical gaps including inconsistent artifact naming across 5 sources, missing Challenger gate coverage for design outputs, broken Step 3→Step 7 handoff, and ambiguous skip criteria.

**Key Findings Across All Three:**

1. **[CRITICAL] Artifact naming contract is broken** — Design outputs are specified differently in `AGENTS.md`, `markdown.instructions.md`, `04-design.prompt.md`, `design.md`, and `copilot-instructions.md`. Artisan may not produce `03-design-summary.md` depending on which source it follows, breaking Chronicler's prerequisite.

2. **[CRITICAL] No Challenger review covers Step 3** — Step 3 sits between Gate 2 and Gate 3 with no Challenger pass. Design diagrams can be incomplete, ADRs missing, or inconsistent with architecture assessment — all unreviewed.

3. **[CRITICAL] Step 3 "optional" criteria are undefined** — Design is listed as optional in `design.md` and `docs/workflow.md`, but no criteria govern when to skip. Chronicler detects skip via filesystem check (fragile, implicit).

4. **[CRITICAL] Step 7 TDD has a structural hole when Step 3 is skipped** — Chronicler's TDD template references diagrams from Step 3 with no fallback. If Step 3 is skipped, Architecture Overview section is hollow.

5. **[CRITICAL] Chronicler lacks MCP tools for live validation** — Instructed to query Resource Graph and validate deployed state, but MCP not in tool list. Falls back to artifact reading only, missing drift.

6. **[HIGH] 5 additional medium-severity gaps** — Skill loading order, prompt vs agent definition divergence, artifact path ambiguity, scope of WARA compliance in Step 7, missing prerequisites alignment.

**Minimum Change Set (Must-Fix):**
- Reconcile artifact naming in AGENTS.md + design.md + documentation.md + prompts
- Add `03-design-summary.md` as required completion artifact (not optional)
- Add step_3_status flag to session state (skipped vs completed vs failed)
- Fix TDD fallback: "Step 3 skipped — architecture from 02-architecture-assessment.md"
- Add `mcp` to Chronicler's tool list OR explicitly document delegation to Sentinel Step 8
- Add Challenger review slot for design artifacts (after Step 3, before Step 3.5)

**Should-Fix (Operational Improvements):**
- Align `04-design.prompt.md` with full agent workflow outputs
- Define skip criteria: Simple tier → skip; Standard/Complex → required
- Add self-validation checklist to Phase 2/Phase 4 of `design.md`
- Define canonical output manifest in both `documentation.md` and Step 7 prompt

**Files to Update:**
- `.github/agents/design.md` — fix skill load order, add summary artifact checkpoint
- `.github/agents/documentation.md` — add TDD fallback, add mcp tool, align prerequisites
- `AGENTS.md` — canonicalize artifact naming, add skip criteria
- `04-design.prompt.md` — align with full agent workflow
- `.squad/routing.md` — add step_3_status to session state schema

**Decision Requested:** Approve minimum change set to unblock full Step 3→Step 7 pipeline.

---

### 2026-05-08T23:37:53.627+00:00: User directive — Branch check before changes

**By:** Yeselam Tesfaye  
**What:** Before making a change, always check which branch you are on first.  
**Why:** User request — captured for team memory

---

### 2026-05-08T23:06:54Z: PR #63 Lint Failure — Trailing Whitespace

**By:** Reuben (IaC Planner)  
**Issue:** `.github/workflows/squad-heartbeat.yml` has trailing spaces on lines 60, 66, 75, 91, 97  
**Recommendation:** Remove trailing whitespace  
**Status:** Requires merge-blocking fix

---

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction

## Inbox Merge (2026-05-08)

### copilot-directive-2026-05-08T22-01-32.879+00-00

### 2026-05-08T22:01:32.879+00:00: User directive
**By:** Yeselam Tesfaye (via Copilot)
**What:** Create a Scrum Master role to manage sprint planning and tracking; break major requests into sprints; start each sprint with an RPI task review and planning session; close each sprint by updating `./docs/sprintHistory` with a running timeline, a concise summary, and a longer capture of updates, lessons learned, and notable agent changes.
**Why:** User request — captured for team memory

### linus-value-proposition

# Value Propositions for Agentic ALZ Accelerator

**Analysis Date:** 2026-05-08T21:51:11.557+00:00  
**Analyzed By:** Linus (Architect)  
**Request:** Synthesize grounded value propositions around practical ALZ adoption acceleration

---

## Summary

The accelerator's core strength is **practical, enforceable ALZ adoption**—not a generic "AI infrastructure" story. After analyzing the repo structure, agent architecture, IaC modules, and operational patterns, I've identified three differentiated value propositions, each grounded in specific repo evidence.

---

## Candidate 1: "Enforce ALZ Best Practices Automatically — No Workarounds"

### Thesis

Organizations that have adopted Azure Landing Zones struggle with **compliance drift** and **best-practice violations** post-deployment. Teams deploy infrastructure, gates close, and in Year 2 they discover unmonitored policy gaps, cost overruns, or security baseline violations buried in 50+ resource groups.

This accelerator solves that by:
1. **Embedding non-negotiable rules in code generation** (not post-deploy checking)
2. **Gating every deployment on baseline compliance** — code generation and security validators run **before** terraform apply/bicep deployment
3. **Continuous monitoring + auto-remediation** for drift that happens anyway
4. **Enforcing cost governance** with budget alerts built into every deployment (6 rules, tested at commit time)

### Evidence from Repo

- **Security baseline** (6 non-negotiable rules): enforced at code gen (Step 5), deployment preflight (Step 6), and continuous monitoring (Step 8)  
  Files: `.github/instructions/iac-bicep-best-practices.instructions.md`, `.github/instructions/iac-terraform-best-practices.instructions.md`, `scripts/validators/validate_security_baseline.py`

- **Cost governance validator**: "no budget, no merge" — every deployment includes parameterized budget alerts at 80%, 100%, 120% forecast thresholds  
  Files: `docs/cost-governance.md`, `scripts/validators/validate_cost_governance.py`, Bicep/Terraform samples in `infra/`

- **Adversarial gate reviews** (Challenger agent) at 4 approval gates (1, 2, 4, 5) scale with complexity — prevents "good enough" shipping  
  Files: `.github/agents/challenger.md`, `src/agents/challenger_agent.py`

- **Day-2 continuous loop** (Steps 8–9): Sentinel runs compliance scans every 30 min, Mender auto-remediates critical/high with snapshot rollback  
  Files: `AGENTS.md` (Day-2 Operations section), `.github/agents/monitoring.md`, `.github/agents/remediation.md`

- **CAF alignment throughout**: Every IaC module maps to CAF design areas; every agent handoff preserves that mapping  
  Files: `AGENTS.md` (CAF Design Area Alignment table), `infra/bicep/{customer}/` module structure, `.github/skills/caf-design-areas/SKILL.md`

### Value Claim

**"Deploy ALZ with rules baked in, not bolted on."** Automatically enforce TLS 1.2, HTTPS-only, managed identity, zero public blob access, and cost controls *before* the first byte hits Azure. Drift is caught and repaired within an hour, not months later.

### Target Customer

- Mid-to-large enterprises that deployed landing zones and now face compliance drift
- Organizations with security/cost COE teams that set standards but lack enforcement tools
- Teams rolling out ALZ to multiple business units (need guardrails, not just templates)

---

## Candidate 2: "Accelerate ALZ Knowledge Transfer via Orchestrated, CAF-Aligned Documentation"

### Thesis

**Knowledge transfer is the real bottleneck in ALZ adoption**, not infrastructure code. When a new architect or security lead joins, they face:
- Undocumented trade-offs (why hub-spoke over vWAN?)
- Scattered ADRs (some in Markdown, some in Teams, some nowhere)
- "Current state" described in PowerPoint slides that go stale in weeks
- No automated, evidence-based reasoning chain from requirements → architecture → code

This accelerator solves that by:
1. **Generating architecture documentation algorithmically** from assessed environments (current-state architecture + diagrams)
2. **Forcing explicit trade-off reasoning** at Step 2 (Architecture) with WAF/CAF scoring before code is written
3. **Creating ADRs at decision points** with WAF rationale and alternatives considered
4. **Versioned, audit-able artifact chain** — every design decision points to requirements that justify it

### Evidence from Repo

- **Generated architecture documentation** for brownfield assessments: current-state docs, target-state docs, Mermaid diagrams generated from live discovery data  
  Files: `docs/accelerator/target-architecture.md` (sections on "Generated Documentation Capability" and "Output Artifacts")

- **Architecture Decision Records (ADRs)** with WAF pillar justification, alternatives, and consequences  
  Files: `.github/skills/azure-adr/`, `src/agents/design_agent.py` (Artisan agent), `docs/accelerator/adr/`

- **WAF + CAF scoring at architecture step** (Step 2, Oracle agent): produces `02-architecture-assessment.md` with pillar scores (0–100 per pillar), design area alignment, cost estimation  
  Files: `.github/agents/architect.md`, `src/agents/architect_agent.py`, `src/tools/wara_engine.py` (scoring model)

- **Step 1 (Requirements) mapped to all 8 CAF design areas** — no orphaned requirements  
  Files: `.github/agents/requirements.md`, `.github/skills/caf-design-areas/SKILL.md`

- **Agent handoff structure** preserves reasoning chain: each agent receives prior artifacts + context, adds its layer, hands off  
  Files: `.squad/routing.md` (Agent-to-Agent Handoffs section), `AGENTS.md` (Artifact Naming Convention, each step has a numbered prefix)

- **Operational runbooks generated post-deployment** (Step 7, Chronicler): resource inventory, monitoring setup, alert thresholds, runbook procedures  
  Files: `.github/agents/documentation.md`, `src/agents/documentation_agent.py`

### Value Claim

**"Turn infrastructure decisions into living documentation."** Capture why you chose hub-spoke (or vWAN), why you placed Identity in a separate subscription, why you enabled certain Defender plans — and auto-generate that reasoning chain for new hires, auditors, and future architects.

### Target Customer

- Large enterprises with distributed engineering teams that need documented precedent
- Compliance/audit teams that require evidence trails for infrastructure decisions
- Organizations scaling from one platform LZ to 5+ concurrent landing zones (need clear delegation + reasoning)
- Teams building ALZ platforms for internal consumption (need runbooks that stay current)

---

## Candidate 3: "Reduce ALZ Deployment Time from 6 Months to 2 Weeks — with Approval Gates Intact"

### Thesis

Most Azure Landing Zone deployments take 6–12 months: discovery → design → approvals → code → testing → deployment. The accelerator collapses that to **2–4 weeks for greenfield, 3–6 weeks for brownfield** by:
1. **Parallelizing agent work** — requirements, architecture, design, and governance run concurrently after Step 1
2. **Generating IaC from templates** (AVM-first Bicep/Terraform) instead of writing from scratch
3. **Automating deployment validation** with what-if/plan preview at Step 6
4. **Maintaining approval gates** (never skipped) but making each gate a 10-minute review, not a 2-week committee process

### Evidence from Repo

- **Parallel workflow steps** after Gate 2: Design (Step 3) and Governance (Step 3.5) run concurrently, then feed into Planning (Step 4)  
  Files: `AGENTS.md` (Workflow Steps diagram showing parallel edges)

- **AVM-first code generation** (Step 5): agents route to AVM modules first, fall back to native `resource` only when no AVM exists. Generates Bicep/Terraform automatically from plan  
  Files: `.github/skills/azure-bicep-patterns/`, `.github/skills/terraform-patterns/`, `.github/agents/bicep-code.md`, `src/agents/bicep_code_agent.py`

- **What-if preview before deployment** (Step 6): validates correctness without applying; gates on dry-run success  
  Files: `.github/agents/deployment.md` (what-if/plan preview section), `src/agents/deployment_agent.py`

- **Complexity-scaled approval gates**: Simple deployments (≤3 resource types, single region) get 1 Challenger pass; standard get 2; complex get 3  
  Files: `AGENTS.md` (Complexity Classification table)

- **Artifact naming convention** (numbered steps) + gate automation: Danny (Orchestrator) routes on artifact readiness, not committee scheduling  
  Files: `.squad/routing.md` (Gate Opens section), `AGENTS.md` (Artifact Naming Convention)

- **Assessment + onboard mode** for brownfield: Step 0/0.5 pre-fills requirements from live discovery, skipping 2–3 weeks of discovery interviews  
  Files: `docs/accelerator/target-architecture.md` (Operational Modes table), `.github/agents/assessment.md`

### Value Claim

**"From requirements to deployed landing zones in 2–4 weeks, with security and CAF alignment baked in."** Parallel agents + code generation + structured gates collapse the timeline without sacrificing governance.

### Target Customer

- Time-sensitive greenfield migrations (cloud center of excellence rolling out ALZ to 10+ business units)
- Organizations on a fiscal quarter deadline (need ALZ in place by Q4)
- MSPs or cloud consulting firms deploying ALZ for multiple customers (amortize the accelerator's cost across engagements)
- Enterprises with brownfield environments that need rapid delta assessment → planning → remediation

---

## Comparative Analysis

| Value Prop | Strongest Differentiator | Evidence | Risk |
|-----------|-------------------------|----------|------|
| **#1: Enforce Baselines** | Automatic compliance in code (not post-deploy checks) | Validators run at commit; Step 5 enforces 6 rules; continuous monitoring with 30-min scan + auto-remediation | Requires adoption of entire workflow; custom rules need code changes |
| **#2: Knowledge Transfer** | Algorithmic documentation generation from assessed environments | Generated current/target-state docs + Mermaid diagrams from discovery; ADRs auto-created at decision points; CAF-aligned throughout | Works best if teams use the artifact chain; loose adoption = scattered docs again |
| **#3: Timeline Acceleration** | Parallelization + AVM-first generation + complexity-scaled gates | 5-step parallel flow post-Gate 2; auto-routing on artifact readiness; brownfield pre-fill skips 2+ weeks | Requires disciplined gate reviews (or gates become rubber-stamps); IaC generation quality depends on plan quality |

---

## Synthesis & Recommendation

All three are **grounded in real repo capabilities** and solve distinct customer problems:

1. **#1 resonates with security/compliance teams** → "rules in code"
2. **#2 resonates with architecture/knowledge teams** → "documented reasoning"
3. **#3 resonates with delivery teams** → "fast path to Azure"

For **launch positioning**, I recommend leading with **#1 (Enforce Baselines)** because:
- It's the most defensible (validator code + security baseline specs are verifiable)
- It solves a pain point *after* landing zones are deployed (broadest audience)
- It bridges all three themes: enforces rules (#1), documents why via ADRs (#2), automates remediation (#3)

Secondary positioning can highlight #2 (knowledge transfer) as a *differentiator* from generic IaC template repos, and #3 as the *speed bonus* for greenfield.

---

## Next Steps

- [ ] Validate these propositions with 2–3 customer conversations (security, architecture, delivery leads)
- [ ] Build one-pager for each that includes "1 week onboarded, value delivered" metrics
- [ ] Draft elevator pitches and success stories grounded in each proposition
- [ ] Map product roadmap against each proposition (which features amplify which claim?)


### rusty-problem-statement

# Problem Statement Candidates — Agentic ALZ Accelerator

**Discovered by:** Rusty (Requirements)  
**Date:** 2026-05-08T21:51:11Z  
**Context:** Fan-out review of repo content to infer core user problem and align on value proposition  
**Input:** Yeselam's stated interest: "accelerating use of the ALZ content I've been researching and tinkering with"

---

## Analysis Summary

### What This Project Does
The Agentic ALZ Accelerator is a **14-agent orchestration system** that transforms Azure Landing Zone requirements → design → infrastructure code → deployment → monitoring, all aligned to CAF design areas. It supports both greenfield (new) and brownfield (existing) deployments with approval gates and continuous compliance monitoring. The system uses AVM-first IaC, enforces a 6-rule security baseline, and includes auto-remediation.

### Core Evidence
- 14 specialized agents (Scribe, Oracle, Artisan, Warden, Strategist, Forge, Envoy, Chronicler, Sentinel, Mender, Challenger, Assessor, Assessment, Orchestrator)
- 35+ skills organized by domain (CAF design areas, IaC patterns, compliance, cost governance)
- 8 GitHub Actions workflows (bootstrap, deploy, monitor, assess, validate)
- Multi-IaC support (Bicep + Terraform with AVM modules)
- Approval gates at 6 decision points
- Day-2 ops (compliance monitoring + auto-remediation)

### What's Being Accelerated
Yeselam explicitly wants to **accelerate use of researched/tinkered ALZ content**. The repo shows:
- 18 months of ALZ research, design decisions, and module composition work
- 221 WARA checks covering 5 WAF pillars
- Multiple IaC frameworks proven and tested
- Architecture diagrams and design docs already authored
- Validated security baseline and cost governance rules

**The constraint:** All this knowledge exists but requires **manual coordination, decision sequencing, and handoffs** to become actual deployments.

---

## 3 Candidate Problem Statements

### **Candidate 1: Enterprise Architects' Bottleneck**

**Target User:** Enterprise Architects and Landing Zone Design Leads (annual engagement model)

**Problem:**  
Azure Landing Zone deployment is a **6-12 month, multi-team coordination effort** requiring synchronized input from networking, security, identity, and governance teams. Architects must manually sequence requirements → architecture → governance → IaC → deployment decisions, document everything in Word/PowerPoint, and coordinate approvals across teams. A single ambiguity or change request cascades through all downstream work. Teams lack a **structured intake process** to capture requirements once and trace them through design → code → monitoring without loss of context.

**Desired Outcome:**  
A **single orchestrated workflow** that:
- Captures requirements in one conversation (not multiple meetings)
- Automatically maps requirements to CAF design areas
- Routes designs through approval gates with challenger reviews
- Generates IaC (Bicep + Terraform) automatically from approved architecture
- Deploys with pre-deployment validation and compliance checks
- Monitors continuously and auto-remediates drift

**Supporting Evidence:**
- README § "CI/CD Pipelines" — 8 workflows handling the full orchestration
- AGENTS.md § "Approval Gates" — 6 non-negotiable gates with challenger reviews
- `01-requirements.md` template — captures all 8 CAF areas in one pass
- 14-agent roster each owning a step of the workflow

---

### **Candidate 2: ALZ Knowledge Transfer at Scale**

**Target User:** Microsoft Premier Field Engineers and Microsoft Solutions Architects (transactional delivery)

**Problem:**  
Microsoft's ALZ expertise is concentrated in docs, reference implementations, and subject matter experts. Customer engagements require **reinventing the wheel** — architects manually combine ALZ CAF design areas, Microsoft best practices, customer constraints, and compliance frameworks. This knowledge transfer happens via PowerPoint decks, Word documents, and email threads. After months of design, customers still need to write IaC or hire contractors. There's no **reusable, automatable, domain-specific orchestration system** that codifies ALZ patterns and accelerates time from requirements → deployed infrastructure.

**Desired Outcome:**  
A **production-ready orchestration platform** that:
- Encodes ALZ best practices, CAF design areas, and security baselines as reusable agents and skills
- Automates requirement-to-code pipeline with approval gates
- Generates architecture diagrams, decision records, and documentation automatically
- Validates against Microsoft standards (WAF, CAF, security baseline) at each gate
- Integrates with Azure CLI, Bicep, Terraform, GitHub Actions, Defender, Policy
- Runs in customer subscriptions with federated credential auth (no stored secrets)

**Supporting Evidence:**
- 221 WARA checks covering 5 WAF pillars (`src/config/wara_checks/`)
- CAF design area mapping in 8 IaC modules (`infra/bicep/` and `infra/terraform/`)
- Security baseline enforced at code generation, deployment, and monitoring (`scripts/validators/`)
- MCP servers for Azure Pricing, Azure Platform, Draw.io integration
- Brownfield assessment workflow (Step 0) for existing environments

---

### **Candidate 3: ALZ-as-a-Product (Acceleration Toolkit)**

**Target User:** Infrastructure Platform Teams and Platform Engineering Leads (SaaS/product-like consumption)

**Problem:**  
Organizations building internal platforms need a **base infrastructure offering** that is:
- **Compliant by default** (security baseline, governance policies, budget controls)
- **Customizable per workload** (profiles for dev, test, prod, different compliance levels)
- **Auditable end-to-end** (requirements → approvals → code → deployment → monitoring)
- **Hands-off after go-live** (continuous compliance, drift detection, auto-remediation)

Currently, platform teams either build from scratch (6–18 months) or fork the ALZ reference implementation (no automation, manual updates). There's no **productized, opinionated, agent-driven infrastructure engine** that delivers landing zones with built-in governance and monitoring.

**Desired Outcome:**  
An **integrated product** that:
- Provides a CLI or web UI to define landing zone requirements
- Auto-generates architecture diagrams, design docs, and approval checklists
- Generates Bicep/Terraform code that passes security, cost, and compliance validation
- Deploys via GitHub Actions with 6-gate approval workflow
- Monitors compliance continuously (every 30 min), alerts on drift, auto-remediates
- Supports greenfield and brownfield (existing Azure environments)
- Integrates with customer GitHub orgs, Azure subscriptions, and existing tooling

**Supporting Evidence:**
- Fullstack end-to-end workflow (requirements → deployment → monitoring)
- 14 agents with clear role definitions and handoff protocol
- Agent-to-agent communication via structured dropbox pattern (`.squad/decisions/inbox/`)
- Session state tracking for multi-hour, multi-step workflows
- CLI entry points (`alz-recall`) and GitHub Actions triggers
- Subagent scale-out rules for parallel work (decision 2026-05-08)

---

## Recommended Framing

All 3 candidates are **viable and complementary**:

| Candidate | Best For | Timeline | Scope |
|-----------|----------|----------|-------|
| **Architects' Bottleneck** | Internal Microsoft + Premier FSE engagement model | Immediate (use existing accelerator) | Single customer per engagement |
| **ALZ Knowledge Transfer** | Microsoft Solutions Architecture and support | Immediate to near-term | Microsoft + customer co-delivery |
| **ALZ-as-Product** | Long-term productization (Internal Platform, ISV, SaaS) | 12+ months | Multi-tenant, multi-customer |

**Suggestion:** Start with **Candidate 1** (Architects' Bottleneck) as **MVP** — it has the broadest market fit and can be proven with an internal or partner customer in 4–8 weeks. Candidates 2 & 3 are natural extensions.

---

## Key Assumptions

1. **ALZ expertise already exists** — Yeselam has researched and built modules, agents, and validators
2. **Orchestration is the gap** — Individual pieces (Bicep modules, policies, validators) exist but lack automated sequencing
3. **Enterprise decision gates are non-negotiable** — Approval gates at 6 checkpoints are critical for governance
4. **CAF alignment drives adoption** — Mapping to all 8 CAF design areas provides Microsoft credibility
5. **Security baseline + compliance are table stakes** — Not optional, enforced at code generation and runtime
6. **Both IaC frameworks matter** — Bicep for Microsoft shops, Terraform for multi-cloud

---

## Next Steps (For Squad)

1. **Yeselam clarifies:** Which candidate resonates most? (Or is there a 4th framing?)
2. **Danny (Orchestrator) routes:** Once framing is decided, escalate to Linus (Architect) for full value proposition and GTM strategy
3. **Rusty appends** learnings to `.squad/agents/rusty/history.md`
4. **Squad votes:** Consensus on target user, problem, and desired outcome before Linus enters


### terry-repo-evidence

# Repository Evidence Pack: Agentic ALZ Accelerator

**Compiled:** 2026-05-08T21:51:11.557+00:00  
**Owner:** Terry (Assessment HVE)  
**Status:** Evidence for value proposition and problem statement refinement

---

## 1. WHAT THIS PROJECT ACTUALLY DOES (Evidence-Based)

### A. Core Artifact: APEX-Aligned Multi-Agent Workflow

**Evidence:**
- **9 production agents** fully implemented in Python + Semantic Kernel (orchestrator, requirements, architect, design, governance, iac-planner, bicep-code, deployment, documentation)
- **Day-2 operations agents** (monitoring, remediation, challenger) for continuous lifecycle
- **DAG-based workflow engine** with approval gates at steps 1, 2, 3, 4, 5, and 6
- **3 MCP servers** integrated: azure-pricing (18 tools), azure-platform (27 tools), drawio

**Differentiator:** This is *not* a template library. It's a functioning orchestration layer that coordinates multi-agent workflow with state persistence and gate enforcement.

### B. Infrastructure-as-Code in Two Tracks

**Evidence:**
- **Bicep track:** 22 Bicep files organized by CAF design area (connectivity, identity, governance, logging, management, policies, security, platform-security, billing-and-tenant)
- **Terraform track:** 9 Terraform files with equivalent module structure
- **AVM-first policy** enforced across both tracks

**What it solves:** Teams can choose Bicep or Terraform without rework—architecture is the same, only codegen path differs.

### C. Brownfield (Existing Environment) Assessment Pipeline

**Evidence:**
- **Discovery collector** reads-only: MGs, subscriptions, resources, policies, RBAC, network topology, logging, security posture
- **WARA assessment engine** (508-line YAML check catalog) evaluates 221 WAF checks across all 5 pillars
- **Report generator** produces: current-state markdown, target-state markdown, assessment JSON, architecture diagrams, remediation roadmaps
- **Step 0 integration** in orchestrator—brownfield assessment feeds downstream architecture and planning

**Capability:** Can assess a 5000+ resource estate, score it against WAF/CAF, and produce a gap remediation roadmap without touching live resources.

### D. Security Baseline (Non-Negotiable)

**Evidence:**
- **6 hardcoded rules** enforced at code gen, deploy preflight, and continuous monitoring:
  - TLS 1.2 minimum
  - HTTPS-only traffic
  - No public blob access
  - Managed Identity preferred
  - Azure AD-only SQL auth
  - Public network disabled (prod)
- **2 validators** in scripts/validators: `validate_security_baseline.py`, `validate_cost_governance.py`
- **Checker logic** in governance agent reads policy assignments and detects violations

**Differentiator:** These aren't recommendations. They're gatekeepers—code can't merge without passing baseline checks.

### E. Cost Governance Model

**Evidence:**
- **Budget resource** required on every deployment (no hardcoding allowed)
- **3-tier alert thresholds:** 80% (forecast warning), 100% (escalation), 120% (critical)
- **Parameterized per environment** to support dev/stage/prod cost separation

**What it solves:** "No budget, no merge" policy prevents runaway spending at deployment gate.

### F. CI/CD Automation

**Evidence:**
- **8 GitHub Actions workflows:**
  - 1-bootstrap.yml (MG hierarchy, subscription setup, provider registration)
  - 2-platform-deploy.yml (4 platform LZs: Mgmt→Conn→Ident→Sec with cascade or targeted)
  - 3-app-deploy.yml (config-driven parallel app LZ deployment)
  - assess.yml (brownfield WAF assessment)
  - 5-pr-validate.yml (lint, security, cost, what-if preview)
  - monitor.yml (compliance scanning across all subscriptions)
  - reusable-deploy.yml (DRY orchestration: resolve→validate→plan→deploy→verify)
  - assign-role.yml (RBAC utility)
- **Self-hosted runner support** via single `vars.RUNNER_LABEL` configuration
- **OIDC federation** for GitHub→Azure auth (no secrets in repo)

**Scope:** Full CI/CD pipeline from checklist to deployed, monitored infrastructure.

### G. Documentation & Artifact Generation

**Evidence:**
- **Post-deployment TDD generator** produces Technical Design Documents (7-design-document.md)
- **Architecture diagram generator** (Python diagrams library + Draw.io) with Azure icon support
- **ADR generator** (Architecture Decision Records with WAF pillar mapping)
- **Generated outputs:**
  - 01-requirements.md (CAF-aligned requirements)
  - 02-architecture-assessment.md (WAF assessment + cost estimates)
  - 03-design-*.{drawio,png,md} (diagrams + ADRs)
  - 04-governance-constraints.{md,json} (policy inventory + baseline checks)
  - 04-implementation-plan.md (AVM module selection, dependency graph)
  - 06-deployment-summary.md (what-if results, resource counts)
  - 07-*.md (as-built suite: design doc, runbooks, inventory)
  - 08-compliance-report.md (policy compliance, drift, secure score)
  - 09-remediation-log.md (auto-remediation audit trail)

**Capability:** Full audit trail and as-built documentation, auto-generated and linked to code.

---

## 2. STRONGEST CAPABILITIES

### Tier 1: Enterprise-Ready Orchestration
1. **Multi-agent coordination** with approval gates—scales from simple (1 region) to complex (hub-spoke, multi-region, multi-env)
2. **Semantic Kernel integration** allows agents to reason about architecture trade-offs, not just templating
3. **State persistence** across multi-hour workflows with resume capability
4. **Approval gate enforcement** at 6 critical decision points—no automatic merges

### Tier 2: Brownfield-Specific Differentiators
1. **Read-only discovery** of existing estates (no mutations during assessment)
2. **WAF-aligned assessment** (221 checks, all 5 pillars) produces scored findings
3. **Gap analysis** from current-state to target-state with remediation roadmaps
4. **Dual-track support** (Bicep + Terraform) so teams aren't forced to rewrite IaC

### Tier 3: Operations & Compliance
1. **Security baseline enforcement** (non-negotiable 6 rules)
2. **Continuous monitoring** (compliance every 30 min, drift every hour, full audit daily)
3. **Auto-remediation** with snapshot/rollback (8 built-in strategies)
4. **Cost governance** with budget enforcement and parameterized thresholds

---

## 3. CRITICAL LIMITATIONS & GAPS

### A. Incomplete Agent Implementations
- **Design agent** (Artisan) has skeleton code—diagram generation not fully integrated
- **Documentation agent** (Chronicler) incomplete—TDD generator exists but agent orchestration missing
- **Terraform code generator** (Forge) not yet implemented—Bicep track is primary

### B. No Live Deployment Validation
- **What-if planning** exists, but post-deployment validation minimal
- **Drift detection** framework exists, but not integrated into continuous monitoring loop

### C. Limited IaC Coverage
- **Bicep:** 22 files covering main design areas; **Terraform:** only 9 files (incomplete parity)
- **App LZ support:** Exists in CI/CD, but no reference architectures for app-tier patterns
- **Hub-spoke networking:** Implemented; VWAN support incomplete

### D. Documentation Gaps
- **No runbooks** for day-2 troubleshooting (monitoring/remediation workflows)
- **APRL sync** mentioned in planning docs but not implemented
- **Migration runbook** (brownfield→greenfield transition) missing

### E. Testing & Validation
- **13 test files** exist; coverage incomplete for agents and tools
- **No end-to-end deployment tests** in CI/CD
- **Validator scope:** security baseline and cost governance; missing compliance validator

---

## 4. DIFFERENTIATORS FROM COMPETITORS

### A. Agentic Workflow (Not Templating)
- **vs. standard ALZ reference implementations:** Agents reason about trade-offs, not just template params
- **vs. IaC-only tools:** Full lifecycle orchestration (discover→design→validate→deploy→monitor)

### B. Brownfield-First Design
- **vs. greenfield-only accelerators:** Step 0 assessment feeds all downstream decisions
- **vs. manual discovery tools:** Automated + scored against WAF/CAF

### C. Enforcement Without Friction
- **Security baseline:** Prevents bad code at code-gen time, not at deployment time
- **Cost governance:** Budget enforcement; no surprise overspends
- **Approval gates:** Human decision points at critical gates; AI operates between gates

### D. Dual-Track IaC (Bicep + Terraform)
- **vs. single-track accelerators:** Teams aren't forced to switch frameworks
- **Architectural parity:** Same design, different codegen output

---

## 5. EVIDENCE-BASED VALUE PROPOSITION (Draft)

**The Agentic ALZ Accelerator transforms Azure Landing Zone delivery from a 6-month, error-prone manual process into an automated, governed, continuously-monitored workflow—with 6 approval gates and non-negotiable security/cost baseline.**

### Key Claims (Evidence-Backed)

| Claim | Evidence |
|-------|----------|
| **Automated workflow orchestration** | 9 agents + DAG engine + 8 CI/CD workflows |
| **Brownfield-aware** | Step 0 assessment (221 WAF checks, read-only discovery) |
| **Enforcement, not guidance** | 6 security baseline rules + cost governance + approval gates |
| **Dual-track IaC** | Bicep (22 files) + Terraform (9 files) with architectural parity |
| **Full lifecycle** | Discover→Design→Validate→Deploy→Monitor→Remediate (Steps 0-9) |
| **Audit trail** | 9 generated artifacts per deployment + continuous compliance logs |

### Value to Different Personas

1. **Enterprise Architects:** WAF-aligned assessment (221 checks, all 5 pillars) + ADR generation
2. **Platform Teams:** Single orchestration entry point; approval gates at critical decisions
3. **Security Teams:** Security baseline enforcement (non-negotiable); continuous compliance monitoring
4. **Finance Teams:** Cost governance (no hardcoding; parameterized budgets)
5. **Operations Teams:** Day-2 operations (monitoring + auto-remediation with audit trail)

---

## 6. PROBLEM STATEMENT (Candidate)

### As-Is
- **Manual ALZ deployments:** 6 months, error-prone, no audit trail
- **Brownfield assessments:** Custom scripts, no WAF alignment, no remediation roadmaps
- **IaC track lock-in:** Choose Bicep or Terraform; switching requires rework
- **Security gaps:** Baseline rules exist; enforcement is after-the-fact
- **Cost surprises:** Budgets set by policy; no deployment-time prevention

### To-Be
- **Automated orchestration:** Requirements→Design→Validate→Deploy→Monitor (days, not months)
- **Scored brownfield assessment:** 221 WAF checks, current-state/target-state gap, remediation roadmap
- **Dual-track IaC:** Same architecture; choose Bicep or Terraform (no rework)
- **Proactive security:** Non-negotiable rules at code-gen time; no bad code merges
- **Cost control:** Budget enforcement at deployment gate; no surprises

---

## 7. RECOMMENDATIONS FOR YESELAM

### A. For Value Proposition Refinement
1. **Lead with brownfield capability** — most competitors lack this; it's a key differentiator
2. **Emphasize "approval gates"** — resonates with enterprise; shows governance discipline
3. **Quantify cost of ALZ delay** — "6 months manual" vs. "days automated" is compelling

### B. For Problem Statement
1. **Focus on two customer jobs:** (1) Brownfield assessment of existing estates, (2) Greenfield deployment with enforced governance
2. **Avoid over-claiming** — Terraform track incomplete; document clearly
3. **Highlight gaps** — transparency builds trust (e.g., "Design/Documentation agents in progress")

### C. For Go-to-Market
1. **Brownfield first:** Start with assessment + remediation roadmap; deploy later
2. **Reference deployment:** Marekgroup example in repo—show it end-to-end
3. **Security + cost story:** Non-negotiable baseline + budget enforcement = CFO-friendly

---

## 8. REPO HEALTH SNAPSHOT

| Dimension | Status | Evidence |
|-----------|--------|----------|
| **Agents** | 9/14 implemented | Orchestrator, Assessment, Governance fully working; Design/Documentation/Terraform partial |
| **Skills** | 35+ defined | Comprehensive coverage of CAF design areas, security, cost, IaC patterns |
| **IaC Bicep** | Production-ready | 22 files, CAF-aligned, AVM-first, security baseline enforced |
| **IaC Terraform** | Beta | 9 files, incomplete module parity with Bicep |
| **Tests** | 13 files, ~50% coverage | Core logic tested; agent orchestration gaps |
| **CI/CD** | 8 workflows | Complete from bootstrap to monitor; deployment validation minimal |
| **Documentation** | Good coverage | Architecture docs exist; day-2 runbooks missing |
| **MCP Integration** | Complete | 3 servers (pricing, platform, drawio) fully wired |

---

## 9. KEY LEARNING FOR BROWNFIELD ASSESSMENT (My Domain)

**Discovery is read-only by design.** The assessment agent doesn't mutate live state—it reads via Azure APIs and generates reports. This is crucial for brownfield scenarios where customers need a "no risk" evaluation before committing to remediation.

**WARA assessment is the bridge.** The 221-check catalog maps to WAF pillars and CAF design areas. This alignment is what allows downstream agents (Architecture, Planning, Code Gen) to make informed decisions from assessment outputs.

**Current-state + Target-state + Roadmap = Decision Support.** The three-artifact model (current-state MD, target-state MD, remediation roadmap MD) gives customers enough data to decide what to fix and when.

---

## NEXT STEPS FOR TEAM

1. **Verify** these findings against your customer feedback
2. **Refine** the problem statement and value prop based on market focus
3. **Prioritize** gaps (Terraform track vs. Design agent vs. day-2 runbooks)
4. **Package** for customer conversations (avoid exposing tool/agent internals; focus on outcome)


## Pass 1 Design/Documentation Contract Fixes (2026-05-13)

### 2026-05-13T16:13:48.828+00:00: Design Flow Review — Step 3 Findings

**By:** Basher

**What:** Comprehensive audit of Step 3 (Design / Artisan) workflow across all input artifacts: `design.md`, `04-design.prompt.md`, `docs/workflow.md`, AGENTS.md, `copilot-instructions.md`, `markdown.instructions.md`, and diagram skills. Identified 8 findings across artifact naming, skip criteria, Challenger review gaps, skill loading, and diagram completeness enforcement.

**Key Findings (Highest-Value, Ranked by Severity):**

1. **[HIGH] Step 3 "Optional" with no defined skip criteria** — No definition of what "simple" means; Step 7 has no fallback when diagrams are absent.
2. **[HIGH] Artifact naming is inconsistent across five documents** — ADR paths conflict (`03-design-adr-*.md` vs `adr/ADR-*.md`); diagram paths conflict (root vs subdirectory).
3. **[HIGH] Design artifacts have no Challenger gate review** — No adversarial check between Gate 2 and Gate 3.
4. **[MEDIUM] `04-design.prompt.md` is severely underspecified vs `design.md`** — Prompt is ~30 lines; agent is 200+ lines with a 4-phase workflow.
5. **[MEDIUM] Skill loading list omits `azure-diagrams` routing skill** — Agent bypasses routing decision tree.
6. **[MEDIUM] "Use both methods" conflicts with routing skill's decision tree** — No coordination between engine selection and dual-format output.
7. **[MEDIUM] No diagram completeness enforcement mechanism** — No validator script, no gate checklist.
8. **[LOW] Step 7 handoff from Step 3 is underspecified** — No schema defined for `03-design-summary.md`; no fallback when design is absent.

**Recommended Next Actions (Priority Order):**
1. Canonicalize artifact naming in `AGENTS.md` and `markdown.instructions.md`
2. Update `design.md` skill list to include `azure-diagrams` (first) and `azure-adr`
3. Define skip criteria (tie to complexity tier: Simple → skip, Standard/Complex → required)
4. Add self-validation checklist to Phase 2 and Phase 4 of `design.md`
5. Align `04-design.prompt.md` with full agent workflow outputs
6. Document Chronicler fallback in `documentation.md` for absent design artifacts
7. Consider adding design artifact check to Gate 2 Challenger criteria

---

### 2026-05-13T18:47:55.170+00:00: Basher Pass 1 — Step 3 Design Contract

**By:** Basher

**What:** For Basher-owned Step 3 files, the canonical design output contract is:
- `agent-output/{customer}/03-design-summary.md` is the required completion artifact and authoritative Step 3 to Step 7 handoff manifest.
- Diagram artifacts live in `agent-output/{customer}/diagrams/` and use the `03-design-<topic>.{drawio|png|md}` naming pattern.
- ADR artifacts live in `agent-output/{customer}/adr/` and use the `03-design-adr-{NNN}-{slug}.md` naming pattern.
- `azure-diagrams` routes the request before engine selection; Draw.io remains the editable source for architecture diagrams, PNG remains quick-reference, and Mermaid is only used when an inline markdown diagram is explicitly needed.

**Why:** This resolves the internal Step 3 contract mismatch between the design agent definition and the Step 3 prompt without changing shared workflow files owned by other agents.

**Scope:**
- Updated: `.github/agents/design.md`
- Updated: `.github/prompts/04-design.prompt.md`
- Not changed in this pass: shared workflow docs, `AGENTS.md`, `.github/copilot-instructions.md`, Step 7 files

---

### 2026-05-13T18:47:55.170+00:00: User directive

**By:** Yeselam Tesfaye (via Copilot)

**What:** Prefer using Claude Opus 4.6 1M for agent work unless otherwise specified.

**Why:** User request — captured for team memory

---

### 2026-05-13T18:47:55.170+00:00: Pass 1 workflow contract state and naming

**By:** Danny

**What:** Updated the shared workflow contract so Step 3 optionality is tied to complexity, `step_3_status` is explicit (`skipped`, `completed`, `failed`), and shared-doc artifact references use prefix-based validation families (`03-*` and `07-*`) rather than implicit filesystem skip detection.

**Why:** This removes ambiguous Step 3 control flow, adds validation before downstream consumption, and keeps the shared contract aligned with the markdown naming rule without changing specialist-owned agent files in Pass 1.

---

### 2026-05-13T16:13:48.828+00:00: Design/Documentation Flow Risk Review — Isabel (Challenger)

**By:** Isabel (Challenger)

**Verdict:** **DO NOT ADVANCE** to full documentation pipeline until risks 1–4 are resolved. Risk 5 is advisory but should be encoded before the next Standard or Complex deployment.

**Top 5 Material Risks:**

1. **[HIGH] Chronicler's TDD Has a Structural Hole When Step 3 Is Skipped** — If Step 3 is skipped, the TDD's Architecture Overview section has no source material. Operations teams receive a documentation artifact with a structurally hollow section.
2. **[HIGH] Artifact Naming Contract Is Broken Across Three Sources** — Prompt produces different files with different names than agent definition. Downstream agent (Chronicler) has a silent dependency on files upstream agent (Artisan) may never produce.
3. **[HIGH] No Challenger Review Covers Step 3 or Step 7** — Artisan can produce diagrams contradicting the architecture assessment without review. Chronicler can produce compliance summaries misrepresenting security baseline status without gate coverage.
4. **[HIGH] Chronicler Lacks MCP Tools Required to Fulfill Its Own Mandate** — Instructed to query live Azure Resource Graph but not equipped with MCP tool. Will silently fall back to reading artifact files only — documenting intended state, not actual deployed state.
5. **[MEDIUM] Step 3 Skip Is an Untracked Branching Condition** — Session state schema does not include `step_3_status` field. Chronicler guesses from filesystem. Mid-run failure is indistinguishable from intentional skip.

**Minimum Change Set (Must-Fix + Should-Fix):**
- Reconcile artifact naming; adopt `agent-output/{customer}/03-design-summary.md` as Artisan's required artifact
- Fix Chronicler's TDD fallback when `03-design-summary.md` is absent
- Add `mcp` to Chronicler tool inventory OR explicitly document live queries are delegated to Sentinel
- Add session state flag `step_3_status` (Orchestrator writes `"skipped"` or `"completed"`)
- Add Challenger review slot for Step 3 design artifacts (should-fix)
- Define and enforce "optional" criteria tied to complexity tier (should-fix)

---

### 2026-05-08T23:06:54.000+00:00: PR #63 Lint Failure Diagnosis

**By:** Reuben (IaC Planner)

**What:** Trailing whitespace in `.github/workflows/squad-heartbeat.yml`:
- Lines 60, 66, 75, 91, 97: trailing spaces

**Root Cause:** YAML lint failure on `yamllint -c .yamllint.yml` check

**Recommendation:** Remove trailing whitespace from identified lines

**Impact:** Blocks PR #63 merge; Severity: Low (formatting only); Fix effort: Minimal

---

### 2026-05-13T16:13:48.828+00:00: Step 7 Documentation Flow — Findings (Tess)

**By:** Tess (Documentation)

**What:** Full fan-out review of Step 7 (Chronicler) documentation workflow focusing on dependency on Step 3 design outputs. Reviewed: `documentation.md`, `08-as-built.prompt.md`, `docs/workflow.md`, `AGENTS.md`, `docs-writer/SKILL.md`, `azure-diagnostics/SKILL.md`.

**Key Findings (Ranked by Severity):**

1. **[HIGH] Output file names are inconsistent** — Agent definition promises different files than prompt. Naming conflict across `documentation.md`, `08-as-built.prompt.md`, `AGENTS.md`.
2. **[HIGH] Step 3 design outputs have no graceful-degradation path** — Agent references Step 3 diagrams in TDD without providing fallback. If Step 3 skipped, agent has no instruction.
3. **[HIGH] Prerequisites block does not match what the prompt actually reads** — Agent definition vs prompt have divergent read behaviors; prompt adds Resource Graph query not in agent.
4. **[HIGH] WARA compliance summary promised in prompt but absent from agent** — Prompt promises per-pillar WARA pass/fail; agent definition does not cover it.
5. **[MEDIUM] Artifact output path is ambiguous** — `agent-output/{customer}/deliverables/` vs `agent-output/{customer}/` (flat).
6. **[MEDIUM] "Cost baseline" artifact defined only in prompt, not in agent** — Prompt lists `07-cost-baseline.md`; agent collapses it into TDD section.
7. **[MEDIUM] Skills loaded by agent inconsistent with prompt** — `docs-writer` not loaded by agent despite containing output naming conventions.
8. **[LOW] No explicit handoff signal from Step 7 to Steps 8–9** — No documentation on what Sentinel reads from Step 7 to initialize baseline.

**Recommended Target-State Output Manifest:**
- `07-technical-design-document.md` — Full as-built architecture
- `07-operational-runbook.md` — Day-2 ops procedures
- `07-resource-inventory.md` — Tabular inventory from Resource Graph
- `07-compliance-summary.md` — Security baseline + WARA (if brownfield) + policy summary
- `07-cost-baseline.md` — Budget config + estimated monthly cost

All written to: `agent-output/{customer}/deliverables/`

---

### 2026-05-13T18:47:55.170+00:00: Step 7 documentation contract canonicalized

**By:** Tess

**What:** Canonicalized the Step 7 documentation contract in `.github/agents/documentation.md` and `.github/prompts/08-as-built.prompt.md` around a single output path and file set: `agent-output/{customer}/deliverables/07-technical-design-document.md`, `07-operational-runbook.md`, `07-resource-inventory.md`, `07-compliance-summary.md`, and `07-cost-baseline.md`. Also defined explicit Step 3 fallback behavior and clarified that Step 7 uses both deployed-state evidence from Step 6 and artifact-derived context from earlier approved steps.

**Why:** The agent definition and prompt had drifted into incompatible contracts, which caused naming ambiguity, missing-diagram risk when Step 3 is skipped, and unclear expectations about whether Step 7 performs live-state discovery or documents workflow evidence.

---

### 2026-05-08T23:37:53.627+00:00: User directive

**By:** Yeselam Tesfaye (via Copilot)

**What:** Before making a change, always check which branch you are on first.

**Why:** User request — captured for team memory

========================
MISSION
========================
Enhance the current agentic ALZ accelerator to:
1) Support brownfield (existing environment) scenarios end-to-end
2) Add an assessment feature that produces actionable recommendations aligned to:
   - Azure Well-Architected Review / WARA-style design and reliability signals (and other pillars where applicable)
   - Cloud Adoption Framework (CAF) assessment-style outputs (strategy/plan/ready/adopt/govern/manage + organizational alignment)

ALSO REQUIRED (NEW):
3) Document the CURRENT STATE architecture (as discovered from repo + optional live discovery outputs) including:
   - A current-state architecture diagram (Mermaid)
   - A current-state architecture document in Markdown describing components, flows, scope, assumptions, and gaps
   - Separate “Current State” vs “Target State” sections

========================
SKILLS & EXPERTISE (MUST APPLY)
========================
- Azure Landing Zones (ALZ) design areas: identity, management groups, subscriptions, policy, RBAC, networking, logging/monitoring, security, platform DevOps
- Brownfield adoption patterns: discover, align, adopt, minimize disruption, drift detection, coexistence strategies
- Azure governance: Policy, initiatives, remediation tasks, role assignments, tagging, budgets
- Observability: Log Analytics, diagnostic settings, Azure Monitor, alerts, Sentinel (optional)
- Security: Defender for Cloud, secure score signals, least privilege, secret hygiene
- Assessment frameworks: Well-Architected pillars + CAF mapping and backlog generation
- Repo engineering: incremental, testable changes; docs-first and code-first balance
- Documentation: crisp Markdown, ADR format, Mermaid diagrams suitable for GitHub rendering

========================
AGENTS (WORK TOGETHER; OUTPUT ONE CONSOLIDATED RESULT)
========================
Agent A — Principal ALZ Architect:
- Minimally extend repo architecture; preserve conventions; define target state

Agent B — Brownfield Adoption SME:
- Define brownfield discovery, drift-aware planning, adopt/align modes, non-disruptive remediation patterns

Agent C — WARA/Well-Architected + CAF Assessor:
- Define rules model, severity rubric, evidence model, mappings to WAF pillars + CAF areas + ALZ areas

Agent D — DevOps/Automation Engineer:
- Wire CLI/scripts + GitHub Actions workflows; add SARIF option; ensure repeatability and guardrails

Agent E — Security Reviewer:
- Ensure least privilege, safe defaults, and non-destructive operations; add gating flags for remediation

Agent F — Technical Writer:
- Produce /docs current-state architecture doc, target-state doc, operator guide, and ADR(s)

========================
OPERATING PRINCIPLES (REPO-FIRST)
========================
- Read repository structure and existing patterns FIRST.
- Do not invent a new architecture if one exists; extend what’s there.
- Prefer small, reviewable PR-sized changes.
- Default to SAFE and READ-ONLY behavior in brownfield unless explicit flags allow remediation.
- Avoid tenant-wide destructive operations; no secret sprawl; keep permissions minimal.

========================
BROWNFIELD DEFINITION & SUCCESS CRITERIA
========================
Brownfield means the tenant may already have:
- Existing MG hierarchy (possibly non-ALZ), existing subscriptions, multiple BU patterns
- Existing Policy assignments/initiatives, RBAC, budgets, tags
- Existing hub/spoke VNets, firewalls, private DNS, private endpoints
- Existing Log Analytics, Sentinel, Defender for Cloud settings
- Existing CI/CD pipelines and service connections
- Partial ALZ adoption (some landing zones built)

Success criteria:
- Safe discovery before changes
- Drift-aware plan: what exists vs desired; show deltas
- Idempotent deployments and minimal disruption
- Support adopt/align mode (coexist + gradual convergence) vs replace
- Clear migration steps, risk notes, rollback guidance

========================
ASSESSMENT FEATURE REQUIREMENTS
========================
Implement an “Assess” capability that:
A) Discovers current state (read-only) and builds baseline inventory:
   - MG hierarchy, subs, policies, role assignments, networking, logging/monitoring, security posture
B) Runs assessment rules to output:
   - Findings (severity, impact, evidence, affected scope, confidence)
   - Recommendations (short + detailed)
   - Mappings:
       * Well-Architected pillar(s)
       * CAF areas (strategy/plan/ready/adopt/govern/manage + org alignment)
       * ALZ design areas (identity, mgmt groups, policy, networking, logging, security, platform devops)
C) Produces artifacts:
   - Markdown report(s): /docs/assessments/
   - JSON output: /outputs/assessments/
   - OPTIONAL SARIF: /outputs/assessments/*.sarif for GitHub code scanning
D) Supports modes:
   - assess-only (no changes) [DEFAULT]
   - assess-and-plan (generates plan + PR checklist + backlog)
   - assess-and-remediate (optional; gated; requires explicit flags)
E) Works for both greenfield and brownfield.

Preferred approach:
- Extensible rules model: rule_id, title, description, severity, confidence, scope, evidence collectors, evaluation logic, recommendation, mappings, remediation steps, references
- Separate “collect evidence” from “evaluate rules”
- Config-driven and scope-aware (tenant/MG/sub/resource group)

========================
CURRENT STATE ARCHITECTURE DOCUMENTATION (NEW DELIVERABLES)
========================
You must document the CURRENT STATE as it exists TODAY in this repo (and any discovered outputs).
Deliver:
1) /agent-output/{customer}/architecture/current-state.md
   - Overview: What this accelerator is, what it deploys, how it’s run
   - Component inventory: modules, pipelines, scripts, config, artifacts
   - Data flows: discovery -> plan -> deploy -> validate -> report
   - Security model: identities/permissions/service principals/OIDC, secrets handling
   - State & storage: where state lives, artifacts, logs, reports
   - Known constraints and gaps (especially for brownfield and assessments)
   - Assumptions and non-goals
2) /agent-output/{customer}/architecture/current-state-diagram.mmd (Mermaid)
   - Provide at least 1 diagram: high-level system context + execution flow
3) /agent-output/{customer}/architecture/target-state.md
   - Summarize intended end-state with brownfield + assessment feature included
   - Clearly list what changes and what remains unchanged
4) Add an ADR: /agent-output/{customer}/adr/ADR-xxxx-brownfield-assessment.md
   - Decision, options considered, tradeoffs, security & operational impact

Diagram requirements:
- Use Mermaid syntax that renders in GitHub.
- Include: operator (engineer), GitHub repo, workflows/actions, discovery module, rules engine, report generator, Azure APIs (ARM/ARG/Graph), Azure scopes (tenant/MG/sub), artifact outputs.

========================
DELIVERABLES (CODE + DOCS)
========================
1) Design doc/ADR(s) describing brownfield + assessment architecture
2) Implementation plan as an ordered task list
3) Code changes:
   - Discovery module(s) (inventory collectors)
   - Assessment rules engine (extensible)
   - Report generator (md/json/sarif)
   - Config schema updates (brownfield + modes)
   - CLI/workflow entry points (scripts + GH Action)
4) Example configs + sample outputs
5) Operator guide (how to run, permissions, troubleshooting)
6) Tests/validation (rules unit tests and/or fixtures)

========================
EXECUTION INSTRUCTIONS (DO THIS IN ORDER)
========================
Step 1 — Repo inspection:
- Summarize repo structure, entrypoints, IaC tech (Terraform/Bicep/mixed), pipelines, modules.
- Identify current architecture patterns and any existing docs/diagrams.
- Identify any existing discovery or assessment logic.

Step 2 — Current state documentation (WRITE FIRST):
- Generate /agent-output/{customer}/architecture/current-state.md
- Generate /agent-output/{customer}/architecture/current-state-diagram.mmd (Mermaid)
- Capture gaps and risks especially around brownfield adoption and assessments.

Step 3 — Target state design (MINIMAL CHANGE):
- Propose a brownfield extension design that fits existing structure.
- Propose assessment feature architecture (modules/interfaces/data model).
- Add ADR with decisions + tradeoffs.

Step 4 — Implement incrementally:
- Implement discovery collectors (read-only).
- Implement rules engine + sample rules.
- Implement report generation (md/json; sarif optional).
- Add modes + gating flags.
- Add docs + examples + tests.

Step 5 — Provide final summary:
- List files added/changed.
- Provide usage examples and expected outputs.
- Provide security and permission requirements (least privilege).
- Provide rollback guidance for any remediation mode.

If something is ambiguous, ask up to 3 focused questions; otherwise proceed with reasonable defaults that match repo conventions.
``
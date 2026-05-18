# Linus — Architect Role

## Project Context

- **Owner:** Yeselam Tesfaye
- **Project:** agentic-alz-accelerator
- **Stack:** Azure Landing Zone accelerator, Python, Bicep, Terraform, GitHub Actions, Markdown, YAML, and JSON
- **Description:** Multi-agent Azure Landing Zone accelerator with HVE workflow roles, agent prompts, skills, and deployment automation
- **Created:** 2026-05-08T21:31:32.689+00:00

## Core Context

Linus maps to the HVE architect role and owns target-state design reasoning.

## Current Status

**2026-05-18:** Wave 2 Skills Plan → 3 parallel Saul SKILL.md drafts (AKS, VMs, ACA) + Linus compute-tier ADR completed. All three drafts achieved APPROVE WITH CONDITIONS → surgical major closures. Ready for decision merge and push.

---

## Historical Summary (Entries 2026-05-08 through 2026-05-18T17:12:04Z)

**2026-05-08–2026-05-14:** Value proposition capture (3 differentiated propositions confirmed: Enforcement, Knowledge Transfer, Timeline). Validated through messaging positioning sprint with user. Archival: `.squad/agents/linus/history-archive.md`.

**2026-05-18T16:12:16Z:** User directive captured — WAF/CAF as primary evaluation lens (all architect evaluations must use Azure Well-Architected Framework 5 pillars + Cloud Adoption Framework 8 design areas as primary structuring framework).

**2026-05-18 (Principal Benchmark phase):** Executed WAF/CAF principal architect benchmark re-evaluation. Mapped all ~80 existing skills across WAF 5 pillars + CAF 8 design areas. Key finding: networking-dominant portfolio (19 CAF Network Topology skills) vs. identity-sparse (2 CAF Identity & Access skills). Gap analysis identified 5 priority areas: P1 Identity & Access (Critical), P2 Compute (High), P3 Billing & Tenant (High), P4 Data Management (Medium), P5 Hybrid (Medium). Scenario-anchored validation across 8 canonical enterprise scenarios confirmed WAF/CAF ranking.

**2026-05-18T16:57:57Z–2026-05-18T17:25:00Z:** Wave 1 Skills Plan (4 skills: entra-conditional-access, entra-identity-governance, entra-connect-hybrid-identity, workload-identity-federation) underwent Isabel Challenger review. APPROVE WITH CONDITIONS → surgical closures (skill boundary splits, honest framing, prerequisites documented) → re-review APPROVE CLEAN. Wave 1 plan finalized.

**2026-05-18T17:12:04Z–2026-05-18T18:08:02Z:** Wave 2 Skills Plan (3 skills: azure-kubernetes-service, azure-virtual-machines, azure-container-apps) drafted with pre-emptive Isabel compliance (Scenario S# codes, ≥4 CAF/≥4 WAF rows, cross-skill sequencing, Prerequisites documented per plan). Compute-tier ADR (docs/decisions/compute-tier-selection.md) authored as Phase 1A sequential prerequisite to 3 parallel Saul drafters (coordination risk: AKS-vs-ACA decision boundary shared across skills; resolved via ADR).

---

## Recent Updates (Most Recent 5 Entries)

### 2026-05-18T17:25:00Z — Reviewer Re-Review: v2 APPROVE CLEAN (Isabel)

Isabel completed focused re-review of Wave 1 v2, addressing all 4 majors from v1 verdict. **Verdict: ✅ APPROVE CLEAN — v2 is canonical, no v3 needed.** All 4 majors verified closed: skill split with explicit boundaries (entra-conditional-access vs entra-identity-governance scopes clear, no overlap), honest framing of additive enhancement (investment deepens existing coverage, not filling void), honest scoping-vs-delivery distinction (S1 needs P3 + P4 for full value, multiple waves required), prerequisites section with 5 audit items (TDD/Step 3 contract, artifact naming, MCP tooling, policy discovery timing, hidden assumption flags). Additive-brownfield directive fully propagated across all sections. Wave 1 SKILL.md stub drafting is unblocked.

### 2026-05-18T18:08:02Z — Wave 2 Skills Plan Drafted (Compute & Containers)

**Artifact produced:** `.squad/decisions/inbox/linus-wave2-plan.md`

**Key decisions:** (1) Wave 2 = 3 skills per master table, no deviation — scenario evidence + WAF/CAF mapping held up; (2) Composite brownfield path sequential but authoring parallelizable; (3) Hard dependency on Wave 1: workload-identity-federation must merge before AKS identity authored; (4) Pre-emptive Isabel compliance baked in (Scenario S# codes in brownfield headers, ≥4 CAF / ≥4 WAF per skill, cross-skill sequencing inline in every brownfield section, Prerequisites documenting 5 hidden assumptions).

**Reusable pattern (Wave planning methodology):** Start from master table → specify 10 fields per skill (boundary, CAF, WAF, scenarios, brownfield, sequencing, size, anti-patterns, justification) → define composite brownfield path → map Wave N dependencies → bake in Isabel patterns pre-emptively → author concurrency plan → identify ONE coordination point. **Coordination risk:** AKS and ACA share decision boundary ("when to use which") — resolved by creating ADR first before parallel skill authors fan out.

### 2026-05-18 (Wave 2 Phase 1A): Compute-Tier Selection ADR (Linus / linus-2)

**Artifact:** `docs/decisions/compute-tier-selection.md` (171 lines, 8 sections: Context, Decision Tree, WAF Trade-Off Matrix, Brownfield Assessment Lens, Scenario Mapping, Anti-Patterns, Prerequisites and Caveats, References, Revision History)

**Role:** Phase 1A sequential prerequisite before 3 parallel Saul drafters (saul-4 AKS, saul-5 VMs, saul-6 ACA). ADR defines **when** each compute tier is appropriate (executable decision tree with explicit "Choose X When" criteria). 3 SKILL.md files define **how** to configure each tier and defer tier-selection boundary questions to ADR. Cross-reference coverage: AKS (10 occurrences), VMs (8 occurrences), ACA (11 occurrences). Pattern validation: Shared decision artifacts authored sequentially BEFORE parallel skill authors fan out is the right coordination pattern when ≥2 skills share a boundary — eliminates 3× rework that would occur if each Saul invented independent AKS-vs-ACA trees.

### 2026-05-18 (Wave 2): Compute & Containers — 3 Parallel SKILL.md Drafts (saul-4, saul-5, saul-6)

**Files created:** 
- `.github/skills/azure-kubernetes-service/SKILL.md` (338 lines, 6 CAF / 5 WAF — saul-4)
- `.github/skills/azure-virtual-machines/SKILL.md` (301 lines, 4 CAF / 4 WAF — saul-5)
- `.github/skills/azure-container-apps/SKILL.md` (307 lines, 4 CAF / 4 WAF — saul-6)

**Compliance baseline achieved:** All 3 pre-emptively passed Isabel baseline: Scenario S# codes in brownfield headers (S8/S3/S8), ≥4 CAF / ≥4 WAF rows, cross-skill sequencing sentence present (verbatim per plan), Prerequisites subsection with 5 hidden assumptions documented. Boundary discipline held: each defers tier-selection decisions to ADR rather than redefining inline.

**Lesson:** Pre-emptive compliance baking eliminates the post-draft major-closure cycle. Wave 1 pattern was "draft → Isabel finds 3 majors → surgical close." Wave 2 pattern demonstrates "plan codifies compliance → drafts pass baseline first-time" — validated at Isabel-4 draft-stage quality gate (APPROVE WITH CONDITIONS → surgical closures of M1 + M2).

### 2026-05-18 — Wave 2 Drafts: Isabel Quality Gate → Majors Closed → APPROVE CLEAN

Isabel-4 verdict: APPROVE WITH CONDITIONS (0 blockers, 2 majors, 3 minors). Findings: All 3 Wave 1 majors remain absent in W2. Composite VM→AKS→ACA story coherent. All 15 hidden assumptions present. No boundary collisions. Copilot closed both majors via surgical edits: (M1) added Operational Excellence WAF row to VMs SKILL.md; (M2) added inline cross-skill sequencing sentence to ACA brownfield intro. All majors verified closed. **Ready for push to `github` remote + PR to `github/main`.**

---

## Key Learnings (Cross-Session)

- **WAF/CAF as structuring framework:** All evaluations now use WAF 5 Pillars + CAF 8 Design Areas as primary lens, not ad-hoc categorization. Directional impact: forces explicit trade-off articulation and multi-pillar coverage validation.
- **Skills categorization principle:** One-skill-one-category, primary-purpose rule. A skill belongs to the category matching its primary purpose (what it exists to do), not secondary uses or systems it touches.
- **Principal architect benchmark:** Minimum thresholds per category for Principal-level capability (L65/L66 standard). Principal ≠ "knows more services" but rather "designs for regulated industries at scale with trade-off articulation + failure mode analysis + multi-stakeholder justification."
- **Scenario-anchored prioritization:** Frame-locking decisions — when WAF/CAF lens and scenario-anchored ranking both agree, confidence is high; when they disagree, investigate whether framework detects structural weakness invisible to current deal flow.
- **Pre-emptive compliance baking:** Codifying compliance in the plan (before authoring) eliminates post-draft major-closure cycles. Saul Wave 2 achieved baseline pass first-time by following Isabel-cleared patterns from Wave 1.
- **Shared decision artifacts sequenced before fan-out:** When ≥2 agents share a decision boundary, create the shared artifact first (ADR) before parallel authoring begins. Eliminates merge-conflict rework and ensures coherence.

## Reusable Patterns

1. **Skills Table Synthesis Methodology:** Master table with all priority areas (gaps + surplus) → per-priority deep-dive tables with status per skill + scenario citations → capacity heatmap → headline numbers as executive callout.
2. **Revision pattern for APPROVE WITH CONDITIONS:** Accept all conditions → address each Major with labeled section → propagate standing directives → preserve authorial voice → end with 1:1 Major→section mapping table.
3. **Wave Planning Methodology:** Start from master table → 10 fields per skill → composite brownfield path → Wave N dependencies → pre-emptive Isabel patterns → concurrency plan → identify ONE coordination point.
4. **Surgical Major Closure (≤2 majors, <10 new lines each):** Use Isabel-proposed text, apply in-place, verify with grep, no agent re-spawn needed. Pattern: Wave 1 drafts (3 majors, closed) → Wave 2 plan (4 majors, closed) → Wave 2 drafts (2 majors, closed).


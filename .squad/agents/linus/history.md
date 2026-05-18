# Project Context

- **Owner:** Yeselam Tesfaye
- **Project:** agentic-alz-accelerator
- **Stack:** Azure Landing Zone accelerator, Python, Bicep, Terraform, GitHub Actions, Markdown, YAML, and JSON
- **Description:** Multi-agent Azure Landing Zone accelerator with HVE workflow roles, agent prompts, skills, and deployment automation
- **Created:** 2026-05-08T21:31:32.689+00:00

## Core Context

Linus maps to the HVE architect role and owns target-state design reasoning.

## Recent Updates

📌 Team hired on 2026-05-08T21:31:32.689+00:00 by Yeselam Tesfaye

## Current Status

**2026-05-18:** Messaging positioning sprint completed. Three value propositions confirmed and decision merged to `.squad/decisions.md`. Awaiting Yeselam validation before sprint slice execution (S1: problem audit + value prop analysis).

## Key Learnings

**Three Differentiated Value Propositions (Confirmed across 2026-05-08 to 2026-05-14):**

1. **Enforcement (PRIMARY):** Three-tier (code → deploy → monitor+remediate)
   - Code-gen validators: 6 security rules + cost governance block PRs
   - Deployment gates: What-if preview + complexity-scaled approval
   - Continuous ops: 30-min compliance scans, 1-hr drift detection, auto-remediation with rollback
   - Unique vs ALZ: Official ALZ provides templates; we enforce compliance post-deployment continuously

2. **Knowledge Transfer (SECONDARY):** Algorithmic documentation with CAF traceability
   - Brownfield assessment (Step 0): Current-state + WAF/CAF evaluation + target-state roadmap
   - Greenfield workflow (Steps 1-7): Generated artifacts (requirements → architecture → design → code → deployment → docs)
   - CAF design area traceability: 8 areas mapped through every artifact end-to-end
   - Unique vs ALZ: Official ALZ is greenfield reference; we generate as-built docs + assess existing estates algorithmically

3. **Timeline (TERTIARY):** Parallelized orchestration with complexity-scaled gates
   - Concurrency: Design (Step 3) and Governance (Step 3.5) run parallel after Gate 2
   - Complexity tiers: Simple (1× pass), Standard (2×), Complex (3×)
   - AVM-first generation prevents rework loops
   - Impact: 8–12 weeks (manual) → 2–4 weeks (orchestrated)

**Messaging Strategy:** Lead with enforcement (broadest TAM: compliance/security teams), secondary knowledge (differentiates from generic IaC), tertiary speed (bonus for delivery teams).

**Full positioning analysis:** Archived to `.squad/agents/linus/history-archive.md`

## Learnings

**WAF/CAF as Primary Evaluation Lens (2026-05-18):**

Per standing directive `copilot-directive-2026-05-18T161216Z.md`: All architect evaluations now use WAF 5 Pillars + CAF 8 Design Areas as the structuring framework — not ad-hoc skill categories. Key insight: The categorical view ("Azure Infra meets at 21") masked that 19/21 skills served a single CAF design area (Network Topology & Connectivity) while Identity & Access had only 2. Count-based metrics without framework alignment create false confidence. The prior "Wave 1 = Arc" priority was solving a secondary problem while the structural gap (Identity & Access = 2 skills for a foundational CAF design area) went unnamed. Pattern: whenever a category "meets" by count, validate coverage ACROSS the frameworks it maps to — count without distribution is meaningless.

Decision reference: `.squad/decisions/inbox/linus-principal-benchmark-waf-caf.md`

**Skills Categorization Principle (2026-05-18):**

One-skill-one-category, primary-purpose rule: A skill belongs to the ONE category that describes its primary purpose — what it exists to do, not what systems it touches or which agents invoke it. An Azure service skill (e.g., azure-monitor) belongs in the category matching the service's architectural role (Governance: observability), not the accelerator layer that consumes it (AI Infrastructure). This corrects the prior v1 over-counting of AI Infrastructure by ~6 skills that were actually Azure platform services used BY agents, not agent orchestration skills themselves.

Decision reference: `.squad/decisions/inbox/linus-skills-categorization-v2.md`

**Principal Azure Infrastructure Architect Benchmark Framework (2026-05-18):**

Reference standard for measuring project skill maturity against industry expectations (Microsoft L65/L66 or Principal Consultant at major SI). Minimum thresholds per category:

| Category | Principal Minimum | Key Composition Requirements |
|----------|-------------------|------------------------------|
| Azure Infrastructure | 18–22 | Must span compute+network+storage+identity+database (not monocultural) |
| Governance | 15–20 | Must cover policy authoring, RBAC design, cost governance (FinOps), security posture, observability platform, compliance mapping |
| Landing Zones | 12–16 | Must include CAF/WAF, dual IaC, brownfield assessment, subscription vending, ADR process |
| Hybrid | 8–12 | Must include Arc (servers+K8s+data), hybrid identity, multi-cloud governance, edge compute |
| AI Infrastructure | 10–14 | Must include orchestration, context management, workflow contracts, evaluation, safety (emerging domain — originality > breadth) |

Key differentiator principle: Principal ≠ "knows more services." Principal = designs for regulated industries at scale with trade-off articulation, failure mode analysis, and multi-stakeholder justification. The gap between Senior and Principal is composability under constraint.

Project gap priorities (as of 2026-05-18): Hybrid is the structural deficit (-5 to -9). Azure Infra meets count but is networking-monocultural. Governance and AI Infrastructure are surplus. Landing Zones are stable.

Decision reference: `.squad/decisions/inbox/linus-principal-benchmark.md`

**Scenario-Anchored Prioritization Methodology (2026-05-18):**

Defined 8 canonical enterprise scenarios the accelerator must credibly deliver: (1) Global Landing Zone, (2) Multi-Region AI Platform, (3) Regulated Workloads, (4) Brownfield M&A Integration, (5) ISV Multi-Tenant SaaS, (6) Sovereign Cloud, (7) Hybrid Edge Platform, (8) Cloud-Native Modernization. Evaluated each Priority (P1–P5) against each scenario as Critical/Important/Optional/N/A. Result: scenario-weighted ranking fully confirmed the WAF/CAF ranking (P1 Identity = 6 Critical, P2 Compute = 5 Critical, P3 Billing = 4 Critical, P4 Data = 4 Critical, P5 Hybrid = 2 Critical).

Key insight: scenario-anchored prioritization complements (not replaces) the WAF/CAF lens. Frameworks identify structural gaps; scenarios prove those gaps cost real deals. When both lenses agree, confidence is high — invest without hesitation. When they disagree, investigate whether the framework is detecting a structural weakness invisible to current deal flow, or vice versa.

Decision reference: `.squad/decisions/inbox/linus-scenario-anchored-gap-plan.md`

**Current vs Target Skills Table Synthesis (2026-05-18):**

Methodology for producing a decision-grade "current vs target" artifact: (1) Master table with one row per priority area PLUS saturated/surplus areas for full-picture context — columns must bridge both standing directives (CAF design area + WAF pillar + scenario blast radius in one row). (2) Per-priority deep-dive tables with ✅/❌ status per skill and explicit scenario citations. (3) Capacity heatmap using block characters for at-a-glance portfolio view. (4) Headline numbers as executive callout with quotable bottom line. Pattern: always show BOTH the gap areas AND the surplus areas — showing only gaps without surplus context makes the investment seem larger than it is. The 80 → 93 framing (16% expansion) is more persuasive than "13 skills needed" because it anchors against the existing base. The 10:1 networking-to-identity ratio is the single most compelling data point for explaining the structural imbalance.

Decision reference: `.squad/decisions/inbox/linus-current-vs-target-skills-table.md`

---

### 2026-05-18T17:12:04Z — Revised Skills Table v2 (Post-Isabel Conditions + Additive-Brownfield)

**Artifact produced:** `.squad/decisions/inbox/linus-current-vs-target-skills-table-v2.md`

**Revision pattern (reusable):** When a Challenger issues APPROVE WITH CONDITIONS, the revision workflow is: (1) Accept all conditions without re-litigating the verdict; (2) Address each Major as a labeled section so the reviewer can verify 1:1 mapping; (3) Propagate all standing directives into EVERY section (not just the ones the reviewer flagged); (4) Preserve authorial voice and analytical framing while incorporating constraints; (5) End with an explicit "Reviewer Response" table mapping each Major → section that addresses it. This pattern preserves the architect's ownership of the artifact while demonstrating full compliance with reviewer conditions.

**Additive-brownfield directive impact on skill scoping:** Every new skill must answer "what brownfield scenario does this serve?" — this is not optional decoration but a structural requirement. The insight: identity skills are INHERENTLY brownfield-relevant because identity debt is the universal brownfield problem (every acquired company has over-privileged access, legacy ADFS, inconsistent CA policies). The directive didn't constrain the plan — it strengthened the justification by making the brownfield applicability explicit rather than implicit. Future skill proposals should lead with the brownfield scenario when the skill naturally serves both modes.

**Wave 1 sequencing decision:** The MAJOR-1 split (3→4 skills) creates a cleaner execution boundary: `entra-conditional-access` and `entra-identity-governance` can be authored in parallel by different contributors because their scopes are non-overlapping. This is better than the original monolithic `entra-id-identity-governance` which would have required a single author to cover CA + PIM + access reviews + entitlement management. The split is architecturally correct (different API surfaces, different compliance domains) AND operationally better (parallelizable authoring).

---

### 2026-05-18T16:57:57Z — Reviewer Gate Verdict: Skills Table Expansion (Isabel)

Isabel (Challenger) performed adversarial review of Linus's WAF/CAF Principal Benchmark and Wave 1-5 skill expansion plan. Verdict: **APPROVE WITH CONDITIONS** (No lockout).

**Findings Summary:**
- 0 blockers, 4 majors, 11 minors
- Confirms WAF/CAF prioritization is sound
- Confirms scenario-anchored methodology is valid
- Flags skill scoping issue: `entra-id-identity-governance` conflates 4 distinct Azure services

**Conditional Revisions Required (Majors):**
1. Split `entra-id-identity-governance` → `entra-conditional-access` + `entra-identity-governance` (Wave 1: 3 → 4 skills)
2. Reframe identity count narrative: existing `azure-rbac` contains partial PIM/CA coverage; investment is deepening, not filling void
3. Reframe "unblocks 6/8 scenarios" → "enables scoping phase for 6/8"; full delivery requires multiple waves (S1 needs P3, S2/S5 need P4)
4. Add prerequisites section documenting pipeline assumptions (TDD/Step 3 contract, artifact naming, MCP tooling must resolve in parallel)

**Authority:** Reviewer Gate (Pre-execution). Conditional approval. Linus may revise without escalation.

**Recommended Wave 1 (4 skills):**
| Skill | Scope | Boundary |
|-------|-------|----------|
| entra-conditional-access | CA policies, named locations, authentication strength, cross-tenant, continuous access eval | NOT: PIM, access reviews |
| entra-identity-governance | PIM at scale, access reviews, entitlement mgmt, lifecycle workflows | NOT: CA policies, RBAC |
| entra-connect-hybrid-identity | Cloud sync, ADFS federation, multi-forest, staged rollout, pass-through auth | NOT: AADDS, B2B/B2C |
| workload-identity-federation | AKS pod identity, cross-cloud (AWS/GCP), managed identity at scale | NOT: GitHub OIDC (use entra-app-registration) |

**Next Step:** Linus to revise; resubmit for gate sign-off.

Reference: `.squad/decisions.md` §"Reviewer Gate Decision — Skills Table" for full analysis and hidden assumptions called out.

---

### 2026-05-18T17:25:00Z — Reviewer Re-Review: v2 APPROVE CLEAN (Isabel)

Isabel completed focused re-review of v2, addressing all 4 majors from v1 verdict. **Verdict: ✅ APPROVE CLEAN — v2 is canonical, no v3 needed.** All 4 majors verified closed: skill split with explicit boundaries, honest framing of additive enhancement, honest scoping-vs-delivery distinction, prerequisites section with 5 audit items. Additive-brownfield directive fully propagated. Wave 1 SKILL.md stub drafting is unblocked.

Reference: `.squad/decisions.md` §"Re-Review Verdict — v2 vs v1 Conditions" for full gate analysis and sign-off.

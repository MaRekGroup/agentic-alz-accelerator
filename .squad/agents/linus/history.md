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

**2026-05-19:** Wave 5 (Hybrid) shipped — ADR authored, scope confirmed (arc-servers S6 + arc-kubernetes S8), catalog closed at 14/14.

---

## Historical Summary (W1 through W4 — entries through 2026-05-18)

**2026-05-08–2026-05-14:** Value proposition capture (3 differentiated propositions confirmed: Enforcement, Knowledge Transfer, Timeline). User directive captured: WAF/CAF as primary evaluation lens for all architect evaluations.

**2026-05-18 (Principal Benchmark):** WAF/CAF principal architect benchmark. Mapped ~80 skills across WAF 5 pillars + CAF 8 design areas. Key finding: networking-surplus (19 CAF Network Topology skills), identity-critical gap (2 CAF Identity & Access). Gap analysis identified P1 Identity (Critical), P2 Compute (High), P3 Billing/Tenant (High), P4 Data (Medium), P5 Hybrid (Medium). Scenario-anchored validation confirmed ranking.

**Wave 1 (Identity):** Plan authored (4 skills: entra-conditional-access, entra-identity-governance, entra-connect-hybrid-identity, workload-identity-federation). Isabel APPROVE WITH CONDITIONS → surgical closures → APPROVE CLEAN.

**Wave 2 (Compute & Containers):** Plan authored (3 skills: AKS, VMs, ACA). Compute-tier ADR `docs/decisions/compute-tier-selection.md` authored as Phase 1A sequential prerequisite before parallel Saul fan-out. Pre-emptive Isabel compliance baked into plan. Isabel-4 APPROVE WITH CONDITIONS (2 majors) → surgical closures → APPROVE CLEAN.

**Wave 3 (Tenant Architecture):** Plan authored (2 skills: management-group-architecture S4, subscription-vending S5). Scope pivoted from Billing & Tenant → Tenant Architecture (Yeselam authorized). ADR `docs/decisions/billing-tenant-hierarchy.md` (168 lines, "design vs. automate" framing). Isabel APPROVE WITH CONDITIONS → closed.

**Wave 4 (Data Platform):** Plan authored (3 skills: sql-database S3, cosmos-db S2, storage-accounts S5). ADR `docs/decisions/data-tier-selection.md` (173 lines, SQL/Cosmos/Storage decision tree). Isabel-7 APPROVE WITH CONDITIONS (3 majors, 4 minors) → all closed inline. Skills merged via PR #69. Capacity: 12/14.

## Key Learnings (Cross-Session)

- **WAF/CAF as structuring framework:** All evaluations use WAF 5 Pillars + CAF 8 Design Areas as primary lens.
- **Pre-emptive compliance baking:** Codifying Isabel patterns in the plan eliminates post-draft major-closure cycles.
- **Shared ADR sequenced before fan-out:** When ≥2 agents share a decision boundary, create the ADR first.
- **Scenario-anchored prioritization:** Frame-locking decisions have high confidence when WAF/CAF lens and scenario ranking agree.

## Reusable Patterns

1. **Wave Planning Methodology:** Master table → 10 fields per skill → composite brownfield path → Wave N dependencies → pre-emptive Isabel patterns → concurrency plan → identify ONE coordination point.
2. **Surgical Major Closure:** Use Isabel-proposed text, apply in-place, verify with grep. No agent re-spawn needed for ≤2 majors, <10 new lines each.
3. **Shared ADR Pattern:** Sequential Phase 1A before parallel Phase 2 fan-out. Cross-reference the ADR in 4+ locations per skill.

## 2026-05-19 — Wave 5 (Hybrid)

- **Linus-7 (claude-sonnet-4.6):** Authored plan `.squad/decisions/inbox/linus-wave5-plan.md` (~350 lines, 9/9 PASS). Confirmed scope: `azure-arc-servers` (S6, CAF Management/Governance/Security, WAF OpsEx primary) + `azure-arc-kubernetes` (S8, CAF Platform Automation/Management/Governance, WAF OpsEx primary). ADR: YES (`docs/decisions/hybrid-onboarding-strategy.md`). Key trade-offs: rejected arc-data-services (no scenario anchor); Arc K8s hard prereq on AKS; both skills carry ⛔ HARD GATEs. Description drafts sized ≤1020 chars (hotfix constraint). 5 Open Questions for Yeselam — all answered (S6/S8 codes, MI-first, balanced weighting, new Hybrid section).
- **Linus-8 (claude-sonnet-4.6):** Authored shared ADR `docs/decisions/hybrid-onboarding-strategy.md` (129 lines, 9 sections). MI-first credential default (Azure Automation HRW) explicitly stated. Arc data services out-of-scope in §2. S6/S8 scenario codes in §8. Downstream Hybrid AGENTS.md section noted in §9. Five anti-patterns. Phase 2 (Saul fan-out) unblocked after ADR committed.

*(Earlier entries summarized 2026-05-19 by Scribe-8.)*


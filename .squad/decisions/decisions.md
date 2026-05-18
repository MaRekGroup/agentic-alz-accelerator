# Decisions Registry

**Last Updated:** 2026-05-18T16:27:36.887+00:00  
**Maintained By:** Scribe

This registry archives all team decisions, extending the WAF/CAF benchmark and scenario plan with new synthesis artifacts.

---

## Decision: Current vs Target Skills Table

**Author:** Linus (Architect)  
**Requested by:** Yeselam Tesfaye  
**Date:** 2026-05-18T16:27:36.887+00:00  
**Status:** Proposed  
**Extends:** Principal benchmark (WAF/CAF evaluation framework) + Scenario-anchored gap plan  

### Summary

Skills portfolio synthesis spanning 80 → 93 (+13 across 5 investment waves). Maps each priority area to CAF design areas, WAF pillars, and blocked scenarios, enabling scenario-grade prioritization.

### Master Table

| # | Priority Area | CAF Design Area | WAF Pillar(s) | Current Count | Current Skills | Target Count | Target Skills (gap items) | Delta | Scenarios Blocked | Wave |
|---|---|---|---|---:|---|---:|---|---:|---|---|
| 1 | **P1: Identity & Access** | Identity & Access | Security, Operational Excellence | 2 | `azure-rbac`, `entra-app-registration` | 5 | +`entra-id-identity-governance`, `entra-connect-hybrid-identity`, `workload-identity-federation` | +3 | 6/8: S1, S2, S3, S4, S5, S6 | Wave 1 |
| 2 | **P2: Compute & Containers** | Platform Automation & DevOps, Management | Reliability, Performance Efficiency | 0 | *(none)* | 3 | `azure-kubernetes-service`, `azure-virtual-machines`, `azure-container-apps` | +3 | 5/8: S2, S3, S5, S7, S8 | Wave 2 |
| 3 | **P3: Billing & Tenant** | Billing & Tenant | Cost Optimization, Operational Excellence | 4 | `azure-cost-management`, `azure-cost-optimization`, `cost-governance`, `azure-quotas` | 6 | +`subscription-vending`, `azure-tenant-management` | +2 | 4/8: S1, S4, S5, S6 | Wave 3 |
| 4 | **P4: Data Platform** | Security, Management | Reliability, Performance Efficiency, Cost Optimization | 0 | *(none)* | 3 | `azure-sql-database`, `azure-cosmos-db`, `azure-storage-accounts` | +3 | 4/8: S2, S3, S5, S8 | Wave 4 |
| 5 | **P5: Hybrid** | Network Topology & Connectivity | Reliability, Operational Excellence | 3 | `azure-expressroute`, `azure-vpn-gateway`, `azure-virtual-wan` | 5 | +`azure-arc-servers`, `azure-arc-kubernetes` | +2 | 2/8: S4, S7 | Wave 5 |
| 6 | **Networking (Saturated)** | Network Topology & Connectivity | Performance Efficiency, Reliability, Security | 19 | 19 skills, no new investment | 19 | *(no new investment)* | 0 | None | — |
| 7 | **Governance (Surplus)** | Governance, Resource Organization | Operational Excellence, Security, Cost Optimization | 22 | 22 skills, exceeds Principal threshold | 22 | *(no new investment)* | 0 | None | — |
| 8 | **Landing Zones (Stable)** | All (cross-cutting) | All (cross-cutting) | 15 | Complete CAF/WAF/IaC coverage | 15 | *(no new investment)* | 0 | None | — |
| 9 | **AI Infrastructure (Stable)** | Platform Automation & DevOps | Operational Excellence | 19 | 19 skills + 6 squad skills | 19 | *(no new investment)* | 0 | None | — |

**Totals:** Current = 80 → Target = 93 | Net new = **+13 skills** across 5 waves

### Headline Metrics

| Metric | Value |
|--------|-------|
| Current portfolio | 80 skills |
| Target portfolio | 93 skills |
| Net new required | 13 skills across 5 waves (16% expansion) |
| Surplus allocation | 24% of current (19/80) in Network Topology alone |
| Identity allocation (current) | 2.5% (2/80) — gap vs foundational role |
| Identity allocation (target) | 5.4% (5/93) — structurally viable |
| Scenarios fully blocked today | 6/8 by P1 identity gap |

**The bottom line:** 13 new skills close gaps blocking 6 of 8 enterprise scenarios. The 10:1 networking-to-identity ratio is the structural imbalance. Closing it converts the tool from "networking-deep" to "full-spectrum ALZ delivery engine."

### Investment Sequencing

| Wave | Target Skills | Expected PR Pattern |
|------|---|---|
| **Wave 1** | `entra-id-identity-governance`, `entra-connect-hybrid-identity`, `workload-identity-federation` | `feat(skills): add [skill-name] SKILL.md` |
| **Wave 2** | `azure-kubernetes-service`, `azure-virtual-machines`, `azure-container-apps` | `feat(skills): add [skill-name] SKILL.md` |
| **Wave 3** | `subscription-vending`, `azure-tenant-management` | `feat(skills): add [skill-name] SKILL.md` |
| **Wave 4** | `azure-sql-database`, `azure-cosmos-db`, `azure-storage-accounts` | `feat(skills): add [skill-name] SKILL.md` |
| **Wave 5** | `azure-arc-servers`, `azure-arc-kubernetes` | `feat(skills): add [skill-name] SKILL.md` |

### Methodology

This synthesis bridges two standing directives:
1. **WAF/CAF as primary evaluation lens** — every row maps to CAF design area + WAF pillars
2. **Scenario-anchored prioritization** — every gap cites blocked scenarios from 8 canonical enterprise scenarios

The structure (master table + deep dives + heatmap + headlines) provides decision-grade completeness for executives, architects, implementers, and portfolio managers.

---

## Prior Decisions (Reference)

### Decision: Principal Azure Infrastructure Architect Benchmark Framework

**Author:** Linus  
**Date:** 2026-05-18  
**Status:** Adopted as evaluation standard

Reference framework for measuring project skill maturity against Microsoft L65/L66 Principal Consultant benchmarks.

**Key benchmarks:**
- Azure Infrastructure: 18–22 (must span compute, network, storage, identity, database)
- Governance: 15–20 (policy authoring, RBAC, cost governance, compliance)
- Landing Zones: 12–16 (CAF/WAF, dual IaC, brownfield assessment)
- Hybrid: 8–12 (Arc, hybrid identity, multi-cloud)
- AI Infrastructure: 10–14 (orchestration, workflow contracts, safety)

**Application:** Baseline for measuring gaps; combined with WAF/CAF for structural analysis.

### Decision: Skills Categorization Principle (One-Skill-One-Category)

**Author:** Linus  
**Date:** 2026-05-18  
**Status:** Adopted

One skill belongs to ONE category matching its primary purpose — what it exists to do, not which agents invoke it. Corrects prior AI Infrastructure over-count (+6 skills that were actually Azure platform services).

### Decision: Scenario-Anchored Prioritization Methodology

**Author:** Linus  
**Date:** 2026-05-18  
**Status:** Adopted

Defined 8 canonical enterprise scenarios:
1. Global Landing Zone
2. Multi-Region AI Platform
3. Regulated Workloads
4. Brownfield M&A Integration
5. ISV Multi-Tenant SaaS
6. Sovereign Cloud
7. Hybrid Edge Platform
8. Cloud-Native Modernization

Evaluate each Priority as Critical/Important/Optional per scenario. When WAF/CAF and scenario lenses agree, confidence is high.

### Decision: Three Differentiated Value Propositions

**Author:** Linus  
**Date:** 2026-05-08 to 2026-05-14  
**Status:** Confirmed and merged to decisions.md

1. **Enforcement (PRIMARY):** Three-tier compliance (code → deploy → monitor+remediate)
2. **Knowledge Transfer (SECONDARY):** Algorithmic documentation with CAF traceability
3. **Timeline (TERTIARY):** Parallelized orchestration with complexity-scaled gates

**Messaging strategy:** Lead with enforcement (broadest TAM), secondary knowledge (differentiation), tertiary speed (bonus).

---

## Metadata

- **Registry Created:** 2026-05-18T16:27:36.887+00:00
- **Last Merge:** Linus spawn (linus-current-vs-target-skills-table.md)
- **Next Review:** Post-Wave 1 execution validation

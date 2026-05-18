### 2026-05-18T16:12:16Z — WAF/CAF Evaluation Lens Directive

User directive established WAF 5 Pillars + CAF 8 Design Areas as the primary structuring framework for all architect-level evaluations. Replaces ad-hoc categorization with Microsoft's canonical frameworks (links: https://learn.microsoft.com/azure/well-architected/, https://learn.microsoft.com/azure/cloud-adoption-framework/). All future architecture assessments must structure recommendations around:
- **WAF pillars:** Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency
- **CAF design areas:** Billing & Tenant, Identity & Access, Resource Organization, Network Topology & Connectivity, Security, Management, Governance, Platform Automation & DevOps

Linus re-ran Principal Benchmark under WAF/CAF lens (see `.squad/decisions.md` for full gap matrix). Critical identity & access gap identified — only 2 skills for Principal-level work requiring hybrid identity, conditional access, PIM, workload identity federation design.

**Standing Rule:** Bias all assessments toward WAF/CAF structure unless explicitly overridden.


### 2026-05-18T16:20:21Z — Scenario-Grounding Directive

User directive established scenario-anchored prioritization as standing requirement for all architect recommendations. Linus extended the WAF/CAF principal benchmark with enterprise scenario evidence: 8 canonical scenarios (Global LZ, Multi-Region AI, Regulated Workloads, M&A, ISV SaaS, Sovereign Cloud, Hybrid Edge, Cloud-Native Modernization) evaluated against priority rankings. Result: scenario analysis **fully confirms** WAF/CAF priority order.

**Standing Rule:** All future architecture assessments, gap closure plans, and recommendations must ground in concrete named enterprise scenarios. Answer: "Which scenario does this unblock? What cannot the architect deliver without it?"

Reference: `.squad/decisions.md` §"Decision: Scenario-Anchored Gap Closure Plan" for full scenario × priority matrix.

**Relationship:** Complements (not replaces) WAF/CAF lens directive from 2026-05-18T16:12:16Z. Both are standing rules.

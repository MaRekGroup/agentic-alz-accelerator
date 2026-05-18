### 2026-05-18T16:12:16Z — WAF/CAF Evaluation Lens Directive

User directive established WAF 5 Pillars + CAF 8 Design Areas as the primary structuring framework for all architect-level evaluations. Replaces ad-hoc categorization with Microsoft's canonical frameworks (links: https://learn.microsoft.com/azure/well-architected/, https://learn.microsoft.com/azure/cloud-adoption-framework/). All future architecture assessments must structure recommendations around:
- **WAF pillars:** Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency
- **CAF design areas:** Billing & Tenant, Identity & Access, Resource Organization, Network Topology & Connectivity, Security, Management, Governance, Platform Automation & DevOps

Linus re-ran Principal Benchmark under WAF/CAF lens (see `.squad/decisions.md` for full gap matrix). Critical identity & access gap identified — only 2 skills for Principal-level work requiring hybrid identity, conditional access, PIM, workload identity federation design.

**Standing Rule:** Bias all assessments toward WAF/CAF structure unless explicitly overridden.


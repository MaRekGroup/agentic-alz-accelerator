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

---

### 2026-05-18T16:57:57Z — Reviewer Gate Verdict: Skills Table Expansion (Isabel)

Isabel (Challenger) reviewed Linus's skill expansion plan at Pre-execution Gate. Verdict: **APPROVE WITH CONDITIONS**. No lockout.

**Pattern Observed:** Isabel's challenge to Linus reveals working hypothesis validation method for architect-role agents:
1. Challenger doesn't propose solutions — only tests whether proposed plan survives adversarial dissection
2. When WAF/CAF lens + scenario evidence + skill count analysis all align (as they do here), confidence in priority ordering is high
3. Conditional approval with scoping refinements (3 skills → 4) is the expected gate outcome for complex portfolio decisions

**Key Takeaway for Oracle:** When a peer architect (Linus) produces a recommendation under WAF/CAF + scenario lens, Oracle's role shifts from "second-guessing the framework" to "assuming the framework is sound and validating downstream implications." Isabel's gate is where framework validity gets challenged. If Isabel approves, downstream execution (Strategist, Forge, Envoy) can assume the framework is robust.

**For Wave 2-5 Planning:** Oracle should expect Linus to iterate the scenario × priority matrix as new customer engagements arrive. Scenarios are not static. S9 (Government Defense) or S10 (Energy/Utilities Compliance) may emerge, shifting priorities or revealing new gaps. Standing principle: re-evaluate annually or when deal flow shifts >20%.

Reference: `.squad/decisions.md` §"Reviewer Gate Decision — Skills Table" for Isabel's full analysis, including hidden assumptions and hidden assumptions audit.

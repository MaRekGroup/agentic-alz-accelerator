# ADR: Billing & Tenant Hierarchy (Management Group Architecture vs Subscription Vending)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-18 |
| **Decision Makers** | Linus (Architect, on behalf of Squad) |
| **Related Skills** | `management-group-architecture`, `subscription-vending` (Wave 3), `cost-governance`, `azure-policy`, `azure-rbac` (existing) |

## Context

Enterprise landing zones require two fundamentally coupled but operationally distinct decisions: how to organize the management group hierarchy (structural design) and how to automate subscription creation into that hierarchy (lifecycle automation). The first is an architecture decision — WHERE subscriptions belong. The second is an engineering decision — HOW subscriptions arrive there with guardrails pre-injected. These two concerns share the subscription-to-MG placement surface: the MG skill defines placement rules, the vending skill enforces them at creation time. Without a shared boundary, each skill independently defines placement criteria — producing the same coordination risk that AKS-vs-ACA had in Wave 2.

Approximately 70% of brownfield engagements assessed by this accelerator involve mis-placed subscriptions: subscriptions parked at the tenant root MG without policy inheritance, vanity hierarchies exceeding four levels that create inheritance opacity, or EA enrollment fragmentation that splits a single tenant's organizational identity across disconnected billing scopes. These mis-placements trace to absent hierarchy design criteria at the architecture phase — the moment when organizational structure should have been made explicit and subscription lifecycle automation should have been planned alongside it. Selecting the wrong hierarchy pattern creates governance debt that compounds across the estate — over-engineering with deep regional sub-hierarchies where flat suffices wastes operational budget on inheritance debugging, while under-engineering with root-parked subscriptions eliminates the policy inheritance model entirely.

This ADR establishes the canonical decision boundary between hierarchy design (`management-group-architecture`) and hierarchy automation (`subscription-vending`). The two Wave 3 SKILL.md files reference this document for hierarchy pattern selection and vending threshold decisions — they do NOT redefine these boundaries inline. The `management-group-architecture` skill goes deep on structural patterns, policy inheritance, and MG move operations; the `subscription-vending` skill goes deep on automated provisioning, guardrail injection, and decommissioning. This ADR stays in the "design vs. automate" boundary layer — the decision surface where structural choices constrain automation behavior and automation capabilities inform structural feasibility.

## Decision Tree

### Choose Flat Hierarchy When

| Criterion | Rationale |
|-----------|-----------|
| Single business unit with unified governance | No organizational boundary requires differentiated policy or RBAC inheritance |
| Fewer than 20 subscriptions total | Management overhead of deeper hierarchy outweighs governance benefit at small scale |
| No data sovereignty or regional compliance requirements | No need for geo-isolated MG branches with distinct policy sets |
| Single billing account (EA or MCA) | No billing-scope fragmentation to model in the hierarchy |
| Uniform compliance regime across all workloads | No need to separate Corp (regulated) from Online (public-facing) archetypes |

### Choose Regional Sub-Hierarchy When

| Criterion | Rationale |
|-----------|-----------|
| Data residency laws mandate geo-scoped policy (GDPR, PDPA, LGPD) | Regional MG branches enforce residency policies without subscription-level exceptions |
| Sovereign cloud or air-gapped deployment requirements | Isolated MG branch maps 1:1 to sovereign boundary with dedicated identity and policy |
| Multi-geo M&A consolidation requiring regional autonomy during transition | Acquired entities retain regional MG autonomy while inheriting parent compliance over time |
| Regional cost-center reporting requirements | MG-per-region aligns cost aggregation with finance structure without custom tagging gymnastics |

### Choose Workload-Type Hierarchy When

| Criterion | Rationale |
|-----------|-----------|
| Large enterprise with distinct Corp, Online, and SAP workload archetypes | Different compliance, networking, and identity requirements per workload class justify separate MG branches |
| Mixed compliance regimes per workload class (PCI-DSS for payments, HIPAA for health) | MG-level policy assignment eliminates per-subscription policy exception sprawl |
| ALZ reference implementation alignment required (Platform/Landing Zones/Sandbox/Decommissioned) | Canonical ALZ hierarchy is workload-type based — alignment reduces drift from reference architecture |
| More than 50 subscriptions with heterogeneous governance needs | Flat hierarchy cannot express differentiated policy at scale without per-subscription overrides |

### When to Vend (use `subscription-vending`) vs Manually Create

| Criterion | Automate (Vend) | Manual |
|-----------|-----------------|--------|
| Subscription creation rate | >10 subscriptions/year | ≤10 subscriptions/year with infrequent changes |
| Multi-tenant SaaS model | Per-tenant subscription isolation requires programmatic provisioning | Single-tenant or shared subscription model |
| Dev/test self-service requirement | Developer teams request sandboxes on-demand with guardrails | All environments provisioned by central platform team |
| Guardrail consistency | Vending pipeline injects policy, RBAC, networking, and budget at creation — eliminates configuration drift | Manual checklist processes are acceptable for the organization |
| Decommissioning lifecycle | Automated 90-day grace → cancellation pipeline needed | Ad-hoc cancellation is sufficient |

## Trade-Off Matrix (WAF Pillars)

The hierarchy pattern chosen determines how WAF pillars trade off against each other. Deeper/broader hierarchies improve security isolation and reliability blast-radius scoping at the cost of operational complexity. The `subscription-vending` skill's guardrail injection compensates for some operational overhead by automating what would otherwise be manual governance work.

| WAF Pillar | Flat Hierarchy | Regional Sub-Hierarchy | Workload-Type Hierarchy | Notes |
|------------|---------------|----------------------|------------------------|-------|
| **Security** | Uniform policy inheritance — simple but cannot differentiate regulated from public workloads | Geo-scoped isolation prevents cross-border data flow; increases inheritance depth (2-3 levels) | Maximum segmentation — Corp, Online, SAP each inherit tier-appropriate security controls | Deeper hierarchy = stronger inheritance control but higher cognitive overhead |
| **Reliability** | Single blast radius — one bad policy change affects entire estate | Regional isolation limits blast radius to geo-boundary; cross-region dependency requires explicit peering | Workload-class isolation — production blast radius scoped to archetype (Corp outage doesn't hit Online) | Blast radius inversely correlates with hierarchy breadth |
| **Operational Excellence** | Minimal management overhead — one set of policies to maintain | Moderate overhead — regional policy variants require synchronization and drift detection | Highest overhead — multiple archetype-specific policy stacks, exemption workflows, and RBAC grants | Operational cost scales with hierarchy breadth and depth |
| **Cost Optimization** | Single billing view — straightforward cost aggregation | Regional cost alignment — natural mapping to geo-based cost centers and billing scopes | Workload-class cost allocation — Corp vs Online have different unit economics; hierarchy reflects this | Billing alignment reduces chargeback complexity |
| **Performance Efficiency** | N/A — hierarchy does not directly impact workload performance | N/A — MG structure is a governance construct, not a data-plane construct | N/A — no direct performance implication | Hierarchy is a control-plane decision; performance is workload-scoped |

## Brownfield Assessment Lens

When the Assessor agent (Step 0) evaluates an existing estate's management group structure, it must determine whether the hierarchy is salvageable (re-parent in place) or requires a parallel build and cutover. This decision gates all downstream MG and vending work.

**Salvageable hierarchy (migrate in-place) prerequisites:**

The existing hierarchy qualifies for in-place restructuring when the RBAC/policy delta between current and target state is less than 5% of total assignments, no Blueprint-locked scopes exist that prevent MG moves, hierarchy depth is 4 or fewer levels, and no production workloads would experience policy evaluation gaps during the 30-minute propagation window. The `management-group-architecture` skill's playbook step 3 ⛔ HARD GATE enforces blast-radius analysis before any move operation — this ADR's criteria feed directly into that gate's pass/fail determination.

**Parallel build and cutover triggers:**

Rebuild is required when policy delta exceeds 50% of total assignments (re-parenting would cascade breaking changes), hierarchy depth exceeds 4 with vanity layers that serve no governance purpose, multi-tenancy has collapsed under a single root MG with subscription-level policy overrides substituting for proper inheritance, or Blueprint-locked scopes block the Azure Resource Manager move API. The parallel approach creates the target hierarchy alongside the existing one, migrates workloads subscription-by-subscription with validated policy evaluation, and decommissions the old hierarchy after a 90-day grace period confirms no regressions.

**90-day decommission pattern:** After cutover, source MG branches enter a monitoring-only state: all subscriptions removed, policies retained for audit reference, RBAC grants frozen. After 90 days with zero policy evaluation requests and no orphaned resource references, the empty MG branch is deleted. Subscription cancellation (not deletion) follows the same 90-day soft-delete window — vending automation must account for this Azure-platform constraint when reusing subscription names or reclaiming quota.

**Design vs. automate boundary in brownfield:** The Assessor's hierarchy evaluation determines WHAT the target structure should be (design — feeds `management-group-architecture`). The subscription re-parenting and new-subscription provisioning into that target structure is HOW it gets implemented (automate — feeds `subscription-vending`). Both skills consume this ADR's brownfield criteria but apply them to different operational phases.

**Brownfield hierarchy assessment flow:**

```
Existing Hierarchy (assess) ──► Salvageable (<5% delta)  ──► Re-parent in place
         │                                                         │
         │                                                         ▼
         │                                                    Validate via
         │                                                    MG skill ⛔ HARD GATE
         │
         └──► Not Salvageable (>50% delta) ──► Parallel build + cutover
                                                       │
                                                       ▼
                                                 90-day grace
                                                 then decommission
```

Each arrow represents an assessment outcome, not an inevitable migration. Existing hierarchies that pass the <5% delta threshold are restructured incrementally; those exceeding it require the parallel approach.

## Scenario Mapping

Each enterprise scenario maps to a specific hierarchy pattern and vending automation level. The "design vs. automate" split is visible per-row: hierarchy pattern is the design decision, vending behavior is the automation decision.

| Scenario | Code | Hierarchy Pattern | Vending Behavior | Key Constraint |
|----------|------|-------------------|------------------|----------------|
| Global Landing Zone (multi-geo) | S1 | Regional sub-hierarchy: Root → Platform + LZ-{Region} branches | Manual — small subscription count per region, central platform team | Data residency policies bound to MG branch; cross-region peering explicit |
| Brownfield M&A Integration | S4 | Workload-type with transitional regional branch for acquired entity | Semi-automated — bulk re-parent via scripted move with blast-radius gates | 30-min policy propagation per move; parallel hierarchy during transition |
| ISV Multi-Tenant SaaS | S5 | Workload-type: dedicated LZ/Tenants MG branch with per-tenant subscriptions | Fully automated vending — API-driven subscription creation with guardrail injection | >100 subscriptions/year; vending pipeline is critical path for tenant onboarding; scale-to-zero cost isolation per tenant |
| Sovereign/Regulated | S6 | Regional sub-hierarchy with isolated MG branch per sovereignty boundary | Manual with approval workflow — sovereign subscriptions require elevated creation controls | Dedicated billing scope per sovereign boundary; no cross-boundary policy inheritance |

Most enterprises will use a combination of hierarchy patterns and vending automation levels simultaneously. A single tenant may have a workload-type hierarchy for its core estate, a regional sub-hierarchy for sovereignty requirements, and fully automated vending for its SaaS tenant subscriptions. The hierarchy pattern is chosen per organizational boundary; vending automation level is chosen per subscription lifecycle velocity.

## Anti-Patterns

The following patterns recur in brownfield assessments and consistently produce governance debt. Each represents a "design vs. automate" failure: either a structural decision made without considering automation implications, or automation deployed without structural guardrails.

**All subscriptions at root MG.** Placing subscriptions directly under the tenant root management group eliminates all policy and RBAC inheritance benefits. Every governance control must be applied per-subscription, creating an assignment storm that scales linearly with subscription count. Security inheritance gaps emerge when new subscriptions are created without explicit policy assignment — they inherit nothing from root by default. This is the most common brownfield finding and the primary driver of "subscription sprawl feels ungovernable" complaints.

**Hierarchy deeper than 4 levels for organizational vanity.** Azure enforces a hard 6-level MG nesting limit (including tenant root). Organizations that mirror their full reporting structure into MG depth (CEO → Division → Department → Team → Environment → Workload) consume 5-6 levels before reaching subscriptions, leaving no room for future structural changes. Beyond the hard limit, each additional level adds 30 minutes of policy propagation delay per move operation and increases inheritance debugging complexity geometrically. The CAF reference architecture uses exactly 3 levels below root for this reason.

**Per-team MGs creating hierarchy sprawl.** Creating a dedicated management group for every development team (MG/Engineering/Team-Alpha, MG/Engineering/Team-Beta, etc.) generates RBAC sprawl where each team MG requires explicit role assignments for platform administrators, cross-team auditors, and shared-service accounts. Cost allocation becomes impossible without custom tagging because MG-level cost aggregation no longer maps to business units. When teams reorganize (which they do quarterly in large enterprises), the hierarchy requires restructuring — a governance event with blast-radius implications.

**Manual subscription creation as default.** Relying on portal-based or ad-hoc subscription creation skips guardrail injection entirely. New subscriptions arrive without policy assignments, without budget alerts, without network peering, and without RBAC grants — creating a shadow IT vector where workloads deploy into ungoverned space. The subscription-vending skill exists precisely to eliminate this gap: every subscription enters the estate pre-configured with the governance controls its target MG mandates. Organizations creating more than 10 subscriptions per year without automation are accumulating governance debt faster than manual remediation can address.

**EA enrollment fragmentation across billing accounts.** Maintaining multiple Enterprise Agreement enrollments for billing convenience (one per division, one per acquisition) fragments the tenant's organizational identity. Each EA enrollment creates an independent billing scope that cannot share reservations, savings plans, or negotiated pricing across the enterprise. When subscription vending spans multiple billing scopes, the automation must handle cross-scope API authentication and billing account selection — adding complexity that a unified billing account eliminates. This pattern frequently emerges in M&A scenarios (S4) where acquired companies retain their original EA instead of consolidating, creating a permanent impediment to unified governance visibility.

## Prerequisites and Caveats

| Factor | Impact | Guidance |
|--------|--------|----------|
| EA vs MCA billing scope | Subscription creation APIs differ: EA uses enrollment account scope, MCA uses billing profile/invoice section scope. MCA is the Microsoft strategic direction. Organizations on EA should plan migration to MCA as a billing prerequisite before enabling API-driven subscription vending at scale — this is a billing-account migration (not addressed in this ADR), not a hierarchy decision. | Confirm billing agreement type during Step 1 requirements; note EA→MCA migration as prerequisite if vending automation is required |
| Global Admin elevation at tenant root | Accessing tenant root MG requires explicit elevation (`Access management for Azure resources` toggle in Entra ID). This is a one-time action but requires Global Administrator and creates an audit event. | Document elevation in runbook; schedule during maintenance window; remove elevation after initial hierarchy deployment |
| 6-level MG nesting limit | Azure Resource Manager enforces a maximum of 6 management group levels including tenant root. This is a hard platform constraint — no exception process exists. | Design hierarchies with maximum 3-4 levels below root to leave room for future structural evolution |
| MG move policy-propagation delay (30 min) | When a subscription moves between MGs, policy evaluation uses the NEW MG's policies after propagation completes (~30 minutes). During this window, workloads may experience policy evaluation against stale assignments. | Schedule moves during maintenance windows; validate policy evaluation post-move before confirming success |
| Subscription creation API eventual consistency (5-15 min) | After subscription creation API returns success, the subscription may not be visible in Resource Graph or MG membership for 5-15 minutes. Vending pipelines must include polling/retry logic. | Build wait-and-verify steps into vending automation; do not chain dependent operations without confirmation |
| Subscription cancellation is NOT deletion (90-day window) | Cancelled subscriptions remain in a disabled state for 90 days before permanent deletion. Resources are inaccessible but not destroyed. Reactivation is possible within this window. | Vending decommission workflows must account for 90-day soft-delete; naming conventions should prevent collision with pending-deletion subscriptions |
| Blueprint deprecation impact | Azure Blueprints is deprecated (retirement 2026-07-11). Existing Blueprint-locked MG scopes block ARM move operations. Migration to Policy + DINE (DeployIfNotExists) is required before hierarchy restructuring. | Assess Blueprint usage during brownfield discovery; plan Blueprint→Policy migration as a prerequisite for MG moves |

## References

### Wave 3 SKILL.md Files (Authored After This ADR)

- `.github/skills/management-group-architecture/SKILL.md` — MG hierarchy design, policy inheritance, move operations, blast-radius analysis
- `.github/skills/subscription-vending/SKILL.md` — Automated subscription provisioning, guardrail injection, decommissioning lifecycle

### Existing Skills (Cross-Referenced)

- [`.github/skills/azure-policy/SKILL.md`](../../.github/skills/azure-policy/SKILL.md) — Policy authoring syntax, built-in initiatives, exemption workflows (hard prereq for MG skill)
- [`.github/skills/azure-rbac/SKILL.md`](../../.github/skills/azure-rbac/SKILL.md) — Role definitions, custom roles, assignment scope patterns
- [`.github/skills/cost-governance/SKILL.md`](../../.github/skills/cost-governance/SKILL.md) — Budget alerts, cost allocation, chargeback patterns

### Microsoft Learn References

- [Organize resources with management groups](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/organize-resources) — CAF MG hierarchy guidance
- [ALZ reference implementation — management group structure](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups) — Canonical Platform/LZ/Sandbox/Decommissioned structure
- [AVM `avm/ptn/lz/sub-vending`](https://github.com/Azure/bicep-registry-modules/tree/main/avm/ptn/lz/sub-vending) — Azure Verified Module for subscription vending
- [Subscription decommissioning](https://learn.microsoft.com/azure/cost-management-billing/manage/cancel-azure-subscription) — Cancellation, soft-delete, and reactivation
- [Microsoft Customer Agreement billing scopes](https://learn.microsoft.com/azure/cost-management-billing/understand/mca-overview) — MCA billing profile and invoice section structure

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-18 | Linus | Initial ADR for Wave 3 skill authoring. Establishes canonical hierarchy-pattern-to-vending-automation decision boundary referenced by both `management-group-architecture` and `subscription-vending` SKILL.md files. |

---
name: management-group-architecture
description: "Azure Management Group hierarchy design, policy inheritance mechanics, and subscription move operations for Azure Landing Zones. USE FOR: ALZ canonical hierarchy design (Root → Platform/Landing Zones/Sandbox/Decommissioned), MG-scoped Azure Policy assignment and inheritance, MG-scoped RBAC role assignments, subscription-to-MG placement strategy, MG move blast-radius analysis, Root MG governance (tenant-level settings), multi-geo regional sub-hierarchies for data sovereignty, and M&A hierarchy integration. DO NOT USE FOR: hierarchy pattern selection criteria (use docs/decisions/billing-tenant-hierarchy.md), Azure Policy authoring syntax (use azure-policy), RBAC role definition design (use azure-rbac), subscription creation automation (use subscription-vending), or network topology within subscriptions (use azure-virtual-network)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-governance
  wave: "3"
---

# management-group-architecture

| Field | Value |
|-------|-------|
| **Skill ID** | `management-group-architecture` |
| **Domain** | Azure Governance / Resource Organization |
| **Hard Prereqs** | `azure-policy` (existing skill) |
| **Soft Prereqs** | `azure-rbac`, `caf-design-areas` |
| **Shared ADR** | [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) |
| **Primary CAF Area** | Resource Organization |
| **Brownfield Scenario** | S4 — Brownfield M&A Integration |
| **Authored** | 2026-05-18, Saul (Wave 3) |

## Overview

Hierarchy-pattern selection criteria are defined in [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md). This skill goes deep on MG hierarchy implementation, policy inheritance mechanics, and MG move operations — not on choosing flat-vs-regional-vs-workload patterns (that's the ADR's job).

Management Groups are the organizational backbone of every Azure Landing Zone. They are the scope at which governance cascades — the point where a single policy assignment becomes enforced across every subscription an enterprise operates. A well-designed hierarchy creates predictable inheritance, manageable RBAC boundaries, and a clear operational model for how governance evolves as the estate grows.

The structural decisions made here have compounding downstream effects. A hierarchy that is too flat forces policy exceptions at subscription level, creating per-subscription policy sprawl that scales linearly with estate size. A hierarchy that is too deep creates inheritance opacity: teams cannot predict which policies apply to their subscriptions without tracing through 4–5 MG levels. Ad-hoc subscription moves performed without blast-radius analysis silently revoke or grant RBAC and policy controls, breaking production workloads in ways that manifest hours later.

This skill addresses the implementation surface of MG architecture: the ALZ canonical structure (Root → Platform → Landing Zones → Sandbox → Decommissioned), MG-scoped policy assignment and initiative inheritance design, MG-scoped RBAC and PIM eligible assignment patterns, subscription-to-MG placement decisions, and the move operation workflow with its required blast-radius analysis gate. It applies to both greenfield deployments establishing an estate from scratch and brownfield M&A scenarios integrating acquired subscriptions into an existing hierarchy.

Use this skill when the agents need to know WHERE subscriptions belong, HOW governance cascades through the hierarchy, WHAT the blast radius of a move operation is, and WHO has administrative boundaries at which MG scope. This skill does not cover Azure Policy authoring syntax, built-in initiative details, or RBAC role definition design — those surfaces belong to `azure-policy` and `azure-rbac`. It does not cover subscription creation automation — that belongs to `subscription-vending`. For the canonical decision tree governing which hierarchy pattern fits which enterprise scenario, read the shared ADR first.

## When to Use This Skill

- Designing a new management group hierarchy for a greenfield Azure Landing Zone deployment
- Auditing an existing estate's MG structure against the ALZ canonical reference (Platform/Landing Zones/Sandbox/Decommissioned)
- Determining which subscriptions belong in which MG branch and why (Corp, Online, SAP, custom archetypes)
- Planning MG-scoped policy assignments and understanding how policy inherits down the hierarchy
- Configuring MG-scoped RBAC for platform engineers, subscription owners, and auditors
- Evaluating blast radius before moving a subscription between MGs
- Designing a regional sub-hierarchy for data sovereignty or multi-geo compliance requirements
- Integrating an acquired company's subscriptions into an enterprise hierarchy (Scenario S4)
- Remediating an estate where subscriptions are parked at the tenant root MG without inheritance
- Configuring Root MG tenant-level settings (require MG for new subscriptions, default management group)
- Granting pipeline service principals the MG-scoped permissions required for subscription factory automation
- Assessing whether an existing hierarchy's depth or breadth is approaching the 6-level Azure platform limit
- Designing a PIM eligible assignment structure for Platform engineers who need just-in-time Owner access at MG scope

## CAF Design Area Mapping

| Design Area | Coverage Level | What This Skill Provides |
|-------------|---------------|--------------------------|
| **Resource Organization** | **Primary** | MG hierarchy IS resource organization — the structural decision that determines how subscriptions group, how policy inherits, and how RBAC cascades across the estate. Cannot design resource organization without MG architecture. ALZ canonical structure (Platform/Landing Zones/Sandbox/Decommissioned) is the reference implementation of this design area. |
| **Governance** | **Primary** | MG-scoped policy assignments are the enforcement plane for all governance rules. Policy inheritance design — which initiative goes at which level, what exemptions are permitted, how deviation handling works — is governance architecture. Exemption workflows at MG scope are how organizations operationalize deviation without breaking inheritance. |
| **Security** | **Primary** | Root-MG security policies (deny public access, require encryption, disable public network) are the estate security foundation. MG-scoped RBAC determines who can access which organizational segment. Defender for Cloud auto-provisioning targets MG scope. Misconfigured MG permissions are the primary privilege escalation vector in multi-subscription estates. |
| **Identity & Access** | **Primary** | MG-scoped RBAC defines administrative boundaries across the estate. PIM eligible assignments targeting MG scope govern Platform engineer access. Service principal access at MG level controls automation tool boundaries — subscription factory pipelines, compliance scanners, and cost tooling all require MG-scoped identity grants. |
| **Platform Automation & DevOps** | Secondary | MG hierarchy enables IaC deployment scoping — Bicep and Terraform targets a specific MG when provisioning subscription factory resources. Pipeline service principals require MG-level permissions for subscription moves and policy assignments. The hierarchy's structural stability is a prerequisite for automated governance at scale. |

## WAF Pillar Coverage

| Pillar | Coverage | Specific Capabilities |
|--------|----------|-----------------------|
| **Security** | **Primary** | Root-MG deny-by-default policies enforce the security baseline across the entire estate in a single assignment. MG-scoped RBAC prevents lateral privilege escalation between organizational units. Defender for Cloud auto-provisioning at MG scope ensures continuous threat protection without per-subscription manual enablement. Misconfigured MG permissions are the #1 privilege escalation vector in multi-subscription environments. |
| **Operational Excellence** | **Primary** | MG hierarchy determines operational boundary clarity: which team owns which governance scope, how policy changes propagate, how subscription moves are governed, and where exemption authority lives. Poorly designed hierarchies create operational confusion — teams cannot tell who approves what, where exceptions go, or why a specific policy applies to their subscription. Move operation audit logs at MG scope provide the evidence trail for change management. |
| **Reliability** | Secondary | MG move operations can silently break workloads if policy evaluation changes revoke network peering permissions, block storage access, or deny compute configurations. Blast-radius analysis and staged moves are reliability practices that prevent undetected production outages. Correct subscription-to-MG placement prevents deny-assignments from blocking existing resources. |
| **Cost Optimization** | Secondary | MG hierarchy enables cost allocation boundaries: Platform costs vs. Landing Zone costs vs. Sandbox costs can be aggregated at MG scope in Azure Cost Management. Policy at MG scope enforces budget tagging requirements across entire branches. Cost views in Azure Cost Management map directly to the MG hierarchy, making chargeback and showback operationally tractable. |

## Boundaries — DO NOT USE FOR

- **Hierarchy pattern selection** (flat vs. regional vs. workload-type) — see [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md)
- **Subscription creation automation** — see `subscription-vending` SKILL.md (Wave 3 sibling)
- **Azure Policy authoring syntax** (initiative definitions, built-in policy IDs, exemption workflow mechanics) — see `azure-policy`
- **RBAC role definitions and custom role design** — see `azure-rbac`
- **Network topology design within subscriptions** (hub-spoke, NSGs, UDRs) — see `azure-virtual-network`
- **Cost allocation tag enforcement and budget alert configuration** — see `cost-governance`, `azure-cost-management`
- **Entra ID tenant creation or multi-tenant federation** — future `azure-tenant-design`
- **EA-to-MCA billing account migration** — see shared ADR Prerequisites and Caveats section

## Architecture Patterns

### 1. ALZ Reference Hierarchy (Platform/LZ/Sandbox/Decom)

The canonical ALZ structure places exactly 3 levels below tenant root: `Root → {Platform, Landing Zones, Sandbox, Decommissioned}`, with Platform further subdivided into `{Identity, Management, Connectivity}` and Landing Zones into `{Corp, Online}` archetypes. This structure is the baseline for all greenfield deployments. Platform MGs govern shared infrastructure subscriptions; Landing Zone MGs govern application workload subscriptions grouped by connectivity archetype; Sandbox MGs govern experimental subscriptions with relaxed policy; Decommissioned MGs hold subscriptions in the cancellation grace period with no new resource deployments permitted.

| MG Node | Child Subscriptions | Policy Posture |
|---------|-------------------|----------------|
| Platform → Identity | Entra ID DC Services, AD DS, privileged access workstations | Deny public endpoints; require zone-redundant deployment |
| Platform → Management | Log Analytics workspace, Automation accounts, Monitor alerts | Diagnostic settings required; Defender for Cloud auto-provision enabled |
| Platform → Connectivity | Hub VNets, Azure Firewall, ExpressRoute/VPN gateways, DNS | Deny direct internet from spoke; require Firewall egress |
| Landing Zones → Corp | Application subscriptions requiring hub connectivity + regulated policy | Deny public IPs; mandatory tagging; budget alerts required |
| Landing Zones → Online | Application subscriptions with public-facing workloads | Allow public IPs; WAF required for App Gateway/Front Door paths |
| Sandbox | Developer self-service, POC, experimental workloads | Budget cap enforced; auto-expire policy; reduced deny set |
| Decommissioned | Cancelled subscriptions in 90-day soft-delete window | Deny all new deployments; RBAC grants frozen |

**When to use:** All greenfield ALZ deployments and brownfield estates being restructured toward CAF alignment. This is the default starting point — deviate only when a documented requirement cannot be satisfied within this structure.

### 2. Regional Sub-Hierarchy for Data Sovereignty

When data residency laws (GDPR, PDPA, LGPD) or sovereign cloud requirements mandate geo-scoped policy enforcement, a regional sub-hierarchy adds a geo-named MG branch under Landing Zones: `Landing Zones → LZ-EU / LZ-APAC / LZ-Americas`. Each regional MG branch inherits the parent's security baseline and adds region-specific compliance policy assignments. Cross-region subscription placement is denied by policy at the regional MG scope, not by manual process.

**When to use:** Enterprises with regulatory mandates for data residency, multi-geo M&A consolidation requiring regional autonomy, or regional cost-center reporting requirements. See ADR Scenario Mapping for S1 and S4 details.

### 3. Brownfield M&A Transitional Hierarchy

During M&A integration, a transitional MG branch `Landing Zones → LZ-Acquired-{EntityName}` holds the acquired entity's subscriptions during the integration period. The transitional branch inherits the enterprise baseline but carries a reduced policy set that accommodates legacy configurations. Policy is progressively tightened during the 30-day stabilization period (see Brownfield Playbook). After stabilization, the transitional MG branch is dissolved and subscriptions are re-parented to the appropriate Corp or Online archetype.

**When to use:** Any subscription acquisition where legacy configurations would fail the target MG's policy set at day-one. This pattern avoids a single large-bang migration that risks production outages.

### 4. Workload-Type Archetype Hierarchy

The Corp/Online distinction in the ALZ reference captures the most important compliance split: Corp subscriptions require private connectivity and regulated-workload policy (no public endpoints, mandatory audit logging), while Online subscriptions permit public-facing resources. For enterprises with additional workload archetypes (SAP, PCI-DSS payment processing, HIPAA healthcare), additional archetype MGs under Landing Zones express these boundaries as policy inheritance branches rather than per-subscription overrides.

**When to use:** Large enterprises (50+ subscriptions) with heterogeneous compliance requirements per workload class. Do not create archetype MGs for fewer than 3 subscriptions — the RBAC and exemption overhead exceeds the inheritance benefit at small scale.

### 5. Emergency Lockdown Pattern

A root-MG deny-all assignment with an explicit exemption workflow provides a break-glass security response: assign a deny-all initiative at tenant root scope, then exempt individual subscriptions via exemption resources scoped to that initiative. Exemptions are time-limited (expiration timestamp required), role-gated, and audit-logged. This pattern enables a rapid estate-wide security response without requiring per-subscription changes.

**When to use:** Security incidents requiring immediate blast-radius containment, compliance audits requiring demonstrated control capability, and as a design-time pattern to verify the exemption workflow is operational before an incident occurs.

## Scenarios Unblocked

MG hierarchy architecture is a prerequisite for scenario-specific governance — the structural decisions here determine which scenario-level controls are even expressible. Key scenarios unblocked by this skill:

- **S1 (Global Landing Zone):** Cannot enforce regional data residency policies without a regional sub-hierarchy design. This skill provides the MG branch design for geo-scoped policy assignment — which landing zone subscriptions belong under LZ-EU vs. LZ-APAC, how sovereignty policies assign at the regional MG, and how cross-region peering restrictions attach at the right scope rather than per-subscription.
- **S4 (Brownfield M&A Integration):** The primary brownfield scenario for this skill. Cannot safely integrate acquired subscriptions into an enterprise hierarchy without blast-radius analysis, transitional MG structure design, and staged move operations. This skill owns the structural integration playbook; `subscription-vending` picks up ongoing subscription provisioning automation after integration stabilizes.
- **S5 (ISV Multi-Tenant SaaS):** Cannot design a per-tenant subscription isolation model without a dedicated LZ archetype MG for tenant subscriptions. The hierarchy branch `Landing Zones → LZ-Tenants` is the structural prerequisite for the vending pipeline that creates and governs tenant subscriptions at scale.
- **S6 (Sovereign/Regulated):** Cannot establish hard governance boundaries between sovereign workloads and commercial workloads without dedicated MG branches with separate policy stacks. This skill designs the isolation boundary; the compliance and security skills apply the policy content within those boundaries.
- **S3 (Regulated Workloads):** Cannot isolate PCI-DSS payment scopes or HIPAA health data scopes without dedicated archetype MGs that prevent Corp-to-Regulated-Workload inheritance bleed. MG-level RBAC boundaries prevent platform engineers from accessing regulated-workload subscriptions without explicit PIM elevation — a control plane requirement for regulated audit evidence.

## Decision Heuristics

| Condition | Implementation Guidance |
|-----------|------------------------|
| Subscription belongs to a shared platform service (hub network, log analytics workspace, identity) | Place in Platform MG (Identity, Management, or Connectivity child) — never in Landing Zones |
| Subscription requires private connectivity to hub + regulated compliance policies | Place in Corp archetype MG |
| Subscription hosts public-facing workloads with relaxed connectivity requirements | Place in Online archetype MG |
| Subscription is experimental, temporary, or developer self-service | Place in Sandbox MG — apply budget cap policy at Sandbox scope |
| Subscription is cancelled or pending decommission | Move to Decommissioned MG before cancellation — retains policy history for audit |
| Moving a subscription between MGs | Run blast-radius analysis (Step 3 in Brownfield Playbook); wait 30 minutes post-move for policy propagation before validating compliance state |
| Policy needs to differ between two groups of Corp subscriptions | Create a child MG under Corp rather than per-subscription policy overrides — inheritance is cheaper to maintain |
| MG hierarchy depth approaching 4 levels | Stop. Width is preferred over depth. Add sibling MGs before adding child MGs — each additional level adds 30 minutes of propagation delay per move operation |
| Blueprint assignments exist at MG scope | Audit and migrate to Policy + DINE before any MG move operation — Blueprint scope is immutable post-assignment and blocks the ARM move API |
| Platform engineer needs Owner access at MG scope | Use PIM eligible assignment at MG scope, not standing Owner. JIT activation with approval workflow reduces standing privilege exposure at the highest-risk scope in the estate |
| New subscription created outside vending automation | Immediately verify target MG placement — subscriptions created via portal default to the configured default MG (or root if not configured). Misplacement creates governance gap until corrected |

## Brownfield Scenario (Scenario S4: Brownfield M&A Integration)

An acquired company arrives with a flat or absent management group hierarchy: subscriptions parked at the tenant root, no policy inheritance, RBAC grants scattered at subscription or resource-group scope, and legacy configurations that would fail the enterprise's Corp MG policy set on day one. The goal is to integrate these subscriptions into the enterprise hierarchy with zero production outages, using the transitional hierarchy pattern (Pattern 3) as the operational bridge.

Cross-skill sequencing: Run after `entra-connect-hybrid-identity` establishes identity trust between tenants; coordinate with `azure-policy` for policy unification across merged hierarchies; hand off subscription placement results to `subscription-vending` for ongoing automation. For the "salvageable vs. parallel rebuild" assessment criteria, consult [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) — the ADR's Brownfield Assessment Lens section defines the <5% delta threshold that determines whether in-place re-parenting or parallel build is the correct approach.

### 8-Step Integration Playbook

1. **Discover existing MG hierarchy** — Map the acquired entity's current MG structure (often flat or absent). Identify orphan subscriptions at root MG. Document current RBAC assignments (export via `az role assignment list --all`) and existing policy assignments at each scope. Catalog any Azure Blueprints assignments at MG scope — these block move operations and must be migrated first. *Soft rollback: discovery only; no changes made.*

2. **Design target hierarchy** — Map acquired subscriptions to the enterprise MG archetype (Corp, Online, SAP, or a transitional `LZ-Acquired-{Name}` branch). Determine if a regional sub-MG is needed for data sovereignty requirements. Produce a subscription placement mapping document. Cross-reference the ADR's Decision Tree to validate pattern selection. *Soft rollback: design artifact only; no Azure changes.*

3. **Pre-move blast-radius analysis** — For each subscription, calculate: which policies will newly apply, which RBAC will be lost, which RBAC will be gained, which deny-assignments will block existing resources. ***⛔ HARD GATE — Stop if >5% of existing resources would be non-compliant with zero remediation path. This is the proceed/abort decision point; all subsequent steps assume blast-radius is acceptable.***

4. **Create target MG structure** — Provision new MGs in the enterprise hierarchy for acquired workloads (e.g., `LZ-Acquired-Contoso`). Apply baseline policy at the new MG scope using the enterprise initiative. Do NOT move subscriptions yet — validate that the new MG's policy set evaluates as expected against a representative test subscription. *Soft rollback: delete new MGs; no production impact.*

5. **Staged subscription moves — non-production first** — Move sandbox and development subscriptions into the target MG. Validate policy evaluation (30-minute propagation wait required), RBAC access for key service principals, and workload health post-move. 48-hour bake period before proceeding. *Soft rollback: move subscription back to source MG.*

6. **Production subscription moves** — Move production subscriptions one-at-a-time with workload health checks between each move. Monitor Defender for Cloud compliance score drift during the propagation window. Coordinate moves during a maintenance window to manage the 30-minute policy propagation gap. *Soft rollback: immediate move-back within 4-hour window while policy propagation state is recoverable.*

7. **Policy unification** — Remove duplicative policy assignments inherited from the acquired entity's legacy structure. Consolidate into enterprise initiative definitions at the appropriate MG scope. Remove subscription-level policy overrides that replicate inheritance-available controls — these create management overhead with no added governance value. Use `az policy assignment list --scope /subscriptions/{id}` to export all subscription-level assignments before removal. *Soft rollback: re-apply legacy assignments from backed-up assignment export.*

8. **Decommission legacy hierarchy** — After 30-day stabilization confirms no policy or RBAC regressions, delete empty MGs from the acquired entity's original structure bottom-up (leaf MGs first, then parents). Archive RBAC assignment exports for audit trail. If the transitional MG branch was used, dissolve it now and re-parent subscriptions to the canonical Corp/Online archetypes. Verify the default management group setting at tenant root does not point to a deleted MG path. *Soft rollback: recreate MGs and reassign from archive before the 90-day soft-delete window closes.*

## Hidden Assumptions

1. **Tenant root access requires Global Admin elevation.** MG operations at root scope require explicitly enabling the `Access management for Azure resources` toggle in Entra ID — this requires Global Administrator and is not on by default. The elevation creates an audit event and is often the first surprise for platform engineers new to MG management. Remove the elevation after initial hierarchy deployment to reduce standing privilege exposure.

2. **Azure enforces a hard 6-level MG nesting limit.** Azure Resource Manager permits a maximum of 6 management group levels including tenant root. No exception process exists. Organizations that mirror full org-chart reporting structure into MG depth (CEO → Division → BU → Department → Team → Environment) exhaust the limit before reaching subscriptions. Design hierarchies with 3–4 levels below root maximum, favoring hierarchy width over depth for organizational complexity.

3. **MG move policy propagation takes up to 30 minutes.** When a subscription moves between MGs, Azure Resource Manager updates MG membership immediately, but policy evaluation shifts to the new MG's assignments after a propagation period (~30 minutes). Compliance checks, deny-assignment evaluations, and RBAC inheritance run against the NEW MG's policies only after propagation completes. Automated pipelines that validate immediately post-move will read stale compliance state — build a 30-minute wait into all move automation.

4. **MG deletion requires all children evacuated first.** An MG containing child subscriptions or child MGs cannot be deleted — the ARM API returns a conflict error. Decommissioning an MG hierarchy requires bottom-up evacuation: move all leaf subscriptions to target MGs, delete leaf MGs, then work upward to parent MGs. Attempting top-down deletion is the most common operational mistake in hierarchy cleanup operations.

5. **Azure Blueprints deprecation blocks MG moves.** Azure Blueprints (deprecated, retirement 2026-07-11) creates scope-locked assignments that the ARM move API cannot override. A subscription with a Blueprint assignment at MG scope cannot be moved until the Blueprint is deleted or migrated to Azure Policy + DINE (DeployIfNotExists). Enterprises that adopted Blueprints in 2020–2022 frequently encounter this blocker during M&A integration. Assess Blueprint usage during Step 1 discovery and schedule Blueprint-to-Policy migration as a prerequisite for any move operation.

> **Note:** The `az blueprint list --management-group {mgId}` command enumerates Blueprint assignments at MG scope. Run this during discovery alongside the RBAC and policy export — Blueprint blockers discovered mid-playbook delay the integration by weeks when the migration plan wasn't scoped for them upfront.

## Anti-Patterns

### Anti-Pattern 1: All subscriptions parked at root MG

Placing subscriptions directly under the tenant root management group — the most common brownfield finding — eliminates all policy and RBAC inheritance benefits. Every governance control must be applied per-subscription, creating an assignment storm that scales linearly with estate size. When new subscriptions are created without an automated placement process, they inherit nothing from root by default and arrive ungoverned. Security inheritance gaps are invisible until an audit surfaces a subscription that has been running without deny-public-access policies for months.

**Corrective action:** Establish the ALZ canonical hierarchy (Platform/Landing Zones/Sandbox/Decommissioned) and define per-MG policy initiatives before moving any subscriptions. Move subscriptions from root to target MGs using the blast-radius analysis playbook above. Do not accelerate this migration — one subscription at a time with 30-minute propagation waits is the correct tempo, not a bulk move that makes rollback impossible.

### Anti-Pattern 2: Hierarchy deeper than 4 levels for organizational vanity

Organizations that model their full reporting structure in MG depth routinely hit Azure's 6-level hard limit before reaching subscriptions, leaving no headroom for future structural evolution. Beyond the platform constraint, each additional hierarchy level adds 30 minutes of policy propagation delay per move operation and increases inheritance debugging complexity. Engineers tracing why a specific policy applies to their subscription must now walk 5–6 MG levels, reading policy assignments at each level. The CAF reference architecture uses exactly 3 levels below root — this is not an oversimplification, it is deliberate depth control.

**Corrective action:** Flatten any hierarchy exceeding 4 levels below root. Organizational complexity that currently maps to MG depth should be expressed as archetype sibling MGs (width) rather than parent-child chains (depth). If a governance boundary genuinely requires a child MG — for example, a regulated subdivision within a Corp MG — that is a valid use of one additional level. Org-chart mirroring is not a valid use.

### Anti-Pattern 3: MG move attempted without blast-radius analysis

Moving a subscription between MGs without pre-calculating the policy and RBAC delta is the most operationally dangerous pattern in MG management. The move completes in seconds; the consequences manifest over 30 minutes as policy propagation kicks in. A subscription moved from a permissive Sandbox MG to a Corp MG with `deny-publicNetworkAccess` policies will find existing storage accounts, SQL instances, and App Services suddenly blocked. RBAC grants scoped to the source MG are lost immediately on move; grants at the target MG propagate with the policy delay. Production outages traced to "we just moved the subscription" take hours to diagnose because the connection between the move and the failure is not obvious.

**Corrective action:** Never skip Step 3 of the integration playbook. The ⛔ HARD GATE exists because there is no fast rollback from a production outage caused by a bad move — only a move-back (which itself has a 30-minute propagation penalty) and an incident investigation. Blast-radius analysis is cheap; a production P0 is not.

### Anti-Pattern 4: MG deletion attempted top-down without evacuating children

Platform engineers attempting to clean up a legacy hierarchy frequently try to delete the top-level MG first, expecting Azure to cascade-delete children. Azure does not cascade-delete MG children — the ARM API returns a conflict error for any MG with active children. The attempted deletion succeeds for no MG at all. Teams then try to force-delete through portal clicks or CLI loops, generating a sequence of error events that is difficult to audit and leaves the hierarchy in a partially modified state that is harder to clean than the original structure.

**Corrective action:** Hierarchy decommissioning is strictly bottom-up. Move all subscriptions in leaf MGs to their target locations. Delete leaf MGs after confirming they are empty. Work upward through parent MGs, deleting each only after its children are confirmed empty. Script this sequence explicitly — do not attempt it manually in the portal for hierarchies with more than 5 MGs. Step 8 of the integration playbook encodes this sequence with audit checkpoints.

## Diagnostic Queries

### KQL: Subscriptions not assigned to a management group (root-parked)

```kql
ResourceContainers
| where type == "microsoft.resources/subscriptions"
| extend managementGroupAncestors = properties.managementGroupAncestorsChain
| where array_length(managementGroupAncestors) == 1
| project name, subscriptionId, managementGroupAncestors
| order by name asc
```

Returns subscriptions whose only ancestor is tenant root — the primary indicator of root-parked subscriptions with no policy inheritance.

### KQL: Policy assignments at subscription scope (inheritance bypass indicator)

```kql
PolicyResources
| where type == "microsoft.authorization/policyassignments"
| where properties.scope has "/subscriptions/"
| where not (properties.scope has "/resourceGroups/")
| project assignmentName=name, scope=properties.scope, policyDefinitionId=properties.policyDefinitionId, displayName=properties.displayName
| order by scope asc
```

High counts of subscription-scoped policy assignments indicate per-subscription governance workarounds — a signal that the MG hierarchy is not expressing governance correctly at the right level.

### KQL: Management group hierarchy depth per subscription

```kql
ResourceContainers
| where type == "microsoft.resources/subscriptions"
| extend ancestorChain = properties.managementGroupAncestorsChain
| extend hierarchyDepth = array_length(ancestorChain)
| project name, subscriptionId, hierarchyDepth, ancestorChain
| order by hierarchyDepth desc
```

Subscriptions with `hierarchyDepth > 5` are at or near the 6-level MG limit. Subscriptions with `hierarchyDepth == 1` are root-parked.

## References

| Topic | Source |
|-------|--------|
| Hierarchy pattern selection decision tree | [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) (this repo, Wave 3 shared ADR) |
| Organize resources with Azure management groups | https://learn.microsoft.com/azure/governance/management-groups/overview |
| ALZ reference architecture — MG structure | https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups |
| CAF resource organization best practices | https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/organize-resources |
| Azure Policy assignment scope and inheritance | https://learn.microsoft.com/azure/governance/policy/concepts/scope |
| Management group move subscription API | https://learn.microsoft.com/azure/governance/management-groups/manage#move-subscriptions |
| Global Admin elevation for tenant root access | https://learn.microsoft.com/azure/role-based-access-control/elevate-access-global-admin |
| Azure Blueprints deprecation and migration | https://learn.microsoft.com/azure/governance/blueprints/overview |
| Defender for Cloud MG-level auto-provisioning | https://learn.microsoft.com/azure/defender-for-cloud/auto-deploy-azure-monitoring-agent |
| ALZ reference implementation GitHub | https://github.com/Azure/Enterprise-Scale |
| `azure-policy` skill (hard prereq) | `.github/skills/azure-policy/SKILL.md` (this repo) |
| `azure-rbac` skill (soft prereq) | `.github/skills/azure-rbac/SKILL.md` (this repo) |
| `caf-design-areas` skill (soft prereq) | `.github/skills/caf-design-areas/SKILL.md` (this repo) |
| `subscription-vending` skill (Wave 3 sibling) | `.github/skills/subscription-vending/SKILL.md` (this repo) |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-18 | Saul | Initial Wave 3 authoring — MG hierarchy design, policy inheritance mechanics, subscription move blast-radius analysis, S4 Brownfield M&A Integration playbook (8 steps, ⛔ HARD GATE at Step 3), 5 hidden assumptions, 4 anti-patterns |

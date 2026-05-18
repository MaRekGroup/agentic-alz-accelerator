---
name: subscription-vending
description: "Automated Azure subscription provisioning via AVM avm/ptn/lz/sub-vending, guardrail injection at creation time, and subscription decommissioning lifecycle for Azure Landing Zones. USE FOR: EA enrollment account or MCA billing scope subscription creation, vending pipeline patterns (IaC-driven, API-driven, self-service portal with guardrails), subscription-level guardrail injection (policy assignments, RBAC grants, diagnostic settings, budget alerts), network connectivity injection (hub-spoke VNet peering, private DNS zone links, route table deployment), MG placement automation into archetype branches (Corp/Online/SaaS-Tenant/Sandbox), quota and SKU pre-provisioning, and full subscription lifecycle (creation → active → decommission → cancellation → 90-day purge). DO NOT USE FOR: management group hierarchy design, pattern selection, and MG move operations (use management-group-architecture), hierarchy-pattern and vending-threshold decision criteria (see docs/decisions/billing-tenant-hierarchy.md), Azure Policy authoring and initiative design (use azure-policy), EA-to-MCA billing agreement migration (out of scope — future skill), VNet/subnet architecture and hub topology design (use azure-virtual-network), budget enforcement and cost alert policy (use cost-governance), or workload identity federation for pipeline service principals (use workload-identity-federation)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-landing-zone
  wave: "3"
---

# subscription-vending

| Field | Value |
|-------|-------|
| **Skill ID** | `subscription-vending` |
| **Domain** | Azure Landing Zone — Platform Automation & Billing |
| **Hard Prereqs** | `azure-resource-manager`, `azure-policy` |
| **Soft Prereqs** | `management-group-architecture` (Wave 3 sibling), `workload-identity-federation` (Wave 1) |
| **Shared ADR** | [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) |
| **Primary CAF Area** | Billing & Tenant |
| **Brownfield Scenario** | S5 — ISV Multi-Tenant SaaS |
| **Authored** | Wave 3 · 2026-05-18 · Saul |

## Overview

Vending threshold criteria (automate vs manual) are defined in [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md). This skill goes deep on subscription creation automation, guardrail injection, and decommissioning lifecycle — not on the hierarchy pattern decision (that's `management-group-architecture` + the ADR).

Subscription vending is the bridge between "we designed a landing zone architecture" and "teams can actually get one." Without it, every new workload request requires manual subscription creation, manual MG placement, manual network peering, and manual policy verification — a 2-week lead time that kills cloud adoption velocity at scale. With automated vending, any authorized team can trigger a pipeline that provisions a fully governed, network-connected, budget-capped subscription in under 15 minutes, with every guardrail pre-wired before the first workload deploys.

This skill covers the full Azure subscription lifecycle: programmatic creation via EA enrollment account or MCA billing profile, subscription-level guardrail injection at creation time (policy assignments, RBAC grants, diagnostic settings, budget alerts), network connectivity injection (hub-spoke VNet peering, private DNS zone delegation links, baseline NSG deployment), MG placement into the correct archetype (Corp, Online, SaaS-Tenant, Sandbox), and the decommissioning lifecycle (workload drain → resource lock removal → subscription cancellation → 90-day soft-delete → purge). Quota and SKU pre-provisioning before workload deployment rounds out the factory pattern.

The primary IaC implementation uses the Azure Verified Module `avm/ptn/lz/sub-vending` (Bicep) or its Terraform AVM equivalent. Per-archetype parameter files capture the governance profile for each subscription class: Corp archetypes receive stricter policy assignments and deny-public-access guardrails; Online archetypes allow selected public endpoints fronted by WAF; SaaS-Tenant archetypes inject per-tenant cost attribution tags and budget isolation. The vending machine also registers required Azure resource providers (`Microsoft.Network`, `Microsoft.Compute`, `Microsoft.Storage`) before network injection begins — a sequencing requirement that eliminates the most common pipeline failure mode.

This skill is the canonical automation story for the Billing & Tenant CAF design area in Wave 3. It does not define WHERE subscriptions belong in the hierarchy — that is the domain of `management-group-architecture` and the shared ADR. It defines HOW subscriptions arrive at the correct location with all guardrails active from minute zero.

## When to Use This Skill

- Subscription creation rate exceeds 10 new subscriptions per year (automation threshold per the shared ADR)
- ISV or SaaS platform requires per-tenant subscription isolation with consistent guardrail injection at every tenant onboarding
- Developer or application teams need self-service sandbox or dev/test subscription provisioning with spending caps and automatic expiry
- Platform team wants to guarantee that no subscription enters the estate without baseline policy, RBAC, budget alerts, and hub network connectivity
- Existing estate has manually-created subscriptions parked at root MG or missing baseline guardrails (brownfield import path)
- Decommissioning subscriptions requires a repeatable lifecycle (drain → cancel → purge) that currently relies on ad-hoc manual steps
- Quota pre-provisioning is needed to guarantee VM SKU capacity for workload deployment before the first pipeline run

## CAF Design Area Mapping

| CAF Design Area | Priority | Subscription Vending Contribution |
|-----------------|----------|------------------------------------|
| **Billing & Tenant** | **Primary** | Subscription creation requires billing scope authorization — EA enrollment account owner or MCA billing profile with `Microsoft.Subscription/aliases/write`. Every vended subscription maps to a cost center via billing scope and mandatory budget tags from day zero. Per-tenant billing isolation for ISV platforms (S5) requires MCA invoice sections or separate EA enrollment accounts. This skill is the canonical Billing & Tenant automation implementation for Wave 3. |
| **Resource Organization** | High | Vended subscriptions are placed into the archetype-specific MG (Corp, Online, SaaS-Tenant, Sandbox) via automated MG placement as part of the vending pipeline. The AVM module's `managementGroupId` parameter is mandatory — no subscription can be created and left at root. The vending pipeline enforces the hierarchy structure designed in `management-group-architecture`, translating hierarchy design into operational reality. |
| **Network Topology & Connectivity** | High | Every vended subscription receives hub-spoke VNet peering, private DNS zone delegation links, and baseline route table deployment at creation time. Network injection at vending eliminates the post-creation connectivity gap that causes teams to deploy workloads into isolated or publicly-exposed subscriptions. The vending pipeline must register `Microsoft.Network` before attempting peering — first-time RP registration adds 2-5 minutes. |
| **Governance** | High | Policy assignments, RBAC grants, and diagnostic settings are injected at subscription creation — not applied retroactively after workloads deploy. This is the shift-left governance pattern: guardrails are pre-wired and tested in the vending pipeline before any workload reaches the subscription. Drift from baseline is detectable from day one because the baseline is declared in IaC and verified on every vending run. |
| Platform Automation & DevOps | Secondary | The vending machine itself is IaC — the AVM `avm/ptn/lz/sub-vending` module in Bicep, or its Terraform AVM equivalent. Pipeline service principals require billing scope permissions, and workload identity federation (via `workload-identity-federation`) eliminates stored credentials. Automation of the subscription lifecycle — creation, guardrail injection, decommissioning — is a Platform Automation & DevOps design area concern. |

## WAF Pillar Coverage

| WAF Pillar | Priority | Specific Capabilities |
|------------|----------|-----------------------|
| **Operational Excellence** | **Primary** | Automated vending replaces 2-week manual lead time with <15-minute provisioning. Self-service intake eliminates the platform-team bottleneck for subscription creation requests. Decommissioning automation prevents orphan subscription cost leak. Idempotent IaC (AVM module) ensures consistent guardrail state regardless of who triggers the pipeline — re-running a failed vending operation is safe. The operational excellence gain IS the business case for vending: it converts a manual, error-prone, days-long process into a tested, repeatable pipeline that scales without adding headcount. |
| **Security** | High | Guardrail injection at creation ensures no subscription exists without baseline security controls: deny-public-access policy, require managed identity, diagnostic settings routing to the central Log Analytics workspace, and RBAC grants scoped to subscription. Billing scope RBAC restricts subscription creation to the automation service principal — preventing shadow IT subscription sprawl where ungoverned subscriptions accumulate outside the estate. Security Baseline rules 1-6 are assigned as policy at vending time. |
| **Cost Optimization** | High | Billing scope mapping ensures cost attribution from day zero via mandatory cost-center tags and per-subscription budget injection at creation. Budget alerts (80%/100%/120% forecast thresholds) fire on every vended subscription — no subscription can be created without a cost guardrail. Decommissioning lifecycle prevents idle subscription cost: abandoned subscriptions accrue platform fees (networking, monitoring, Defender plans) without workloads. Per-tenant billing isolation enables chargeback at ISV scale. |
| Reliability | Secondary | Quota pre-provisioning requests ensure required VM SKUs are available in the target region before workload deployment begins, preventing first-deployment failures due to insufficient capacity. Network injection at vending guarantees hub connectivity from the first workload deployment, rather than requiring manual peering requests post-creation. Subscription cancellation with 90-day soft-delete provides a recovery window if decommissioning is triggered in error. |

## Boundaries

### DO NOT USE FOR

- **Hierarchy pattern selection** — see [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) for "Choose flat / regional / workload-type hierarchy when" decision criteria and the "automate vs manual" vending threshold decision tree
- **MG hierarchy design and move operations** — see `management-group-architecture` SKILL.md (Wave 3 sibling); this skill enforces placement at vending time, it does not design the hierarchy or orchestrate bulk re-parenting
- **Azure Policy authoring and initiative design** — see `azure-policy`; this skill assigns existing policy initiatives at subscription scope during vending, it does not author custom policy definitions
- **EA-to-MCA billing agreement migration** — out of scope; MCA migration is a billing-account-level operation, not a subscription-level operation; note EA→MCA as a prerequisite for SP-based creation if the enrollment is still on classic EA (see Prerequisites)
- **VNet and subnet architecture** — see `azure-virtual-network`; this skill injects peering and DNS links into an existing hub, it does not design the hub topology or address space
- **Budget enforcement and cost alert configuration beyond injection** — see `cost-governance`; this skill injects a per-subscription budget at creation, it does not configure cross-subscription cost policies or savings recommendations
- **Workload identity for pipeline service principals** — see `workload-identity-federation` (Wave 1); this skill assumes the vending pipeline's SP has the correct billing scope permissions — federated identity credential design for that SP is out of scope here

## Architecture Patterns

### 1. AVM `avm/ptn/lz/sub-vending` Pipeline (Bicep/TF) — Recommended

The primary pattern. The AVM `avm/ptn/lz/sub-vending` module orchestrates subscription alias creation, MG placement, network injection, and baseline RBAC and policy in a single idempotent Bicep deployment. Trigger via GitHub Actions or Azure Pipelines with a per-archetype parameter file. Key inputs: `subscriptionAliasName`, `billingScope`, `managementGroupId`, `virtualNetworkPeeringEnabled`, `hubVirtualNetworkResourceId`, `roleAssignments`, and `resourceProviders` (register before peering). Output: a fully-provisioned subscription with guardrails active. Use the Terraform AVM equivalent (`azure/lz-vending` provider module) for Terraform-first estates.

```bash
# Trigger vending pipeline via Azure CLI (GitHub Actions equivalent)
az deployment mg create \
  --location southcentralus \
  --management-group-id mg-landingzones \
  --name "vend-corp-$(date +%Y%m%d%H%M)" \
  --template-file modules/avm/ptn/lz/sub-vending/main.bicep \
  --parameters @parameters/corp-archetype.json \
               subscriptionAliasName="sub-corp-teamalpha-$(date +%s)" \
               billingScope="/providers/Microsoft.Billing/billingAccounts/{enrollmentId}/enrollmentAccounts/{accountId}"

# Poll until subscription is provisioned (eventual consistency guard)
until az rest \
  --method GET \
  --uri "https://management.azure.com/providers/Microsoft.Subscription/aliases/${ALIAS}?api-version=2021-10-01" \
  --query "properties.provisioningState" -o tsv | grep -q "Succeeded"; do
  echo "Waiting for subscription provisioning..."; sleep 30
done
echo "Subscription ready — proceeding to guardrail injection."
```

### 2. Per-Archetype Vending Templates (Corp / Online / SaaS-Tenant / Sandbox)

Each subscription archetype maintains its own parameter file: Corp archetypes enforce deny-public-access and require PIM-eligible access for privileged roles; Online archetypes allow selected public endpoints with mandatory WAF policy and CDN tags; SaaS-Tenant archetypes inject per-tenant cost attribution tags (`TenantId`, `TenantTier`), a tenant-scoped budget, and a policy set appropriate for ISV-managed workloads; Sandbox archetypes enforce a spending cap and a 90-day auto-cancellation timer. The archetype parameter file is the "governance profile" for that subscription class — changes are code-reviewed and version-controlled alongside application IaC.

### 3. Multi-Tenant SaaS Per-Tenant Vending (S5)

For ISV platforms creating one subscription per customer tenant: a lightweight intake payload (JSON via API or a GitHub Issue form) captures `tenantName`, `tenantId`, `tierSKU`, and `region`; a pipeline renders the SaaS-Tenant parameter file and calls the AVM module. Each tenant subscription lands in the `LZ/Tenants/{tier}` MG branch, receives isolated VNet peering to the ISV hub, and gets a per-tenant budget with `TenantId` cost attribution. This pattern supports hundreds of vending operations per year — the practical bottleneck is the ~2,000 subscription soft limit per EA enrollment account.

```bash
# Example: vend a SaaS-Tenant subscription for customer onboarding
az deployment mg create \
  --location southcentralus \
  --management-group-id mg-lz-tenants-standard \
  --name "vend-tenant-${TENANT_ID}-$(date +%s)" \
  --template-file modules/avm/ptn/lz/sub-vending/main.bicep \
  --parameters @parameters/saas-tenant-archetype.json \
               subscriptionAliasName="sub-isv-tenant-${TENANT_ID}" \
               managementGroupId="mg-lz-tenants-standard" \
               subscriptionTags="{\"TenantId\":\"${TENANT_ID}\",\"TenantTier\":\"standard\",\"CostCenter\":\"isv-saas\"}"

# Register required resource providers before network injection
SUBSCRIPTION_ID=$(az account show --name "sub-isv-tenant-${TENANT_ID}" --query id -o tsv)
for RP in Microsoft.Network Microsoft.Compute Microsoft.Storage Microsoft.KeyVault; do
  az provider register --namespace $RP --subscription $SUBSCRIPTION_ID
done
```

### 4. Self-Service Sandbox Vending

Developer and test teams request sandboxes via a self-service intake (GitHub Issue form or Logic App web form). The Sandbox archetype has a lighter governance profile: no hub network injection (isolated by default), a 90-day auto-cancellation policy enforced by a scheduled pipeline, and a spending cap of $200/month via budget. Sandbox subscriptions land in the `Sandboxes` MG branch and inherit only the Sandbox policy initiative. Auto-cancellation is a separate scheduled pipeline that queries subscription age via Resource Graph and cancels any sandbox exceeding the retention window.

## Security Baseline Reinforcement

Subscription vending is the earliest enforcement point for Security Baseline rules — guardrails are injected by the pipeline before any workload deploys.

| Rule | Subscription Vending Enforcement |
|------|----------------------------------|
| **Rule 1 – TLS 1.2 minimum** | `Deny` policy assigned at subscription scope: storage accounts with `minimumTlsVersion < TLS1_2` and App Services with `minTlsVersion < 1.2` are blocked on deployment. |
| **Rule 2 – HTTPS-only traffic** | `Deny` policy for storage accounts with `supportsHttpsTrafficOnly: false`. App Service HTTPS-only enforcement applied via initiative assignment for Corp and SaaS-Tenant archetypes. |
| **Rule 3 – No public blob access** | `Deny` for storage accounts with `allowBlobPublicAccess: true` in Corp and SaaS-Tenant archetypes. Online archetype allows selective exemption requiring WAF-front attestation. |
| **Rule 4 – Managed Identity preferred** | `Audit` policy flags resources without managed identity. Vending pipeline provisions a subscription-scoped user-assigned managed identity for platform-level automation tasks. |
| **Rule 5 – Azure AD-only SQL auth** | `Deny` for SQL servers with `azureADOnlyAuthentication: false` in Corp archetype subscriptions. Applied as `Audit` for Online and SaaS-Tenant archetypes. |
| **Rule 6 – Public network disabled (prod)** | `Deny` for `publicNetworkAccess: Enabled` on PaaS resources (Key Vault, Storage, SQL, Cosmos DB) in Corp archetype subscriptions. Network injection ensures workloads route through hub firewall — public endpoints are not the default path. |

## Decision Heuristics

| Condition | Recommendation |
|-----------|----------------|
| Subscription creation rate > 10/year | Automate — implement the AVM vending pipeline |
| Multi-tenant SaaS with per-tenant isolation | Use Pattern 3 (SaaS-Tenant archetype vending) |
| Dev/test self-service demand | Use Pattern 4 (Sandbox vending with auto-cancel) |
| Classic EA enrollment (not MCA) | SP-based subscription creation is NOT available; use enrollment account owner identity, or plan EA→MCA migration first |
| Subscription count approaching 2,000 in a single enrollment | Provision additional EA enrollment accounts or MCA billing profiles before reaching the limit |
| Existing manually-created subscriptions to import | Brownfield import: Terraform `terraform import` or Bicep `existing` keyword + retroactive guardrail application |
| Network injection fails at vending time | Verify `Microsoft.Network` RP registration — first-time registration adds 2-5 min; add explicit RP registration step before peering |
| Subscription visible in Entra ID but not in Resource Graph | Wait 5-15 min for creation API eventual consistency; poll `GET /providers/Microsoft.Subscription/aliases/{name}` for `provisioningState: Succeeded` |

## Brownfield Scenario (Scenario S5: ISV Multi-Tenant SaaS)

An ISV has accumulated 30-80 manually-created customer tenant subscriptions over 2-3 years — each provisioned differently, some missing policy assignments, others lacking network connectivity to the ISV hub, with inconsistent cost attribution tags and no decommissioning process. The goal is to import existing subscriptions into the vending state, establish a repeatable per-tenant vending pipeline for new tenants, and decommission legacy manual creation processes. **Cross-skill sequencing:** Run after `management-group-architecture` establishes the `LZ/Tenants` MG branch for tenant placement; references `workload-identity-federation` for pipeline service principal federation to billing scope; hands off vended subscriptions to `azure-kubernetes-service` or `azure-container-apps` for workload deployment on the ISV platform.

| Step | Action | Rollback Gate |
|------|--------|---------------|
| 1 | **Audit current subscription estate.** Enumerate all subscriptions, MG placement, billing scope, creation method (manual vs automated), and baseline guardrail state. Identify shadow subscriptions at root MG. Export via `az account list --all` and Resource Graph queries. | Discovery only — no Azure resources modified. |
| 2 | **Map billing scope.** Document EA enrollment accounts or MCA billing profiles. Identify who holds `Microsoft.Subscription/aliases/write`. Determine whether the current billing structure supports per-tenant isolation at scale — check cumulative subscription count against the ~2,000 enrollment soft limit. | Documentation only — no Azure resources modified. |
| 3 | **Design vending parameters.** Define the SaaS-Tenant archetype parameter file: target MG (`LZ/Tenants/{tier}`), network connectivity spec (hub VNet resource ID, private DNS zone resource IDs), baseline policy initiative assignment, budget cap, and required tags (`TenantId`, `TenantTier`, `CostCenter`). | Design artifact — no Azure resources created. |
| 4 | **Deploy vending automation.** Provision the AVM `avm/ptn/lz/sub-vending` pipeline. Configure billing scope service principal with `Microsoft.Subscription/aliases/write` and `Microsoft.Management/managementGroups/subscriptions/write`. Validate with a sandbox SaaS-Tenant subscription against the archetype parameter file. | Destroy vending pipeline infrastructure; no tenant subscriptions created at this step. |
| 5 | **Vend first non-production tenant subscription.** Trigger the pipeline for a dev/test tenant. Validate: subscription lands in `LZ/Tenants/Dev`, Defender compliance score meets baseline, VNet peering is active, private DNS resolves ISV platform services, budget alert fires at 80% threshold. | Cancel subscription within 30-day grace period; undo peering and DNS links manually. |
| 6 | **Vend production tenant subscriptions.** Trigger in batches of 10. Include quota pre-provisioning for required VM SKUs before first workload deployment. Monitor Defender compliance score per subscription; verify per-tenant cost attribution in Cost Management with `TenantId` dimension. | Cancel with workload drain; 90-day recovery window applies. |
| 7 | **Migrate existing manually-created subscriptions.** For tenants already using manually-created subscriptions: import into Terraform state (`terraform import azurerm_subscription.tenant_{id}`) or declare as Bicep `existing` resource; apply guardrails retroactively (policy assignment, RBAC, budget, tags); move subscription to correct MG (`LZ/Tenants/{tier}`) per blast-radius analysis from `management-group-architecture`. | Revert MG move and remove retroactive guardrail assignments if compliance evaluation gaps appear post-move. |
| 8 | **Decommission legacy manual process.** Apply a `Deny` policy at the billing scope that blocks subscription creation except via the automation service principal. Document the self-service vending intake process (GitHub Issue form or portal form). Communicate intake SLA (<15 min) to application and sales teams. | Re-enable manual creation path via policy exemption if a vending pipeline outage is declared. |

## Prerequisites and Caveats

Before applying this skill, verify these conditions hold for your environment. Unmet prerequisites are the primary cause of vending pipeline failures that appear correct in design but break in implementation.

| Prerequisite | Impact | Guidance |
|--------------|--------|----------|
| **EA vs. MCA billing scope** | EA enrollment account-based creation requires a human account owner (not SP) in classic EA. MCA billing profiles support SP-based creation and are the strategic Microsoft direction. | Confirm billing agreement type during Step 1 requirements. Flag EA→MCA migration as a prerequisite if fully automated SP-based vending is required. |
| **Billing scope permissions** | `Microsoft.Subscription/aliases/write` must be granted to the vending SP on the EA enrollment account or MCA billing profile scope. This is a non-ARM permission — assigning it requires billing account admin access, not Azure RBAC. | Grant during platform setup. Validate with `az billing account list` before the first pipeline run. |
| **Management Group Global Admin elevation** | First-time access to tenant root MG requires the `Access management for Azure resources` toggle in Entra ID Portal. This is a one-time action that creates an audit event and must be removed after initial hierarchy setup. | Document in the deployment runbook. Schedule during maintenance window. Remove elevation after hierarchy bootstrap completes. |
| **AVM module version pinning** | The `avm/ptn/lz/sub-vending` module receives regular updates. Unpinned module references (`br/public:avm/ptn/lz/sub-vending:latest`) may pull breaking changes into production vending pipelines. | Pin to a specific module version (`br/public:avm/ptn/lz/sub-vending:0.3.0`). Review release notes before upgrading. |
| **Blueprint deprecation** | Azure Blueprints is deprecated (retirement 2026-07-11). Blueprint-locked subscriptions cannot be moved between MGs via the ARM move API. | Assess Blueprint usage during Step 0 brownfield discovery. Plan Blueprint→Policy + DINE migration as a prerequisite for any MG placement that requires moving locked subscriptions. |

## Hidden Assumptions

1. **EA enrollment account owner permission model.** In classic EA agreements, only the enrollment account owner — a person, not a service principal — can create subscriptions programmatically. Service principal-based creation via `PUT /providers/Microsoft.Subscription/aliases` requires either a Microsoft Customer Agreement billing profile or a Microsoft Partner Agreement. Organizations still on classic EA must either have the enrollment account owner trigger pipeline runs, or plan an EA→MCA migration before enabling fully-automated SP-based vending at scale.

2. **Subscription creation API eventual consistency.** The `PUT /providers/Microsoft.Subscription/aliases/{aliasName}` endpoint returns HTTP 202 Accepted — not 201 Created. The subscription may take 5-15 minutes to become visible in Resource Graph, MG membership, and the ARM management plane. Vending pipelines that immediately attempt guardrail injection (policy assignment, VNet peering, diagnostic settings) after the 202 response will fail. Pipelines must poll `GET /providers/Microsoft.Subscription/aliases/{aliasName}` and wait for `provisioningState: Succeeded` before chaining any downstream operations.

3. **Subscription limit per billing scope.** EA agreements carry a soft limit of approximately 2,000 subscriptions per enrollment account. ISV SaaS platforms with hundreds or thousands of customer tenants will hit this limit, requiring multiple EA enrollment accounts or MCA billing profiles with independent subscription capacity. The vending pipeline must route creation requests to the correct billing scope based on current subscription count — otherwise creation fails silently with a quota error and the pipeline has no clear error signal.

4. **Network injection timing dependency and RP registration.** VNet peering and private DNS zone linking require the `Microsoft.Network` resource provider to be registered in the target subscription. In a brand-new subscription, RP registration triggers automatically on first resource deployment but completes asynchronously (2-5 minutes). Pipelines that attempt VNet peering immediately after subscription creation will fail with a "provider not registered" error. The AVM module's `resourceProviders` parameter should explicitly register `Microsoft.Network`, `Microsoft.Compute`, and `Microsoft.Storage` as a dedicated step before any network injection call.

5. **Subscription cancellation is NOT deletion.** When a subscription is cancelled via the API or portal, it enters a recoverable disabled state for 90 days. During this window the subscription still counts against the ~2,000-subscription billing limit, resource locks remain in place (blocking resource cleanup), and the subscription alias cannot be reused by name. True deletion requires a Microsoft support request after the 90-day window closes. Decommissioning pipelines must account for the deferred quota reclamation, and naming conventions should incorporate a uniqueness suffix (timestamp or short GUID) to prevent collision with pending-deletion subscriptions.

## Anti-Patterns

### Anti-Pattern 1: Manual Subscription Creation as Default

Relying on portal-based or ad-hoc subscription creation skips guardrail injection entirely. New subscriptions arrive without policy assignments, without budget alerts, without network peering, and without RBAC grants. Over time, these unguarded subscriptions become shadow IT vectors — workloads deploy into ungoverned space, cost attribution is absent, and no decommissioning process exists. When the platform team eventually audits the estate, each manually-created subscription represents hours of remediation work: retroactive policy assignment, network peering setup, tag application, and budget configuration. For ISV platforms (S5) creating tens of subscriptions per year, this compounds into an unmanageable governance backlog within 12-18 months. The shared ADR's decision tree sets 10 subscriptions per year as the automation threshold — above that, the remediation cost of manual creation exceeds the vending implementation investment within one fiscal year.

**Corrective action:** Implement the AVM `avm/ptn/lz/sub-vending` pipeline and apply a `Deny` policy at the billing scope that prevents subscription creation except via the automation service principal. Route all subscription requests through the vending intake form. The investment in vending automation pays back within 3-5 subscriptions — after that, every new subscription arrives pre-governed at no additional platform team effort.

### Anti-Pattern 2: Vending Without Guardrail Injection at Creation

Deploying the vending pipeline to automate subscription creation but deferring guardrail injection ("we'll add policies later") is the most common vending anti-pattern. The subscription is created quickly — but without policy assignments, RBAC grants, diagnostic settings, or budget alerts. The "inject later" step is invariably deprioritized under workload delivery pressure, so the subscription operates ungoverned for weeks or months. Drift accumulates: a developer adds a public storage account, a missed budget alert allows $5,000 of unmonitored spend, and an audit finds no diagnostic data because the Log Analytics workspace connection was never configured. By the time guardrails are applied retroactively, the remediation effort equals or exceeds the manual-creation scenario.

**Corrective action:** Guardrail injection must be a non-negotiable step in the vending pipeline — executed as part of the same idempotent run as subscription creation, not as a separate downstream action. The AVM `avm/ptn/lz/sub-vending` module supports `roleAssignments`, `policyAssignments`, `diagnosticSettings`, and `hubVirtualNetworkResourceId` as first-class parameters in the same deployment call. If guardrail injection fails, the pipeline must fail — not produce a subscription without guardrails. A subscription that exists but is ungoverned is worse than no subscription, because it creates the illusion of governance without the substance.

### Anti-Pattern 3: No Decommissioning Lifecycle

Creating subscriptions without a corresponding decommissioning process produces subscription sprawl. Abandoned subscriptions accumulate at the rate of creation — and each one carries a platform tax even with no workloads: network peering consumes hub gateway bandwidth, diagnostic settings forward empty logs to Log Analytics (billed by ingestion volume), and Defender for Cloud plans generate per-subscription fees regardless of workload density. An ISV platform (S5) with 200 customer tenants and no decommissioning process can accumulate $30,000–$50,000 per year in platform fees for subscriptions belonging to churned customers. The 90-day soft-delete window further complicates cleanup: cancelled subscriptions continue to count against the ~2,000-subscription billing limit until the window expires.

**Corrective action:** Design decommissioning as a first-class pipeline stage alongside creation. The lifecycle flow: churn or decommission signal → workload drain validation → remove resource locks → trigger subscription cancellation via API → mark subscription as `decommissioned` in the vending manifest → automated check at 90-day mark confirms all resources are gone → request deletion via support if required. Implement a scheduled pipeline that flags subscriptions with zero resource deployments for more than 30 days as decommission candidates for platform team review.

### Anti-Pattern 4: Vending Service Principal with Over-Scoped Permissions

For ISV vending, using a single service principal with Owner rights across all vended subscriptions creates a disproportionate blast radius: if the vending SP credential is compromised, every tenant subscription is exposed. This is compounded when the same SP is shared with deployment pipelines, monitoring agents, or other automation — the vending SP becomes a master key for the entire ISV platform estate. Classic EA enrollment account owners often end up in this pattern because the enrollment account permission model conflates "can create subscriptions" with "owns all subscriptions created."

**Corrective action:** Scope the vending service principal to the minimum required permissions: `Microsoft.Subscription/aliases/write` at billing scope and `Microsoft.Management/managementGroups/subscriptions/write` at the target MG. Post-creation RBAC and guardrail injection should use a separate, subscription-scoped managed identity provisioned during the vending run — not the billing-scope SP. Use `workload-identity-federation` to eliminate stored SP credentials for the pipeline entirely. Operational access to vended tenant subscriptions must use per-subscription identities — never the vending SP.

### Anti-Pattern 5: Vending Into Root MG Instead of Correct Archetype MG

Vending pipelines that omit MG placement — or that specify the tenant root MG as the target — negate the governance inheritance model. Subscriptions at root MG inherit only the minimal root-level policy assignments; they receive none of the Corp, Online, or SaaS-Tenant archetype controls. The entire value of the MG hierarchy is lost: differentiated policy inheritance per workload class, RBAC boundary per archetype, and blast-radius scoping by subscription tier are all dependent on correct MG placement at creation. This pattern typically emerges when the vending pipeline is implemented before the MG hierarchy is designed — subscriptions land at root as a "we'll move them later" compromise that becomes permanent as workloads deploy and post-creation moves become risky.

**Corrective action:** MG placement is a required input to the vending pipeline — never optional. The AVM `avm/ptn/lz/sub-vending` module's `managementGroupId` parameter is mandatory; omitting it is a pipeline error, not a fallback to root. Validate at pipeline entry that the target MG exists, matches an approved archetype (Corp/Online/SaaS-Tenant/Sandbox), and that the subscription's workload classification justifies that archetype. Reference `management-group-architecture` for archetype definitions and [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) for the hierarchy pattern that determines where each archetype MG lives.

## Diagnostic Queries

### KQL: Identify subscriptions at tenant root MG (no archetype placement)

```kql
ResourceContainers
| where type == "microsoft.resources/subscriptions"
| extend mgPath = tostring(properties.managementGroupAncestorsChain)
| where mgPath contains "\"name\":\"Tenant Root Group\""
      and not(mgPath contains "\"name\":\"mg-landingzones\"")
      and not(mgPath contains "\"name\":\"mg-sandboxes\"")
| project name, subscriptionId, mgPath
| order by name asc
```

### KQL: Subscriptions missing mandatory vending tags (cost attribution gap)

```kql
ResourceContainers
| where type == "microsoft.resources/subscriptions"
| extend tags = todynamic(tags)
| where isempty(tags["CostCenter"])
       or isempty(tags["Environment"])
       or isempty(tags["ManagedBy"])
| project name, subscriptionId, tags
| order by name asc
```

### KQL: Subscriptions with no budget resource (guardrail injection gap)

```kql
Resources
| where type == "microsoft.consumption/budgets"
| summarize hasBudget = count() by subscriptionId
| join kind=rightanti (
    ResourceContainers
    | where type == "microsoft.resources/subscriptions"
    | project subscriptionId = subscriptionId, subscriptionName = name
  ) on subscriptionId
| project subscriptionName, subscriptionId
| order by subscriptionName asc
```

### KQL: Cancelled subscriptions still counting against enrollment limit (90-day window)

```kql
ResourceContainers
| where type == "microsoft.resources/subscriptions"
| where properties.state == "Disabled" or properties.state == "Deleted"
| extend cancelledDate = tostring(properties.managedByTenants)
| project name, subscriptionId, state = tostring(properties.state)
| order by state asc
```

## References

| Resource | Notes |
|----------|-------|
| **[`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md)** | **Shared ADR — read first.** Canonical hierarchy-pattern and vending-threshold decision tree. Defines "automate vs manual" criteria, scenario mapping, and brownfield assessment lens referenced by this skill's Decision Heuristics and Brownfield Scenario. |
| [`management-group-architecture`](../management-group-architecture/SKILL.md) | Wave 3 sibling. This skill enforces MG placement at vending time; that skill designs the hierarchy. Brownfield import Step 7 references its blast-radius analysis gate. |
| [`workload-identity-federation`](../workload-identity-federation/SKILL.md) | Wave 1 soft prereq. Federated identity credential lifecycle for the vending pipeline SP — eliminates stored credentials for billing-scope subscription creation. |
| [`azure-resource-manager`](../azure-resource-manager/SKILL.md) | Hard prereq. Subscription alias API (`Microsoft.Subscription/aliases`), ARM resource provider registration, and `existing` resource declaration for brownfield import. |
| [`azure-policy`](../azure-policy/SKILL.md) | Hard prereq. Policy initiative authoring, built-in initiatives, and assignment syntax used in guardrail injection. This skill assigns; that skill authors. |
| [AVM `avm/ptn/lz/sub-vending` (Bicep)](https://github.com/Azure/bicep-registry-modules/tree/main/avm/ptn/lz/sub-vending) | Azure Verified Module — primary IaC implementation for subscription vending. Covers alias creation, MG placement, RBAC injection, network peering, and resource provider registration. |
| [ALZ Reference — Subscription Vending Design Area](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/subscription-vending) | CAF subscription vending guidance: billing scope setup, vending machine patterns, and ALZ-aligned archetype parameter design. |
| [Programmatic subscription creation](https://learn.microsoft.com/azure/cost-management-billing/manage/programmatically-create-subscription) | Microsoft Learn: `PUT /providers/Microsoft.Subscription/aliases`, EA vs MCA creation flows, eventual consistency, and alias resource lifecycle. |
| [MCA billing scopes and invoice sections](https://learn.microsoft.com/azure/cost-management-billing/understand/mca-overview) | MCA billing account → billing profile → invoice section hierarchy required for SP-based subscription creation at scale. |
| [`azure-kubernetes-service`](../azure-kubernetes-service/SKILL.md) | Wave 2. Vended subscriptions for ISV compute platforms hand off to AKS for containerized workload deployment. |
| [`azure-container-apps`](../azure-container-apps/SKILL.md) | Wave 2. Alternative compute platform for vended subscriptions in serverless-eligible ISV SaaS scenarios. |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-18 | Saul | Initial Wave 3 authoring — subscription vending pipeline design, AVM `avm/ptn/lz/sub-vending` patterns, per-archetype guardrail injection, Security Baseline reinforcement table, brownfield S5 ISV multi-tenant 8-step playbook, 5 concrete hidden assumptions, 5 anti-patterns, shared ADR cross-reference (`billing-tenant-hierarchy.md`). |

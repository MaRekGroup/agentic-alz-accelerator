---
name: azure-arc-servers
description: "Azure Arc-enabled servers for hybrid estate governance — onboarding, machine configuration, extensions, and policy. USE FOR: Arc-enabled server onboarding (azcmagent, deployment scripts, at-scale via MI or SP), guest configuration / machine configuration policy authoring, Arc extension management (AMA, MDE, Custom Script, Dependency Agent), Azure Policy assignment to Arc-enrolled servers, Defender for Servers Plan 2 on Arc machines, Update Manager for Arc, inventory queries via Resource Graph, and brownfield hybrid-estate hardening (S6). DO NOT USE FOR: Arc-enabled Kubernetes (use azure-arc-kubernetes), native Azure VM management (use azure-virtual-machines), Entra hybrid identity / AD Connect (use entra-connect-hybrid-identity), on-prem network connectivity (use azure-expressroute / azure-vpn-gateway), Azure Policy authoring syntax (use azure-policy), or Arc vs. migrate decision (see docs/decisions/hybrid-onboarding-strategy.md)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-hybrid
  wave: "5"
---

# azure-arc-servers

| Field | Value |
|-------|-------|
| **Skill ID** | `azure-arc-servers` |
| **Domain** | Azure Hybrid — Arc-enabled Servers |
| **Wave** | 5 — Hybrid |
| **Hard Prereqs** | `azure-policy` |
| **Soft Prereqs** | `azure-monitor`, `azure-defender-for-cloud`, `workload-identity-federation` (W1) |
| **Shared ADR** | [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) |
| **Primary CAF Area** | Management (primary); Governance, Security |
| **Primary WAF Pillar** | Operational Excellence (primary); Security, Reliability |
| **Brownfield Scenario** | S6 — Hybrid Estate Governance |
| **Authored** | Wave 5 · 2026-05-19 · Saul |

Arc-enabled servers project physical machines and VMs from any hypervisor, on-premises data center, or other cloud into Azure Resource Manager as `Microsoft.HybridCompute/machines` objects. Once projected, they are first-class Azure resources: subject to Azure Policy, visible in Resource Graph, targetable by Defender for Cloud, Update Manager, and Monitor — using the same governance infrastructure already established for native Azure resources. This skill enables Oracle, Assessor, Warden, and Forge to architect, deploy, and govern Arc server onboarding at scale.

**When to use this skill:** Use when on-premises or multi-cloud VMs must participate in Azure Policy, Resource Graph inventory, Defender for Servers P2 coverage, or AMA-based centralized logging. Consult [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) to confirm Arc is the right governance extension versus native migration before applying this skill.

## Overview

This skill covers the full operational surface of Azure Arc-enabled servers: onboarding (azcmagent installation, at-scale deployment scripts, MI-first credential pattern), guest configuration / machine configuration policy (DSC-based OS baselines, CIS benchmarks, custom configs), Arc extension management (AMA, MDE, Dependency Agent, Custom Script Extension), Arc-scoped Azure Policy assignments, Defender for Servers Plan 2 enrollment, Update Manager patch compliance, and observability via Resource Graph and Azure Monitor. Supported platforms include Windows Server 2012+ and major Linux distributions (Ubuntu, RHEL, SUSE, Debian, CentOS) on any hypervisor or bare metal.

The Arc-vs-migrate decision boundary — when to project resources into Arc versus lifting them to native Azure VMs — is defined in [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md). **Connect to Arc when** on-premises resources must participate in Azure Policy and Resource Graph, guest configuration enforcement is required on non-Azure hosts, Defender for Servers P2 is needed for non-Azure coverage, AMA or Update Manager must centralize logging and patch compliance at hybrid scale, or brownfield hybrid estate inventory must surface in the Step 0 Assessor KQL collectors. This skill goes deep on HOW to configure Arc-enabled servers within those boundaries — it does not redefine the decision tree.

**Out of Scope:**
- Arc-enabled Kubernetes clusters (connection, Flux, constraint templates, OIDC) → `azure-arc-kubernetes`
- Native Azure VM lifecycle management (sizing, VMSS, availability sets) → `azure-virtual-machines`
- Entra hybrid identity / Azure AD Connect → `entra-connect-hybrid-identity`
- ExpressRoute / VPN connectivity to on-premises environments → `azure-expressroute` / `azure-vpn-gateway`
- Azure Policy guest configuration authoring syntax in depth → `azure-policy`
- Arc data services (SQL MI on Arc, PostgreSQL on Arc) → explicitly out of scope per ADR §1 (catalog final at 14)

## When to Use This Skill

- Designing Arc-enabled server onboarding for an on-premises server fleet that must participate in Azure Policy and Resource Graph
- Configuring machine configuration (guest config) policy baselines — CIS benchmarks, custom DSC configs, OS hardening profiles
- Managing the Arc extension deployment sequence: AMA for log ingestion, MDE for endpoint protection, Dependency Agent for service map
- Enrolling non-Azure servers in Defender for Servers Plan 2 via Arc enrollment as the mandatory coverage layer
- Configuring Update Manager to centralize patch compliance across hybrid Arc-enrolled machines
- Extending brownfield Step 0 Assessor discovery beyond the Azure subscription boundary to surface on-premises servers in Resource Graph
- Remediating S6 Hybrid Estate Governance gaps: unmanaged on-premises servers lacking Policy coverage, monitoring, or Defender enrollment
- Authoring Resource Graph KQL queries to inventory Arc machine compliance state, extension health, and agent version drift

## When NOT to Use This Skill

| Out-of-Scope | Use Instead |
|--------------|-------------|
| Arc-enabled Kubernetes (GitOps, Flux v2, constraint templates, OIDC issuer) | `azure-arc-kubernetes` |
| Native Azure VM management (sizing, VMSS, availability sets, Azure extensions on IaaS VMs) | `azure-virtual-machines` |
| Entra hybrid identity / Azure AD Connect / Cloud Sync | `entra-connect-hybrid-identity` |
| ExpressRoute or VPN connectivity from on-premises to Azure | `azure-expressroute` / `azure-vpn-gateway` |
| Azure Policy authoring syntax (effect types, initiative definitions, remediation tasks) | `azure-policy` |
| RBAC role assignments for Arc resource management | `azure-rbac` |
| AMA workbook and alert rule authoring for Arc servers | `azure-monitor` |
| Defender for Cloud alert triage and recommendation remediation | `azure-defender-for-cloud` |
| Arc data services (SQL MI on Arc, PostgreSQL on Arc) | Out of scope — catalog final at 14 (see ADR §1) |
| Arc vs. migrate decision criteria for a specific workload | [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) |

## CAF Design Area Mapping

| CAF Design Area | Coverage | Primary |
|-----------------|----------|---------|
| **Management** | AMA extension deployment and DCR association for centralized log ingestion; Update Manager patch compliance and scheduled maintenance windows; Azure Monitor metrics and alert rules for Arc machine availability; hybrid inventory visibility via Resource Graph and Azure Portal single pane of glass | ✅ |
| **Governance** | Guest configuration / machine configuration policy baselines (CIS benchmarks, OS hardening); Azure Policy assignment inheritance at MG scope covering Arc-enrolled machines; Resource Graph KQL collectors for hybrid compliance posture; policy compliance dashboard surfacing brownfield drift | ✅ |
| **Security** | Defender for Servers Plan 2 enrollment via Arc (mandatory for non-Azure host coverage); MDE extension deployment for endpoint detection and response; guest config security baselines enforcing CIS and NIST controls at OS level; MI-first credential pattern eliminating SP secret rotation risk | ✅ |
| Identity & Access | Onboarding credential scope (MI-first via Azure Automation Hybrid Runbook Worker per ADR §5; SP fallback scoped to subscription/RG only); `Azure Connected Machine Onboarding` role minimum scope; Arc resource RBAC for Warden and Forge operations | |
| Platform Automation & DevOps | At-scale onboarding automation via deployment scripts and Azure Automation HRW; CI/CD pipeline integration for Arc registration in greenfield LZ bootstraps; IaC (Bicep/Terraform) for Arc extension deployment via AVM modules | |

## WAF Pillar Coverage

| WAF Pillar | Coverage | Primary |
|------------|----------|---------|
| **Operational Excellence** | Single pane of glass for hybrid inventory via Resource Graph and Azure Portal; AMA unifies log ingestion from on-premises and Azure resources into a single Log Analytics workspace; Update Manager centralizes patch compliance and scheduled maintenance across Arc fleet; extension lifecycle managed through Arc extension resource model, surfacing version drift as policy compliance findings | ✅ |
| **Security** | Defender for Servers Plan 2 + MDE brings Azure security posture to on-premises hosts without migrating workloads; guest configuration enforces OS-level CIS and NIST baselines on Arc machines; MI-first onboarding credential per ADR §5 eliminates per-resource SP secret rotation risk at scale; machine configuration remediates compliance drift via desired-state enforcement | ✅ |
| **Reliability** | Machine configuration (DSC) enforces desired-state configuration baselines, reducing configuration drift that causes unplanned outages; Update Manager maintains patch currency on the hybrid fleet, reducing CVE exposure on long-lived on-premises hosts; guest config audit mode provides early-warning compliance signal before enforcement causes availability impact | ✅ |
| Cost Optimization | Arc control plane and base extensions (AMA, Dependency Agent) are free; Defender for Servers Plan 2 billed per enrolled server/month — tag-scoped Defender assignment limits cost to actively governed machines; Update Manager centrally eliminates per-server WSUS/SCCM infrastructure overhead | |

*Performance Efficiency is intentionally excluded: Arc is control-plane only and has no impact on the workload data path or host compute performance (per ADR §6 WAF trade-off matrix).*

## Greenfield Patterns

For greenfield hybrid estates — new on-premises infrastructure built alongside a new Azure Landing Zone — Arc onboarding runs at day 0 rather than retrofitting. The same sequence applies as brownfield, but without the assessment and remediation steps. Arc projection is purely additive to the ARM namespace: no existing subscription, policy assignment, network resource, or managed identity is modified by connecting Arc servers.

### 1. Azure Automation Hybrid Runbook Worker (MI-First)

The default onboarding credential pattern for greenfield estates is Managed Identity via Azure Automation Hybrid Runbook Worker, per [`docs/decisions/hybrid-onboarding-strategy.md` §5](../../../docs/decisions/hybrid-onboarding-strategy.md). This eliminates service principal secrets entirely from the onboarding pipeline. Deploy the Azure Automation account in the Management subscription of the Landing Zone hub; configure a Hybrid Runbook Worker group pointing to a set of bootstrap machines (or Azure VMs) with outbound connectivity to the target on-premises network. The Runbook generates and distributes `azcmagent` deployment scripts using the Automation Account's system-assigned managed identity, scoped to `Azure Connected Machine Onboarding` role on the target subscription.

The service principal fallback (see ADR §5) is appropriate only for isolated legacy environments where the on-premises network cannot reach a Hybrid Runbook Worker endpoint. When SP fallback is required, use a single SP scoped to the target subscription or resource group — never per-machine or per-batch SPs (anti-pattern: credential proliferation).

### 2. Day-0 Policy Assignment at Management Group Scope

For greenfield, assign machine configuration policy initiatives at the MG scope in **audit** mode before any servers are enrolled. Servers enrolled into a scope with no policy assignments deliver zero governance value (anti-pattern: vanity Arc). Recommended initiatives to assign at day 0:

- `[Preview]: Configure Windows machines to run Azure Monitor Agent` (built-in)
- `Configure Linux machines to run Azure Monitor Agent` (built-in)
- `[Preview]: Deploy requirements to enable guest configuration policies on virtual machines` (built-in prerequisite)
- Custom CIS Level 1 machine configuration baseline for the estate's OS distribution mix

Switch audit-mode policies to **deny/deployIfNotExists** only after validating compliance state on the first enrolled cohort — premature deny-mode blocks onboarding scripts that rely on agent installation order.

### 3. IaC Extension Deployment via AVM Modules

For Bicep and Terraform IaC generation (Step 5 Forge), use AVM modules for Arc extension deployment. Extension deployment sequence is order-sensitive: AMA must be installed before MDE (MDE log pipeline depends on AMA workspace configuration); Dependency Agent requires MMA/AMA already running. Forge should parameterize the Log Analytics workspace resource ID and Defender workspace as IaC variables — never hardcoded.

### 4. Resource Group and Tagging Policy at Arc Enrollment

Configure a dedicated resource group for Arc machine objects (e.g., `rg-arc-servers-<region>-<env>`) with the CAF-required tags (`Environment`, `Owner`, `CostCenter`, `Project`, `ManagedBy`) at resource group creation. The Arc deployment script accepts a `--resource-group` parameter — parameterize at day 0 so all enrolled machines inherit the correct tag scope. Apply an `append` policy to ensure tags propagate to Arc machine resources even if enrollment scripts omit them.

## Brownfield Scenario (Scenario S6: Hybrid Estate Governance)

This skill sequences after `azure-policy` (MG-scoped policy assignments established) and benefits from `azure-monitor` (Log Analytics workspace and AMA DCRs) for centralized telemetry. Use this brownfield playbook in conjunction with the Arc vs. migrate decision criteria from [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) — evaluate each server cohort against the "Migrate to Azure When" table before proceeding to Phase 4 onboarding.

Typical brownfield S6 findings: on-premises server fleet entirely invisible to Resource Graph and Azure Policy, Defender for Servers P2 coverage terminated at the Azure subscription boundary (on-premises hosts unprotected), no centralized patch compliance visibility (WSUS/SCCM silos), log ingestion fragmented across disparate on-premises SIEM agents rather than unified AMA pipeline, and zero machine configuration policy assignments on non-Azure hosts. The 8-step playbook below sequences remediation from read-only discovery through the irrevocable hard-gate actions, with rollback types specified for each step.

| Step | Action | Rollback Type |
|------|--------|---------------|
| 1 | Inventory: Resource Graph query for existing `Microsoft.HybridCompute/machines` (already Arc-enrolled) and cross-reference against on-premises CMDB export. Identify unenrolled server cohorts by OS, location, and business unit. | Read-only |
| 2 | Assess connectivity prerequisites per ADR §5 Phase 3: verify outbound HTTPS (port 443) to Arc endpoint URLs (`aka.ms/AzureArcNetworkRequirements`) from each target subnet. Confirm proxy path or private endpoint if direct internet egress is unavailable. | Read-only |
| 3 | ⛔ **HARD GATE — Onboarding credential scope**: Before generating any onboarding credential (MI via HRW per ADR §5, or SP fallback), confirm the credential is scoped to `Azure Connected Machine Onboarding` role at the target subscription or resource group — NOT at root MG level. MI-first via Azure Automation HRW is the mandatory default per ADR §5; SP fallback requires explicit justification. A credential scoped too broadly that leaks grants an attacker the ability to enroll any machine in the tenant as an Arc resource. Scope is set at credential creation — narrowing scope after leakage requires credential revocation, which cascades to all in-flight onboarding operations. | Irrevocable scope decision — credential must be revoked and recreated if scope is incorrect. Treat as irreversible. |
| 4 | Generate `azcmagent` deployment scripts (portal wizard or ARM API `onboardingScripts`); parameterize with environment tag values (CAF required tags), resource group, and subscription ID. Distribute to target machines via Automation HRW runbook, SCCM/Intune script policy, or manual execution on first cohort for validation. | Soft rollback (re-run `azcmagent disconnect` to deregister; machine disappears from Resource Graph; no data deleted) |
| 5 | Assign machine configuration policy initiative at MG scope in **audit** mode: CIS Level 1 baseline for enrolled OS distributions; AMA/DCR prerequisite extension policy. Validate compliance state in Policy compliance dashboard before switching to `deployIfNotExists` enforcement mode. | Soft rollback (remove policy assignment; compliance posture returns to pre-assignment state) |
| 6 | Deploy Arc extensions in dependency order: (1) AMA + DCR association (log ingestion pipeline), (2) MDE (Defender for Endpoint — requires AMA workspace registration), (3) Dependency Agent (service map — requires AMA). Validate each extension's provisioning state before installing the next. Enable Defender for Servers Plan 2 at subscription scope to activate auto-provisioning of MDE for Arc machines. | Soft rollback (remove extensions individually; no data deleted; Defender coverage gap opens immediately on extension removal — coordinate with SOC) |
| 7 | ⛔ **HARD GATE — MDE extension removal severs Defender coverage**: Removing the MDE extension from an Arc-enrolled production server disconnects Defender for Servers P2 coverage immediately and permanently for that machine until re-enrollment is completed. There is no graceful drain or alert-capture window. Coordinate explicit SOC sign-off and a maintenance window before any MDE extension removal in production. Once removed, any threat events on that machine between removal and re-enrollment are not captured in MDE — the gap is unrecoverable. | Irrevocable coverage gap — MDE telemetry between removal and re-enrollment is permanently lost. Cannot be restored retroactively. |
| 8 | Validate full posture: Resource Graph compliance query for all Arc machines (extension health, agent version, policy compliance state); Defender for Cloud secure score delta; Update Manager patch compliance report for Arc fleet. Enable machine configuration `deployIfNotExists` enforcement mode for validated cohorts. | Soft rollback (switch enforcement policies back to audit mode; no deployed resources removed) |

**Pre-HARD-GATE Verification Checklist:**

Before Step 3 (credential scope): (a) confirm Azure Automation Hybrid Runbook Worker is deployed and reachable from the target on-premises network; (b) if SP fallback is required, document the justification (HRW unreachable due to network isolation); (c) assign `Azure Connected Machine Onboarding` role to the credential at the narrowest available scope (resource group preferred, subscription if RG scope is impractical); (d) enable Azure AD audit logging to record all credential usage during the onboarding window.

Before Step 7 (MDE extension removal, if required): (a) confirm SOC has been notified and acknowledged the coverage gap window; (b) schedule the removal during a declared maintenance window with incident response on standby; (c) have the re-enrollment script ready to execute immediately after removal; (d) confirm no active Defender incidents are open for the affected machines before proceeding.

## Security Baseline Alignment

Arc-enabled servers directly enforce and extend the non-negotiable Security Baseline rules against non-Azure hosts.

| Rule | Arc-Enabled Server Enforcement |
|------|--------------------------------|
| **Rule 4 – Managed Identity preferred** | MI-first onboarding credential via Azure Automation Hybrid Runbook Worker (ADR §5 canonical reference) eliminates service principal secrets from the onboarding pipeline. All Arc machines onboarded via MI-first inherit System-Assigned identity through the `Microsoft.HybridCompute/machines` resource object, enabling downstream managed-identity auth patterns. |
| **Rule 6 – Public network disabled (prod)** | Arc agent communication to Azure endpoints can be routed via Private Link for Arc (Arc Private Link Scope resource) to eliminate public internet exposure of Arc management traffic in production. Defender for Servers P2, enabled through Arc enrollment, enforces network baseline and JIT access controls on Arc-enrolled machines analogous to native VM protection. |

*Rules 1–3 and Rule 5 are enforced on Arc-enrolled machines via machine configuration (guest config) policy: CIS baselines mandate TLS 1.2+, HTTPS-only service bindings, and local account hardening. Arc does not surface these rules on the Arc resource itself — it surfaces them through the policy compliance pipeline.*

## Architecture Patterns

### 1. At-Scale Arc Onboarding with MI-First Credentials

For large server fleets (>50 machines), at-scale onboarding uses the Azure Arc deployment script generator (portal or ARM API) combined with Azure Automation Hybrid Runbook Worker. The Runbook iterates over a CMDB-sourced machine list, invokes the generated `azcmagent` script via WinRM (Windows) or SSH (Linux), and reports per-machine enrollment status to a Log Analytics custom table. MI-first via the Automation Account's system-assigned identity scoped to `Azure Connected Machine Onboarding` eliminates credential rotation entirely from the onboarding runbook. Tag injection (`--tags "Environment=Prod;Owner=PlatformTeam"`) at script invocation time ensures all enrolled machines inherit CAF-required tags from day 0.

**SP fallback pattern (when HRW is unreachable):** A single service principal with `Azure Connected Machine Onboarding` scoped to the target subscription. Never create per-machine or per-batch SPs — credential proliferation is a hard anti-pattern (see Anti-Patterns).

### 2. Machine Configuration Policy Baselines

Machine configuration (formerly guest configuration) uses Azure Policy to audit and enforce DSC-based configuration on Arc-enrolled machines. Key built-in initiatives for Arc server fleets: `[Preview]: Configure Windows machines to run Azure Monitor Agent`, `Configure Linux machines to run Azure Monitor Agent`, and CIS Level 1 Windows/Linux baselines. Custom machine configuration packages (`.nupkg` DSC module bundles) deploy via the `DeployIfNotExists` policy effect, triggering agent-side DSC run on each newly enrolled machine.

Policy enforcement sequence for Arc brownfield: (1) assign prerequisite extension policy (`deployIfNotExists` for guest config extension), (2) assign audit-mode baseline policies and validate compliance state, (3) switch to `deployIfNotExists` enforcement after validation. Skipping audit mode and going directly to deny-mode enforcement blocks enrollment scripts that rely on specific package installation ordering.

### 3. Arc Extension Deployment Sequence

Extension installation order on Arc servers is architecturally constrained:

1. **AMA (Azure Monitor Agent)** — Establishes the Data Collection Rule association and log ingestion pipeline. Must be first.
2. **MDE (Microsoft Defender for Endpoint)** — Onboards the machine to Defender for Servers P2. Requires AMA workspace registration to correlate endpoint telemetry with MMA/AMA log streams.
3. **Dependency Agent** — Enables service map and VM Insights. Requires AMA running and the `VMInsights` solution enabled on the Log Analytics workspace.
4. **Custom Script Extension (optional)** — Post-enrollment configuration tasks (OS hardening scripts, agent registrations). Run last; does not depend on monitoring stack.

AVM module note: `avm/res/hybrid-compute/machine` exists in the Bicep public registry but is **scope-limited to Arc Resource Bridge for Azure Stack HCI or VMware**, where the Arc Machine resource is created declaratively alongside a `VirtualMachineInstance` extension. The module's own documentation states it "should not be used for other Arc-enabled server scenarios, where the Arc Machine resource is created automatically by the onboarding process." For the general at-scale Arc enrollment patterns covered by this skill (Connected Machine agent install via deployment script, HRW, or DSC), the Arc machine resource is created by the agent itself — no AVM module wraps that flow. Extension resources can still be authored as native `Microsoft.HybridCompute/machines/extensions` blocks, or — once an Arc machine exists — via per-extension AVM modules where available.

### 4. Resource Graph Hybrid Inventory

Once enrolled, Arc machines surface in Resource Graph under `microsoft.hybridcompute/machines`. The Step 0 Assessor extends its existing KQL collectors to include Arc machines alongside native resources, providing a unified hybrid inventory view. Key properties available in Resource Graph: `properties.agentVersion`, `properties.status` (Connected/Disconnected/Expired), `properties.osSku`, `properties.osVersion`, `properties.extensions` (array of installed extensions with provisioning state), and `properties.lastStatusChange` (staleness detection).

## Diagnostic Queries

### KQL: Arc servers missing AMA extension (monitoring gap)

```kusto
Resources
| where type == "microsoft.hybridcompute/machines"
| extend extensions = properties.extensions
| where isnull(extensions)
      or not(extensions has "AzureMonitorWindowsAgent")
          and not(extensions has "AzureMonitorLinuxAgent")
| project name, resourceGroup, subscriptionId,
          osType = tostring(properties.osType),
          agentVersion = tostring(properties.agentVersion),
          status = tostring(properties.status)
| order by resourceGroup asc, name asc
```

Returns Arc machines with no AMA extension installed — primary log ingestion gap in S6 estates.

### KQL: Arc servers not enrolled in Defender for Servers (security coverage gap)

```kusto
SecurityResources
| where type == "microsoft.security/assessments"
| where name == "45cfe080-ceb1-a91e-9743-71b8ca1b7e03"  // Defender for Servers enrollment assessment
| where properties.status.code == "Unhealthy"
| extend machineId = tostring(properties.resourceDetails.Id)
| project machineId, subscriptionId,
          statusCode = tostring(properties.status.code),
          displayName = tostring(properties.displayName)
| order by subscriptionId asc
```

Returns Arc machines assessed as not enrolled in Defender for Servers Plan 2 — triggers remediation in S6 brownfield Step 6.

### KQL: Arc servers with stale agent versions (operational debt)

```kusto
Resources
| where type == "microsoft.hybridcompute/machines"
| extend agentVersion = tostring(properties.agentVersion)
| extend lastStatusChange = todatetime(properties.lastStatusChange)
| where lastStatusChange < ago(30d)
       or isempty(agentVersion)
| project name, resourceGroup, subscriptionId,
          agentVersion, lastStatusChange,
          status = tostring(properties.status),
          osType = tostring(properties.osType)
| order by lastStatusChange asc
```

Returns Arc machines that have not reported status in 30+ days or have no agent version recorded — primary agent drift finding in long-lived hybrid estates.

### KQL: Arc servers without machine configuration policy assignment

```kusto
PolicyResources
| where type == "microsoft.policyinsights/policystates"
| where properties.resourceType =~ "microsoft.hybridcompute/machines"
| where properties.complianceState =~ "NonCompliant"
| summarize NonCompliantCount = count() by
    machineName = tostring(properties.resourceId),
    policyDisplayName = tostring(properties.policyDefinitionName),
    subscriptionId
| order by NonCompliantCount desc, machineName asc
```

Returns Arc machines with non-compliant machine configuration policy assignments — surfaces S6 brownfield compliance gaps before Step 8 enforcement mode switch.

## Prerequisites and Caveats

Before applying this skill to a brownfield S6 estate, verify the following prerequisites. Unmet prerequisites are the primary cause of hard-gate failures that appear architecturally sound but break at execution time.

| Prerequisite | Impact | Guidance |
|--------------|--------|----------|
| Outbound HTTPS (port 443) to Arc endpoint URLs | `azcmagent` cannot register without reaching `management.azure.com`, `login.microsoftonline.com`, and regional Arc endpoints | Use the Azure Arc Network Requirements tool (`aka.ms/AzureArcNetworkRequirements`) to generate the full URL list for the target region before Step 2 |
| `azure-policy` skill — MG-scoped policy assignments in place | Without policy assignments, Arc-enrolled machines deliver zero governance value (vanity Arc anti-pattern) | Confirm `azure-policy` is established and machine config prerequisite extensions are assigned before Step 5 |
| Log Analytics workspace ID and key (for AMA DCR association) | AMA extension requires a DCR resource pointing to the workspace; missing workspace ID causes AMA provisioning failure | Provision Log Analytics workspace via `azure-monitor` skill before brownfield Step 6 extension deployment |
| CMDB export or existing inventory list | At-scale onboarding scripts iterate over a machine list; no CMDB means manual enumeration or resource-by-resource enrollment | Export CMDB data for Step 1 inventory; cross-reference with Resource Graph to identify already-enrolled machines before generating new scripts |
| SOC acknowledgment for Defender coverage gap window | Step 6 MDE extension installation and Step 7 removal both require SOC awareness of temporary coverage gaps | Schedule Steps 6 and 7 with explicit SOC change management approval, per ADR §5 Phase 6 gate |
| `Azure Connected Machine Onboarding` role assigned at appropriate scope | Onboarding credential (MI or SP) without this role causes `azcmagent connect` to fail with authorization error | Assign role before generating scripts in Step 3; confirm scope is subscription or RG level (not root MG) |

## Hidden Assumptions

1. **`azcmagent` requires outbound HTTPS — no inbound connectivity needed.** The Arc agent initiates all connections outbound from the enrolled machine to Azure Arc endpoints. No inbound ports from Azure to the on-premises machine are required. However, proxy servers that perform TLS inspection (SSL bump) break `azcmagent` certificate validation unless the Arc endpoint certificates are added to the proxy's trusted CA list. This is the most common connectivity failure in enterprise on-premises environments with mature network security stacks.

2. **Arc enrollment does NOT create a guest account or computer object in Entra ID.** The `Microsoft.HybridCompute/machines` resource is an ARM projection only — it does not provision a service account, Entra device object, or computer account in Active Directory. Teams expecting Arc enrollment to replace AD domain join for identity purposes are misapplying the tool. Arc provides Azure management-plane governance projection; identity federation for users and workloads on the enrolled machine remains a separate concern (`entra-connect-hybrid-identity`).

3. **Machine configuration (guest config) DSC resources execute as SYSTEM / root.** Policy-driven configuration remediation runs with elevated OS privileges on the enrolled machine. Poorly authored custom machine configuration packages can cause OS instability or security regressions. Validate all custom DSC resources in a non-production environment before assigning policies in `deployIfNotExists` enforcement mode at MG scope. There is no Azure-side sandbox for custom machine configuration execution.

4. **Arc agent auto-upgrade is opt-in, not default.** The `azcmagent` binary and Arc extension agents do not self-update unless `allowExtensionOperations` and the `enableAutoUpgrade` flag on each extension are explicitly set. Without auto-upgrade, long-lived Arc machines accumulate agent version debt that breaks extension API compatibility and telemetry pipeline schemas. Include agent auto-upgrade configuration in the onboarding script and validate via Resource Graph `properties.agentVersion` queries as part of ongoing operational runbooks.

5. **Disconnecting an Arc machine (`azcmagent disconnect`) does not delete the ARM resource object.** The `Microsoft.HybridCompute/machines` resource persists in the resource group after the agent disconnects. The machine appears as `Disconnected` status in Resource Graph and Policy compliance counts it as a non-compliant resource indefinitely. Explicitly delete the ARM resource (`az connectedmachine delete`) after decommissioning or deregistering a machine to prevent phantom resources inflating compliance gap findings in Sentinel reports.

## Anti-Patterns

**Vanity Arc onboarding ("hybrid checkbox").** Connecting servers to Arc without consuming any governance capabilities — no policy assignments, no AMA extension, no Defender enrollment — produces Arc projection with zero enforcement value. The machine appears in compliance dashboards as "covered" but delivers nothing. Every Arc-enrolled resource must have at minimum one active policy assignment and one monitoring extension within 30 days of enrollment. Resources enrolled without consuming governance primitives should be treated as a compliance gap finding and either remediated or decommissioned. This anti-pattern is explicitly documented in the shared ADR §7.

**Credential proliferation via per-resource service principals.** Creating a dedicated service principal per onboarding batch, per business unit, or per server generates a secret management burden that negates Arc's security benefit. A leaked per-server SP enables an attacker to enroll arbitrary machines as Arc resources in the tenant. The MI-first default via Azure Automation Hybrid Runbook Worker (ADR §5) eliminates per-resource credentials entirely. When SP fallback is required, a single SP scoped to the target subscription or resource group is the maximum — never narrower than subscription scope for large estates, never broader than root MG for any estate.

**Policy fragmentation between Arc and native resources.** Assigning different policy sets to Arc-enrolled servers versus native Azure VMs within the same management group creates a bifurcated compliance posture that the Warden and Sentinel cannot evaluate consistently. Arc-enrolled machines inherit MG-scoped policy assignments the same way native resources do. Arc-specific additions (guest configuration, machine config prerequisites) should be additive policy applied in the same initiative as native VM policy — not a parallel initiative that diverges over time. Fragmented policy produces compliance reports showing native VMs at 95% and Arc machines at 40%, obscuring the true hybrid posture and triggering incorrect remediation prioritization.

**Agent drift on long-lived Arc machines.** Arc agent versions (`azcmagent` binary, extension agents) require active version management. Machines enrolled once and never updated accumulate version debt that breaks extension compatibility, causes AMA schema mismatches in Log Analytics, and disables machine configuration policy enforcement when DSC module versions diverge. Update Manager surfaces stale agent alerts for Arc servers via the `assessmentStatus` property; the `properties.agentVersion` Resource Graph field enables KQL queries to identify machines below the minimum supported version. Include agent version compliance in the Sentinel monitoring baseline and the periodic operational runbook.

## Cross-Skill References

| Skill | Relationship |
|-------|-------------|
| [`azure-policy`](../azure-policy/SKILL.md) | **Hard prereq.** Machine configuration (guest config) policy authoring, initiative assignment, `deployIfNotExists` and `auditIfNotExists` effect syntax for Arc-enrolled machines |
| [`azure-monitor`](../azure-monitor/SKILL.md) | **Soft prereq.** Log Analytics workspace provisioning, Data Collection Rule authoring, AMA extension deployment, and alert rule creation for Arc machine telemetry |
| [`azure-defender-for-cloud`](../azure-defender-for-cloud/SKILL.md) | **Soft prereq.** Defender for Servers Plan 2 enrollment at subscription scope, MDE extension auto-provisioning settings, Defender secure score delta tracking |
| [`workload-identity-federation`](../workload-identity-federation/SKILL.md) | W1 soft prereq. Managed identity patterns for Arc machine onboarding automation; service account token projection for workloads running on Arc-enrolled hosts |
| [`azure-arc-kubernetes`](../azure-arc-kubernetes/SKILL.md) | **W5 sibling.** Arc-enabled Kubernetes (connectedClusters, Flux v2 GitOps, constraint templates, OIDC issuer). Kubernetes clusters hosted on the same on-premises infrastructure as Arc servers may enroll for both skills in the S6 scenario. |
| [`azure-virtual-machines`](../azure-virtual-machines/SKILL.md) | W2. Native Azure VM management. Use when the Arc-vs-migrate decision (ADR §4 "Migrate to Azure When" table) favors lift-and-shift over hybrid governance projection. |
| [`entra-connect-hybrid-identity`](../entra-connect-hybrid-identity/SKILL.md) | W1. Hybrid identity for users and on-premises Active Directory. Arc provides ARM management projection; Entra Connect provides Entra identity for user accounts — distinct, non-overlapping surfaces. |
| [`management-group-architecture`](../management-group-architecture/SKILL.md) | W3. MG hierarchy must be established (billing-tenant-hierarchy ADR) before Arc policy scope is assigned — Arc inherits policy at MG scope. S4 (M&A Integration) cross-reference: acquired on-premises servers enroll after MG hierarchy is restructured. |
| [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) | **Shared ADR (Linus-8).** Canonical Arc vs. migrate decision boundary, MI-first credential default, onboarding sequence model, WAF trade-offs, anti-patterns, and scenario mapping (S6/S8/S4). **Read before applying this skill to any workload.** |

## Microsoft Learn References

| Resource | Notes |
|----------|-------|
| [Azure Arc-enabled servers overview](https://learn.microsoft.com/azure/azure-arc/servers/overview) | Connected Machine agent, supported OS matrix, Arc server lifecycle (enrollment, disconnect, decommission) |
| [Connected Machine agent deployment options](https://learn.microsoft.com/azure/azure-arc/servers/deployment-options) | At-scale onboarding options: deployment scripts, Automation HRW, Azure DevOps, service principal and MI credential patterns |
| [Azure Policy machine configuration overview](https://learn.microsoft.com/azure/governance/machine-configuration/overview) | Guest config / machine configuration policy authoring, DSC resource packaging, `deployIfNotExists` enforcement for Arc-enrolled machines |
| [Azure Monitor Agent management](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage) | AMA extension installation via Arc, Data Collection Rule association, workspace migration from legacy MMA agent |
| [Defender for Servers overview](https://learn.microsoft.com/azure/defender-for-cloud/defender-for-servers-introduction) | Plan 1 vs Plan 2 feature comparison, Arc enrollment as mandatory coverage layer for non-Azure hosts, MDE extension deployment |
| [Azure Update Manager for Arc-enabled servers](https://learn.microsoft.com/azure/update-manager/overview) | Patch assessment and scheduled maintenance for Arc machines, integration with Azure Policy for compliance enforcement |
| [Azure Arc-enabled servers security overview](https://learn.microsoft.com/azure/azure-arc/servers/security-overview) | MI-first onboarding best practices, Arc Private Link Scope for endpoint isolation, extension permission model |
| [Azure Arc Private Link Scope for servers](https://learn.microsoft.com/azure/azure-arc/servers/private-link-security) | Private Link Scope configuration for Arc servers — eliminates public management traffic to Arc data-plane endpoints (`guestconfiguration.azure.com`, `his.arc.azure.com`, `dp.kubernetesconfiguration.azure.com`) per Security Baseline Rule 6 |
| [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) | Wave 5 Shared ADR — Arc vs. migrate decision boundary, MI-first credential default (§5), WAF trade-off matrix (§6), anti-patterns (§7), scenario mapping S6/S8/S4 (§8) |
| [`docs/decisions/compute-tier-selection.md`](../../../docs/decisions/compute-tier-selection.md) | W2 ADR — compute tier selection for native Azure; relevant when Arc-vs-migrate decision favors lift to Azure VMs |
| [`docs/decisions/billing-tenant-hierarchy.md`](../../../docs/decisions/billing-tenant-hierarchy.md) | W3 ADR — MG hierarchy must be established before Arc policy scope is assigned (S4/S6 sequencing dependency) |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-19 | Saul | Initial Wave 5 authoring — Arc server onboarding (MI-first via HRW per ADR §5, SP fallback), machine configuration policy baselines, extension deployment sequence (AMA → MDE → Dependency Agent), greenfield day-0 patterns (4 patterns), S6 Hybrid Estate Governance brownfield 8-step playbook (⛔ HARD GATE Steps 3 and 7, Soft rollback Steps 4/5/6/8), pre-HARD-GATE verification checklists, CAF/WAF tables (5/4 rows), Security Baseline Alignment (Rules 4+6), 4 KQL diagnostic queries, 6 prerequisites, 5 hidden assumptions, 4 anti-pattern paragraphs, cross-skill references (8 entries), 8 Microsoft Learn URLs + 3 cross-referenced ADRs in References section. Shared ADR (`docs/decisions/hybrid-onboarding-strategy.md`) cross-referenced in 6 locations (Overview, When to Use, Brownfield intro, Greenfield MI-first pattern, Cross-Skill References, Microsoft Learn References). |
| 2026-05-19 | Coordinator | Isabel-9 surgical edits — heading format (M1 → `## Brownfield Scenario (Scenario S6: ...)`), added Arc Private Link Scope Learn URL (SF-2), corrected AVM module scope disclosure (C2: module is scope-limited to Stack HCI/VMware Arc Resource Bridge, not general Arc enrollment), revision history count corrected (SF-1: 8 Learn URLs + 3 ADRs, not "10 Microsoft Learn URLs"). |

---
name: azure-arc-kubernetes
description: "Azure Arc-enabled Kubernetes for hybrid and multi-cloud cluster governance — connection, GitOps, policy, and extensions. USE FOR: Arc K8s cluster connection (helm-based Arc agent, at-scale onboarding), GitOps with Flux v2 (cluster bootstrap, app delivery, multi-cluster fleet), Azure Policy for Arc K8s (built-in initiatives, constraint templates via OPA Gatekeeper), cluster extensions (Container Insights, Defender for Containers, OIDC issuer), workload identity on Arc K8s (service account token projection), custom locations for Arc-enabled services, and brownfield K8s fleet governance. DO NOT USE FOR: AKS-native cluster architecture (use azure-kubernetes-service), Arc-enabled server management (use azure-arc-servers), Container Apps patterns (use azure-container-apps), Flux v2 on AKS specifically (use azure-kubernetes-service), Entra hybrid identity (use entra-connect-hybrid-identity), or Arc-vs-migrate decision criteria (see docs/decisions/hybrid-onboarding-strategy.md)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-hybrid
  wave: "5"
---

# azure-arc-kubernetes

| Field | Value |
|-------|-------|
| **Skill ID** | `azure-arc-kubernetes` |
| **Domain** | Azure Hybrid — Arc-enabled Kubernetes |
| **Wave** | 5 — Hybrid |
| **Hard Prereqs** | `azure-kubernetes-service` (Flux v2 GitOps reference patterns), `workload-identity-federation` (OIDC issuer / service account token projection) |
| **Soft Prereqs** | `azure-policy` (constraint templates, initiative authoring), `azure-monitor` (Container Insights), `azure-defender-for-cloud` (Defender for Containers) |
| **Shared ADR** | [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) |
| **Primary CAF Area** | Platform Automation & DevOps (primary); Management, Governance (secondary) |
| **Primary WAF Pillar** | Operational Excellence (primary); Security, Reliability (secondary) |
| **Brownfield Scenario** | S8 — Brownfield K8s Fleet |
| **Authored** | Wave 5 · 2026-05-19 · Saul |

Arc-enabled Kubernetes projects any CNCF-conformant cluster — running on on-premises bare metal, VMware, other clouds (EKS, GKE, RKE), or edge devices — into Azure Resource Manager as a `Microsoft.Kubernetes/connectedClusters` object. Once projected, the cluster gains GitOps-driven desired-state management via Flux v2, Azure Policy enforcement via OPA Gatekeeper constraint templates, observability via Container Insights and Defender for Containers, and workload identity federation via the OIDC issuer extension. This skill enables Oracle, Assessor, Warden, and Forge to architect, deploy, and govern Arc-connected Kubernetes fleets at enterprise scale — both for greenfield hybrid buildouts and brownfield fleet governance (S8).

**When to use this skill:** Use when an off-Azure K8s cluster requires GitOps fleet management, Azure Policy constraint enforcement, unified monitoring, or OIDC-based workload identity. Consult [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) before applying this skill to confirm Arc is the correct path versus migrating to AKS.

## Overview

Arc-enabled Kubernetes extends the Azure control plane to any CNCF-conformant cluster without migrating workloads. The Arc agent (deployed as a Helm chart into a dedicated `azure-arc` system namespace) establishes a control-plane connection from the cluster to Azure Resource Manager. This projection enables ARM-native governance: the cluster becomes a `Microsoft.Kubernetes/connectedClusters` resource subject to Azure Policy, visible in Resource Graph, targetable by Defender for Cloud, and manageable via GitOps extensions.

The skill covers six primary surfaces:

1. **Connection:** `az connectedk8s connect` / helm-based agent deployment, proxy configuration, private endpoint path for air-gap environments
2. **GitOps:** Flux v2 extension — cluster bootstrap, kustomization targets, multi-cluster fleet management, app delivery via GitRepository and HelmRelease
3. **Policy:** OPA Gatekeeper constraint templates deployed via Arc extensions; `Kubernetes cluster pod security baseline standards for Linux-based workloads` built-in initiative; audit-before-deny sequencing
4. **Extensions:** Container Insights, Defender for Containers, OIDC issuer (for workload identity), Open Service Mesh, custom locations
5. **Workload Identity:** OIDC issuer extension enables service account token projection compatible with `workload-identity-federation` (W1) patterns — federating Arc cluster service accounts to Azure managed identities without storing credentials
6. **Fleet Governance:** Multi-cluster Policy compliance dashboard, Flux reconciliation status aggregation, Defender fleet posture, Resource Graph inventory queries

**AKS is the hard prerequisite.** The `azure-kubernetes-service` skill (W2) owns Flux v2 concepts, GitOps bootstrap patterns, and workload identity architecture. This skill defers all AKS-native guidance there and focuses on the Arc connectivity layer and the additional complexity it introduces. The `workload-identity-federation` skill (W1) owns OIDC federation mechanics; this skill covers the Arc-specific extension lifecycle and sequencing.

**Arc-vs-migrate decision boundary** is defined in [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) §3–§4. Do not redefine it here — reference it.

## When to Use This Skill

- Connecting an off-Azure K8s cluster (on-premises, EKS, GKE, RKE2, k3s, edge device) to Azure Resource Manager for unified governance
- Designing a Flux v2 GitOps fleet across heterogeneous cluster environments (mixed AKS + Arc-connected clusters)
- Assigning Azure Policy constraint templates (OPA Gatekeeper) to enforce pod security standards on non-AKS clusters
- Enabling OIDC issuer on an Arc-connected cluster so workloads can authenticate to Azure services without storing credentials
- Deploying Container Insights and Defender for Containers to off-Azure clusters via Arc cluster extensions
- Planning at-scale Arc K8s onboarding using MI-first credential pattern (Managed Identity via Azure Automation Hybrid Runbook Worker — see ADR §5)
- Governing a brownfield K8s fleet (S8) spanning multiple environments under a single Azure Policy + Monitor surface
- Configuring custom locations to deploy Arc-enabled data services or app services onto Arc-connected infrastructure

## When NOT to Use This Skill

- **AKS-native cluster architecture** (CNI modes, node pools, private cluster, AKS-specific extensions) → `azure-kubernetes-service`
- **Flux v2 GitOps on AKS** (AKS GitOps extension, AKS-specific bootstrap patterns) → `azure-kubernetes-service`
- **Arc-enabled server management** (azcmagent, guest config, AMA on servers, Defender for Servers P2) → `azure-arc-servers`
- **Container Apps serverless patterns** (KEDA-native HTTP scaling, Dapr building blocks) → `azure-container-apps`
- **Entra hybrid identity / AD Connect sync** → `entra-connect-hybrid-identity`
- **Workload identity federation mechanics** (FIC lifecycle, AKS OIDC, cross-cloud FIC) → `workload-identity-federation`
- **Azure Policy constraint template syntax authoring** → `azure-policy`
- **Azure Monitor workbook design and alert rules** → `azure-monitor`
- **Arc-vs-migrate decision** (when to use Arc K8s vs. migrating to AKS) → [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md)
- **Arc data services** (SQL Managed Instance on Arc, PostgreSQL on Arc) → out of scope; skill catalog final at 14

## CAF Design Area Mapping

| CAF Design Area | Coverage | Primary |
|-----------------|----------|---------|
| Platform Automation & DevOps | Flux v2 GitOps provides declarative desired-state management across the full hybrid fleet. Arc connectivity layer enables cluster bootstrap from git with the same patterns the AKS skill establishes for cloud-native clusters. Multi-cluster fleet management — kustomization targets, HelmRelease delivery, reconciliation status — is a first-class Platform Automation concern. | ✅ |
| Management | Container Insights (via Arc extension) extends Log Analytics observability to off-Azure clusters. Flux reconciliation logs feed Azure Monitor. Resource Graph inventory queries surface `Microsoft.Kubernetes/connectedClusters` alongside native resources. Extension version state is exposed in the cluster's ARM resource object and must be tracked in the operational runbook. | ✅ |
| Governance | OPA Gatekeeper constraint templates deployed via Azure Policy enforce pod security standards on Arc-connected clusters — the same governance posture applied to AKS extends to all CNCF-conformant off-Azure clusters. Arc-enrolled clusters inherit management-group–scoped policy assignments identically to native resources. | ✅ |
| Security | Defender for Containers (Arc extension) and OIDC issuer (workload identity) bring Azure security controls to off-Azure clusters. Constraint templates enforce pod security baseline and custom admission controls. OIDC issuer enablement is a ⛔ HARD GATE — see Brownfield Playbook Step 7. | |
| Identity & Access | OIDC issuer extension enables service account token projection compatible with `workload-identity-federation` (W1) — federating Arc cluster workloads to Azure managed identities. MI-first onboarding credential default per ADR §5 removes per-cluster service principal secrets. | |
| Network Topology & Connectivity | TCP 443 outbound to Arc endpoints is a hard prerequisite. Private endpoint path (Azure Arc Private Link Scope) is the production pattern for clusters that cannot route outbound directly. ExpressRoute or VPN baseline assumed — not owned by this skill. | |

## WAF Pillar Coverage

| WAF Pillar | Coverage | Primary |
|------------|----------|---------|
| Operational Excellence | Flux v2 GitOps makes desired state authoritative across the fleet — drift is detectable and correctable because cluster configuration lives in git. Multi-cluster reconciliation status aggregation via Azure Monitor. Extension lifecycle (install, upgrade, remove) managed declaratively. Agent version hygiene tracked via Resource Graph. | ✅ |
| Security | Defender for Containers threat detection on Arc clusters. OPA Gatekeeper constraint templates block non-compliant pod specs at admission. OIDC issuer eliminates in-cluster secrets for Azure service auth. MI-first onboarding credential (ADR §5) removes per-cluster SP secret risk. OIDC issuer enablement ⛔ HARD GATE — irrevocable change requires pre-mutation workload team validation. | ✅ |
| Reliability | Flux v2 reconciliation continuously enforces desired state — configuration drift is corrected without manual intervention. Cluster availability is customer-managed (no Azure SLA on the underlying infrastructure); Arc control-plane carries 99.9% SLA for the projection layer only. Policy constraint templates prevent non-compliant workloads from deploying in the first place. | ✅ |
| Cost Optimization | Arc control plane and extensions are free for cluster connectivity. Container Insights and Defender for Containers are billed per cluster node — scope to participating namespaces to control telemetry cost. On-premises cluster infrastructure cost remains with the customer; re-platform TCO analysis (per ADR §4) may reveal migration as cheaper than ongoing Arc operations overhead. | |
| Performance Efficiency | Arc is control-plane only — no impact on workload data path. GitOps pull-based reconciliation is asynchronous and out-of-band. Cluster networking and compute performance are determined by the underlying on-premises or off-cloud infrastructure. | |

## Greenfield Patterns

For new clusters being built alongside a new landing zone, connect to Arc immediately after cluster installation — before any workloads deploy. This ensures GitOps and Policy are authoritative from day 0 rather than retrofitted later.

### Greenfield Connection Sequence

1. **Provision Arc resource group and Log Analytics workspace** — tag with CAF required tags (`Environment`, `Owner`, `CostCenter`, `Project`, `ManagedBy`). Create the workspace first; Container Insights extension requires a target workspace at extension install time.

2. **Establish connectivity prerequisites** — confirm outbound TCP 443 from cluster nodes to Arc endpoints. For production clusters that must not route outbound, configure [Azure Arc Private Link Scope](https://learn.microsoft.com/azure/azure-arc/kubernetes/private-link) before connecting.

3. **Establish onboarding credential (MI-first)** — use Managed Identity via Azure Automation Hybrid Runbook Worker as the default onboarding credential. See [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) §5 for the canonical credential pattern. Service principal with cluster-admin equivalent is the fallback only when MI is unavailable.

4. **Connect the cluster:**

   ```bash
   az connectedk8s connect \
     --name <cluster-name> \
     --resource-group <rg-name> \
     --location <region> \
     --tags Environment=prod CostCenter=<cc> Project=<proj> ManagedBy=arc
   ```

5. **Enable Flux v2 GitOps extension** — configure source (GitRepository) and kustomization targets. Mirror AKS GitOps bootstrap patterns from the `azure-kubernetes-service` skill; the Flux v2 extension is the same across AKS and Arc K8s.

   ```bash
   az k8s-extension create \
     --name flux \
     --extension-type microsoft.flux \
     --cluster-type connectedClusters \
     --cluster-name <cluster-name> \
     --resource-group <rg-name> \
     --scope cluster
   ```

6. **Assign Azure Policy initiative** — apply `Kubernetes cluster pod security baseline standards for Linux-based workloads` (built-in) at management group scope. Set effect to `audit` first; switch to `deny` only after compliance baseline is established.

7. **Deploy monitoring and security extensions** — in order: Container Insights → Defender for Containers → OIDC issuer (if workload identity is required). See Extension Sequencing below.

8. **Validate posture** — Resource Graph query for `Microsoft.Kubernetes/connectedClusters` compliance state; Defender for Containers alert baseline; Flux reconciliation status per kustomization.

### Extension Sequencing

Always deploy extensions in this order to avoid dependency failures:

| Order | Extension | Purpose | Billing |
|-------|-----------|---------|---------|
| 1 | `microsoft.azuremonitor.containers` | Container Insights — telemetry pipeline before any other extension | Per node (Log Analytics) |
| 2 | `microsoft.azuredefender.kubernetes` | Defender for Containers threat detection | Per node (Defender plan) |
| 3 | `microsoft.azure.connectedk8s.oidcissuer` | OIDC issuer for workload identity — deploy last; see HARD GATE | Free (extension) |

### AVM Module Reference

No Azure Verified Module for `Microsoft.Kubernetes/connectedClusters` exists at time of Wave 5 authoring. Use native Bicep `resource` blocks or Terraform `azurerm_arc_kubernetes_cluster` resource. Track [AVM module registry](https://aka.ms/avm) for future availability.

**Bicep (native resource block):**

```bicep
resource arcCluster 'Microsoft.Kubernetes/connectedClusters@2024-01-01' = {
  name: clusterName
  location: location
  identity: {
    type: 'SystemAssigned'           // Security Baseline Rule #4
  }
  properties: {
    agentPublicKeyCertificate: ''    // populated by az connectedk8s connect
  }
  tags: tags
}
```

**Terraform:**

```hcl
resource "azurerm_arc_kubernetes_cluster" "this" {
  name                = var.cluster_name
  resource_group_name = var.resource_group_name
  location            = var.location
  agent_public_key_certificate = var.agent_public_key_certificate

  identity {
    type = "SystemAssigned"          # Security Baseline Rule #4
  }

  tags = var.tags
}
```

## Brownfield Scenario (Scenario S8: Brownfield K8s Fleet)

**Scenario S8** covers existing heterogeneous Kubernetes fleets — on-premises clusters, EKS/GKE/RKE running off-Azure, and edge clusters — that require unified GitOps, Policy, and Monitor governance under an existing Azure Landing Zone. This scenario is the primary brownfield use case for Arc-enabled Kubernetes per [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) §8.

**Prerequisite skills:** Run `management-group-architecture` (W3) first to ensure the target MG scope is established before assigning Arc policy. Run `azure-kubernetes-service` (W2) to understand Flux v2 reference patterns before bootstrapping GitOps on Arc clusters.

The brownfield playbook follows the six-phase sequence from the shared ADR (§5 Onboarding Sequence Model). All irreversible mutations are annotated with ⛔ HARD GATE.

---

### Step 1 — Inventory Existing Clusters

Query Resource Graph for already-enrolled clusters and cross-reference against the cluster CMDB to identify the full enrollment scope:

```kusto
resources
| where type == "microsoft.kubernetes/connectedclusters"
| project name, location, resourceGroup, properties.connectivityStatus,
           properties.distribution, properties.kubernetesVersion,
           properties.agentVersion
| order by name asc
```

Produce a cluster inventory table: name, distribution, Kubernetes version, Arc agent version, connectivity status, and enrollment date. Identify clusters that are present in the CMDB but absent from Resource Graph — these are the unenrolled targets.

*Soft rollback: inventory step is read-only; no cluster state is modified.*

---

### Step 2 — Validate Connectivity and RBAC Prerequisites

For each target cluster:

- Confirm outbound TCP 443 from cluster nodes to Arc service endpoints (`management.azure.com`, `*.dp.kubernetesconfiguration.azure.com`, `*.arc.azure.com`). See [network requirements](https://learn.microsoft.com/azure/azure-arc/kubernetes/network-requirements).
- Confirm cluster-admin or equivalent RBAC for the connecting service principal or MI.
- Confirm Kubernetes version is within [Arc-supported range](https://learn.microsoft.com/azure/azure-arc/kubernetes/overview#supported-kubernetes-versions). Clusters outside the supported range must be upgraded before connection.
- If the cluster routes through a proxy, capture the `--proxy-http`, `--proxy-https`, and `--proxy-skip-range` values for the connection command.

*Soft rollback: validation step is read-only.*

---

### Step 3 — ⛔ HARD GATE: Arc Agent Helm Install Mutates the Cluster

> **This step modifies cluster state. Validate in a non-production cluster first.**

Running `az connectedk8s connect` deploys the Arc agent as a Helm chart into a new system namespace (`azure-arc`) and modifies the cluster's DNS configuration. This is a **pre-mutation gate**. Before proceeding:

**Pre-mutation checklist:**
- [ ] Non-production cluster connection tested and agent health confirmed (`az connectedk8s show`)
- [ ] `azure-arc` namespace does not already exist with conflicting resources
- [ ] DNS modification impact assessed for clusters with custom CoreDNS configurations
- [ ] Change management approval obtained for production clusters
- [ ] Workload owner notification sent (DNS changes can affect service resolution timing)

**Rollback path:**

Disconnecting requires explicit steps — this is **only partially automated**:

```bash
# Step 1: Disconnect via CLI (removes Azure resource object)
az connectedk8s delete --name <cluster-name> --resource-group <rg-name>

# Step 2: Manual namespace cleanup on the cluster (NOT automated by CLI)
kubectl delete namespace azure-arc
# If Flux extension was installed:
kubectl delete namespace flux-system
# Remove any CRDs installed by Arc extensions
kubectl get crds | grep azure | awk '{print $1}' | xargs kubectl delete crd
```

> The `az connectedk8s delete` command removes the ARM resource object but does **not** fully clean the in-cluster state. Manual namespace and CRD removal is required. CRD removal may fail if custom resources exist — each must be deleted before the CRD itself.

*If rollback is required in production, coordinate with all workload teams before deleting namespaces or CRDs.*

---

### Step 4 — Enable Flux v2 GitOps Extension

Configure the Flux v2 extension and define kustomization targets. Mirror the AKS GitOps bootstrap patterns from the `azure-kubernetes-service` skill — the Flux v2 extension is architecturally identical across AKS and Arc K8s.

```bash
az k8s-extension create \
  --name flux \
  --extension-type microsoft.flux \
  --cluster-type connectedClusters \
  --cluster-name <cluster-name> \
  --resource-group <rg-name> \
  --scope cluster \
  --configuration-settings multiTenancy.enforce=true
```

Define cluster-level vs namespace-level Flux resources based on trust boundary:
- **Cluster-level kustomizations:** platform infrastructure (RBAC, network policies, baseline policies)
- **Namespace-level kustomizations:** application workloads (teams manage their own HelmReleases)

*Soft rollback: Flux extension can be removed with `az k8s-extension delete` and namespace cleanup.*

---

### Step 5 — Assign Azure Policy Initiative

Assign the `Kubernetes cluster pod security baseline standards for Linux-based workloads` built-in initiative at management group scope so all enrolled clusters inherit the assignment:

```bash
az policy assignment create \
  --name "arc-k8s-pod-security-baseline" \
  --policy-set-definition "a8640138-9b0a-4a28-b8cb-1666c838647d" \
  --scope "/providers/Microsoft.Management/managementGroups/<mg-id>" \
  --enforcement-mode DoNotEnforce   # audit first
```

Validate compliance state via Policy compliance dashboard before switching enforcement mode to `Default` (deny). Custom constraint templates (OPA Gatekeeper) build on the `azure-policy` skill — reference it for authoring syntax.

*Soft rollback: policy assignment deletion removes enforcement; no cluster state is mutated by policy assignment alone.*

---

### Step 6 — Deploy Monitoring and Defender Extensions

Deploy in order: Container Insights first (telemetry pipeline), then Defender for Containers.

```bash
# Container Insights
az k8s-extension create \
  --name azuremonitor-containers \
  --extension-type microsoft.azuremonitor.containers \
  --cluster-type connectedClusters \
  --cluster-name <cluster-name> \
  --resource-group <rg-name> \
  --configuration-settings logAnalyticsWorkspaceResourceID=<workspace-id>

# Defender for Containers
az k8s-extension create \
  --name microsoft-defender \
  --extension-type microsoft.azuredefender.kubernetes \
  --cluster-type connectedClusters \
  --cluster-name <cluster-name> \
  --resource-group <rg-name>
```

> **Extension removal warning:** Removing the Defender for Containers extension from a production cluster immediately drops Defender threat detection coverage for that cluster. Coordinate with the SOC before removing Defender extensions in production environments. This applies to Arc K8s identically to the Arc servers pattern.

*Soft rollback: extensions can be removed (`az k8s-extension delete`) but Defender coverage gap is immediate upon removal.*

---

### Step 7 — ⛔ HARD GATE: OIDC Issuer Enablement Is Irrevocable

> **This is the highest-risk mutation in Wave 5. Enable only after workload team validation.**

The OIDC issuer extension changes the token audience configuration for the cluster's service account token projection. Once enabled, existing workloads that rely on the default service account token audience may break if they have not been updated to use the projected token format.

**Pre-mutation checklist:**
- [ ] All workload teams notified of the OIDC audience change
- [ ] All service account–to–Azure bindings audited (identify workloads using legacy SP secrets that will not benefit from OIDC and may be disrupted)
- [ ] Non-production cluster OIDC issuer tested with representative workloads
- [ ] Federated identity credentials pre-created in target managed identities (reference `workload-identity-federation` skill W1 for FIC lifecycle)
- [ ] Rollback plan documented (see below) and reviewed by workload owners

**Enable OIDC issuer:**

```bash
az connectedk8s update \
  --name <cluster-name> \
  --resource-group <rg-name> \
  --enable-oidc-issuer
```

**Rollback path — only partially automated:**

The OIDC issuer configuration change in the cluster is **irrevocable via a simple toggle**. The `az connectedk8s update --disable-oidc-issuer` CLI option does not exist at Wave 5 authoring time. Rollback requires:

1. Disconnect the cluster (`az connectedk8s delete`) — removes ARM resource object
2. Manually clean `azure-arc` namespace and OIDC-related CRDs from the cluster
3. Reconnect the cluster without OIDC issuer — treating this as a fresh enrollment
4. Restore all Flux configurations, policy assignments, and extensions
5. Re-validate all workloads that consumed the OIDC issuer

> This rollback is equivalent to a full re-enrollment of the cluster. At production scale, re-enrollment may take hours and requires coordinating all dependent workloads. The FIC-bound managed identities in Azure are unaffected (they can be reused) but all service account token projections in-cluster must be revalidated.

*If workload identity is not required in the current sprint, defer OIDC issuer enablement. It can be added later — but cannot be rolled back cleanly.*

---

### Step 8 — Validate Fleet Posture

```kusto
// Compliance state per connected cluster
policyresources
| where type == "microsoft.policyinsights/policystates"
| where resourceType == "microsoft.kubernetes/connectedclusters"
| summarize compliant=countif(properties.complianceState == "Compliant"),
             noncompliant=countif(properties.complianceState == "NonCompliant")
  by resourceId, policyAssignmentName
| order by noncompliant desc
```

Validate:
- Policy compliance dashboard: all clusters assigned to the baseline initiative
- Defender for Containers: alert baseline established, no critical findings unacknowledged
- Flux reconciliation: `kubectl get kustomizations -A` shows `Ready=True` for all targets
- Container Insights: cluster metrics flowing to Log Analytics workspace
- Resource Graph: `connectivityStatus == "Connected"` for all enrolled clusters

*All validation queries are read-only; no cluster state is modified.*

---

## Security Baseline Alignment

| Rule | Arc K8s Surface | Enforcement |
|------|-----------------|-------------|
| 1. TLS 1.2 minimum | Arc agent communication to Azure endpoints is TLS 1.2+ by default; no configuration required | Automatic via Arc agent |
| 2. HTTPS-only traffic | Arc control-plane communication is HTTPS-only; workload ingress TLS is cluster-owned | Arc: automatic; workloads: Gatekeeper constraint template |
| 3. No public blob access | Not directly applicable to Arc K8s control plane; applies to any storage extensions | Inherited from `azure-storage-accounts` baseline |
| 4. Managed Identity preferred | MI-first onboarding credential via Azure Automation Hybrid Runbook Worker (ADR §5); OIDC issuer for workload identity eliminates in-cluster secrets | ⛔ HARD GATE Step 3 enforces MI-first; Step 7 enables OIDC |
| 5. Azure AD-only SQL auth | Not directly applicable to Arc K8s; applies to any SQL workloads running on the cluster | Inherited from `azure-sql-database` baseline |
| 6. Public network disabled (prod) | Use Azure Arc Private Link Scope to route Arc control-plane traffic through private endpoints; disable direct outbound Arc connectivity in production | Arc Private Link Scope configuration at connection time |

## Cross-Skill References

| Skill | Relationship | Reference Point |
|-------|-------------|----------------|
| [`azure-kubernetes-service`](../azure-kubernetes-service/SKILL.md) | **Hard Prereq** — AKS owns Flux v2 concepts, GitOps bootstrap, workload identity architecture. Arc K8s defers all AKS-native patterns there. | Greenfield Step 5, Brownfield Step 4 |
| [`workload-identity-federation`](../workload-identity-federation/SKILL.md) | **Hard Prereq** — WIF owns OIDC federation mechanics, FIC lifecycle, managed identity selection. Arc K8s provides the OIDC issuer extension; WIF provides the federation pattern. | Brownfield Step 7, Security Baseline Rule 4 |
| [`azure-arc-servers`](../azure-arc-servers/SKILL.md) | **W5 sibling** — Arc servers governs the on-premises VMs hosting cluster nodes (host-level Defender for Servers P2, guest config baselines). Shared ADR establishes the boundary. | S8 supporting role (node VM governance) |
| [`azure-policy`](../azure-policy/SKILL.md) | **Soft Prereq** — Policy owns constraint template syntax authoring and initiative design. Arc K8s consumes policy assignments; it does not redefine policy authoring. | Brownfield Step 5, Greenfield Step 6 |
| [`azure-monitor`](../azure-monitor/SKILL.md) | **Soft Prereq** — Monitor owns workspace design, alert rules, and workbook authoring. Arc K8s deploys Container Insights as an extension; Monitor skill governs the workspace it writes to. | Extension Sequencing, Brownfield Step 6 |
| [`management-group-architecture`](../management-group-architecture/SKILL.md) | **Sequencing dependency** — MG hierarchy must be established before Arc policy scope is assigned. See ADR §8 (S4 sequencing). | Brownfield prerequisite |
| [`docs/decisions/hybrid-onboarding-strategy.md`](../../../docs/decisions/hybrid-onboarding-strategy.md) | **Shared ADR** — Arc-vs-migrate decision criteria, MI-first credential default, onboarding sequence model, WAF trade-offs, and anti-patterns. Canonical authority for all W5 boundaries. | Overview, When to Use, Brownfield intro, Security Baseline Rule 4 |

## Anti-Patterns

**Vanity Arc onboarding ("hybrid checkbox").** Connecting clusters to Arc without consuming any governance capabilities — no policy assignments, no monitoring extensions, no Defender enrollment — produces Arc projection with zero enforcement value. The cluster appears in compliance dashboards as covered but delivers nothing. Every Arc-enrolled cluster should have at minimum the pod security baseline initiative assigned and Container Insights deployed within 30 days of enrollment. See ADR §7 for the full anti-pattern catalog.

**Credential proliferation via per-cluster service principals.** Creating a dedicated SP per cluster or per onboarding batch generates a secret management burden that negates Arc's security benefit. The MI-first default via Azure Automation Hybrid Runbook Worker eliminates per-cluster credentials. When SP fallback is required, a single SP scoped to the target resource group is the maximum — never per-cluster SPs. Reference ADR §5.

**Policy fragmentation between Arc-connected and native clusters.** Assigning different policy initiatives to Arc-connected clusters versus AKS clusters within the same management group creates a bifurcated compliance posture. Arc-enrolled clusters inherit MG-scoped policy assignments identically to native resources. Arc-specific additions (Gatekeeper constraint templates) should be additive policy, not substitutive.

**OIDC issuer enabled without workload team coordination.** Enabling the OIDC issuer extension without notifying workload teams that service account token audiences are changing can break existing workloads silently. Always run the pre-mutation checklist at Brownfield Step 7 and test on non-production clusters first. See ADR §7 (OIDC issuer HARD GATE callout).

**Agent drift on long-lived Arc clusters.** Arc K8s Helm chart versions accumulate version debt if not actively managed. The Arc operator exposes extension version states in the cluster's ARM resource object — include agent version checks in the Sentinel monitoring baseline and operational runbook.

## Microsoft Learn References

| Resource | URL |
|----------|-----|
| Azure Arc-enabled Kubernetes overview | <https://learn.microsoft.com/azure/azure-arc/kubernetes/overview> |
| Supported Kubernetes distributions | <https://learn.microsoft.com/azure/azure-arc/kubernetes/overview#supported-kubernetes-versions> |
| Connect a cluster to Azure Arc | <https://learn.microsoft.com/azure/azure-arc/kubernetes/quickstart-connect-cluster> |
| Network requirements for Arc-enabled Kubernetes | <https://learn.microsoft.com/azure/azure-arc/kubernetes/network-requirements> |
| Azure Arc Private Link Scope (private connectivity) | <https://learn.microsoft.com/azure/azure-arc/kubernetes/private-link> |
| Flux v2 GitOps on Arc-enabled Kubernetes | <https://learn.microsoft.com/azure/azure-arc/kubernetes/conceptual-gitops-flux2> |
| Azure Policy for Arc-enabled Kubernetes | <https://learn.microsoft.com/azure/azure-arc/kubernetes/policy-extension> |
| OPA Gatekeeper constraint templates on Arc | <https://learn.microsoft.com/azure/governance/policy/concepts/policy-for-kubernetes> |
| Cluster extensions overview | <https://learn.microsoft.com/azure/azure-arc/kubernetes/conceptual-extensions> |
| Container Insights for Arc-enabled clusters | <https://learn.microsoft.com/azure/azure-monitor/containers/container-insights-enable-arc-enabled-clusters> |
| Defender for Containers on Arc-enabled Kubernetes | <https://learn.microsoft.com/azure/defender-for-cloud/defender-for-containers-enable?tabs=aks-deploy-portal%2Ck8s-deploy-cli%2Ck8s-verify-cli%2Ck8s-remove-arc&pivots=defender-for-container-arc> |
| Workload identity on Arc-enabled Kubernetes (OIDC issuer) | <https://learn.microsoft.com/azure/azure-arc/kubernetes/workload-identity> |
| Custom locations on Arc-enabled Kubernetes | <https://learn.microsoft.com/azure/azure-arc/kubernetes/custom-locations> |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-19 | Saul-13 | v1.0 — Initial publication (Wave 5). Brownfield S8 playbook with 2 ⛔ HARD GATE annotations. References Linus-8 ADR as canonical authority for Arc-vs-migrate, MI-first credential default, and OIDC issuer irrevocability. |

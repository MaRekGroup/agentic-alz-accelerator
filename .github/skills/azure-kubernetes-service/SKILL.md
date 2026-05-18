---
name: azure-kubernetes-service
description: "AKS cluster architecture, node pool design, workload identity, networking modes, and GitOps patterns for Azure Landing Zones. USE FOR: CNI mode selection (kubenet/Azure CNI/CNI Overlay/CNI Powered by Cilium), node pool topology (system/user/GPU/spot), workload identity integration, pod security standards (PSA/PSS), network policy (Azure/Calico/Cilium), ingress architecture (AGIC/nginx/Contour), service mesh (Istio/OSM), autoscaling (HPA/VPA/KEDA/cluster autoscaler), private cluster patterns, AKS backup/DR, GitOps (Flux v2), and AKS landing zone accelerator alignment. DO NOT USE FOR: general networking topology (use azure-virtual-network), AKS egress firewall rules (use azure-firewall), workload identity federation setup (use workload-identity-federation), container registry security (future: azure-container-registry), Arc-enabled K8s on-premises (future: azure-arc-kubernetes), Container Apps serverless patterns (use azure-container-apps), or VM-host concerns (use azure-virtual-machines)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-compute
  wave: "2"
---

# Azure Kubernetes Service Skill

## Overview

This skill covers the architectural decisions that turn an empty AKS cluster into a production-ready, policy-compliant, and operationally sustainable Kubernetes platform inside an Azure Landing Zone. It addresses the choices that matter most at enterprise scale: which CNI mode to select and why, how to separate system and workload node pools, how to integrate workload identity without deprecated pod-identity machinery, and how GitOps keeps declarative state authoritative over manual operations.

AKS is the broadest API surface in the Wave 2 compute tier. The cluster configuration decisions made here cascade into networking, security, identity, and operational posture choices — treating AKS as "just a place to run containers" is the primary source of architecture debt in enterprise Kubernetes estates. Use this skill to give Oracle, Forge, Strategist, and Assessor the depth they need to make those decisions correctly from the start, or to audit and remediate existing clusters that accumulated debt under simpler assumptions.

> **Compute tier boundary:** For the AKS-vs-Container-Apps-vs-VMs decision, consult `docs/decisions/compute-tier-selection.md`. This skill goes deep on AKS internals; it does not redefine the tier selection criteria.

## Boundary

### USE FOR

- AKS cluster architecture: CNI mode selection (kubenet, Azure CNI, Azure CNI Overlay, Azure CNI Powered by Cilium)
- Node pool topology: system node pools, user node pools, GPU node pools (NC/ND/H100 series), spot node pools
- Workload identity integration with Microsoft Entra ID (OIDC issuer, service account token projection, federated identity credentials)
- Pod security standards (PSA enforce/warn/audit) and pod security admission controller configuration
- Network policy enforcement: Azure Network Policy, Calico, Cilium
- Ingress architecture: AGIC (Application Gateway Ingress Controller), nginx ingress, Contour, TLS termination patterns
- Service mesh: Istio add-on, Open Service Mesh (OSM), mTLS, traffic management
- Autoscaling: HPA (Horizontal Pod Autoscaler), VPA (Vertical Pod Autoscaler), KEDA (event-driven), cluster autoscaler, node auto-provision (NAP)
- Private cluster patterns: private API server, private endpoint integration, DNS integration with private zones
- AKS backup with Azure Backup for AKS and cross-region DR topology
- GitOps with Flux v2 (AKS GitOps extension), cluster bootstrap, multi-cluster fleet management
- AKS landing zone accelerator alignment and AKS baseline reference architecture

### DO NOT USE FOR

- General hub-spoke networking topology → `azure-virtual-network`
- NSGs, UDRs, route table design → `azure-virtual-network`
- AKS egress firewall rules and FQDN allowlists → `azure-firewall`
- Workload identity federation setup, federated identity credential lifecycle → `workload-identity-federation`
- Container registry security, image signing, Notary v2 → future `azure-container-registry`
- Arc-enabled Kubernetes for on-premises or edge clusters → future `azure-arc-kubernetes`
- Serverless container workloads, KEDA-native HTTP scaling, Dapr building blocks → `azure-container-apps`
- VM OS patching, Dedicated Host, BYOL licensing → `azure-virtual-machines`
- GitHub Actions OIDC deployment identity → `entra-app-registration`

## CAF Design Area Alignment

| CAF Design Area | Priority | AKS contribution |
|-----------------|----------|-----------------|
| **Network Topology & Connectivity** | **Primary** | CNI mode determines IP address consumption, subnet sizing, and private endpoint integration. AKS private cluster requires private DNS zone delegation and custom DNS resolver alignment. Ingress controller placement (inside vs. outside subnet) affects east-west and north-south routing topology. Cannot deliver network-compliant AKS without this design area resolved first. |
| **Platform Automation & DevOps** | **Primary** | GitOps via Flux v2 is the authoritative state mechanism — cluster bootstrap, namespace scaffolding, RBAC manifests, and workload deployment all flow through git rather than imperative kubectl. Pipeline integration (cluster credentials via workload identity, not stored secrets) is a Platform Automation & DevOps concern. |
| **Security** | **Primary** | Pod Security Admission enforcement, network policy between namespaces, Key Vault CSI secrets driver, image integrity via Azure Policy, Defender for Containers runtime protection, and private cluster (Security Baseline rule #6) are all security design area decisions with direct AKS surface. |
| **Identity & Access** | **Primary** | Microsoft Entra ID integration for Kubernetes RBAC, workload identity federation for pod-to-Azure auth (references `workload-identity-federation`), and role bindings for Azure-to-K8s identity are Identity & Access design area decisions that AKS must satisfy before workloads can reach any Azure service securely. |
| Resource Organization | Secondary | Node pool tagging, namespace-to-subscription boundary design, and multi-cluster fleet naming conventions feed the resource organization model. |
| Management | Secondary | Container Insights, Azure Monitor managed Prometheus, Grafana dashboards, and diagnostic settings are management design area outputs that AKS diagnostic configuration enables. |

## WAF Pillar Mapping

| WAF Pillar | Priority | AKS contribution |
|------------|----------|-----------------|
| **Reliability** | **Primary** | Zone-redundant node pools spread pods and nodes across availability zones, eliminating single-AZ failure as a cluster-wide outage. Pod Disruption Budgets (PDBs) prevent unsafe evictions during voluntary disruptions (upgrades, node drain). Multi-cluster DR topology with AKS backup and cross-region restore defines Recovery Time Objective. Cannot deliver reliable containerized workloads without these configurations explicit. |
| **Performance Efficiency** | **Primary** | HPA and cluster autoscaler work together to match pod count and node count to actual demand. KEDA extends scaling to non-CPU signals (queue depth, Cosmos RU consumption, custom metrics). GPU node pools with taint-based scheduling ensure inference workloads land on correct hardware without contaminating CPU-only pools. Node Auto-Provision selects SKUs dynamically. |
| **Security** | **Primary** | Private API server endpoint (Security Baseline rule #6), pod network isolation via network policy, workload identity eliminating in-cluster secrets, PSA enforce mode blocking privileged containers, and Defender for Containers runtime threat detection are the AKS security pillars. Each is a distinct configuration decision; none is automatic. |
| **Operational Excellence** | **Primary** | Declarative GitOps (Flux v2) is the operational excellence anchor — drift is detectable and correctable because desired state lives in git, not in operator memory. Upgrade cadence discipline (AKS LTS channel, node image auto-upgrade) and Container Insights alerting close the operational loop. |
| Cost Optimization | Secondary | Spot node pools for fault-tolerant workloads (batch jobs, ML training) reduce compute spend. Right-sizing via VPA recommendations and node pool SKU selection eliminates chronic over-provisioning that afflicts static-size clusters. |

## Scenarios Unblocked

- **S2 (Multi-Region AI Platform):** Cannot deliver model hosting on GPU node pools or inference autoscaling (KEDA + custom GPU metrics) without AKS cluster architecture depth. GPU node pool taint design, proximity placement groups for GPU-to-CPU locality, and multi-cluster federation for regional failover are all AKS-owned concerns.
- **S3 (Regulated Workloads):** Cannot architect compliant AKS without this skill — regulation mandates workload isolation via namespace-scoped network policy, PSA enforce mode, private API endpoint, and pod sandboxing (Kata Containers, preview). Assessor classifies existing AKS clusters against these requirements.
- **S5 (ISV Multi-Tenant SaaS):** Cannot design deployment stamps or per-tenant compute isolation without AKS multi-tenancy patterns — namespace isolation, RBAC boundaries, network policy per-tenant egress, and node pool tainting for noisy-neighbor prevention.
- **S7 (Hybrid Edge):** Cannot architect Azure Arc-connected edge clusters without understanding AKS primitives they extend. GitOps (Flux v2) that runs at edge clusters is the same extension pattern used in cloud AKS — AKS depth is the prerequisite before Arc-K8s depth.
- **S8 (Cloud-Native Modernization):** Cannot deliver "containerize and deploy" without AKS cluster design. This is the cloud-native compute platform for enterprise containerization. Networking mode selection, workload identity integration, and GitOps bootstrap are the three blockers for modernization projects.

## Architecture Patterns

### 1. CNI Mode Selection

| CNI mode | When to use | Key constraint | Migration path |
|----------|-------------|----------------|----------------|
| **Azure CNI Overlay** _(default for new clusters)_ | New clusters, all scenarios where pod IP subnet exhaustion is a concern | Pod IPs come from an overlay address space — no VNet IP consumption per pod | N/A — start here |
| **Azure CNI Powered by Cilium** | Clusters requiring eBPF-based network policy, Hubble observability, or DSR load balancing | Requires Cilium-compatible kernel; no Azure NPM coexistence | Upgrade from Azure CNI to Cilium CNI requires node pool recreation |
| **Azure CNI (node-subnet)** | Legacy clusters pre-dating Overlay GA, or workloads needing pod IPs routable from on-premises | IP exhaustion risk: every pod consumes a VNet IP — plan subnet size as `(max_nodes × max_pods_per_node) + buffer` | Migrate to Overlay via node pool blue-green replacement |
| **Kubenet** | **Avoid for new clusters.** Legacy only — no Windows node support, no network policy, no direct pod routing | Cannot apply Azure or Calico network policy; user-defined routing required for pod-to-pod across nodes | Migrate to Azure CNI Overlay via cluster recreation |

> **Default:** Azure CNI Overlay for all new clusters. Cilium variant when eBPF observability or DSR is a named requirement.

### 2. Node Pool Topology

| Pool type | Purpose | Sizing guidance | Taints / labels |
|-----------|---------|-----------------|-----------------|
| **System node pool** | kube-system workloads (CoreDNS, metrics-server, CSI drivers, Flux) | 3 nodes minimum, `Standard_D4ds_v5` or equivalent, zone-spread | `CriticalAddonsOnly=true:NoSchedule` — prevents user workloads landing on system nodes |
| **User node pool (general)** | Application workloads, ingress controllers, monitoring agents | Scale between min/max via cluster autoscaler; use `Standard_D8ds_v5` or equivalent | Label by tier: `workload-tier=app` |
| **GPU node pool** | AI/ML inference, model training, GPU-accelerated workloads | NC/ND/H100 series; quota pre-approval required (see Prerequisites); start with min=0 for cost control | `nvidia.com/gpu=present:NoSchedule`; NVIDIA device plugin DaemonSet required |
| **Spot node pool** | Fault-tolerant batch, ML training, test environments | 20% of steady-state capacity is typical; must configure pod toleration for spot eviction | `kubernetes.azure.com/scalesetpriority=spot:NoSchedule` |

**Rule:** Never place user workloads on the system node pool. System node pool resource starvation during peak load is the most common AKS reliability failure in brownfield clusters.

### 3. Workload Identity Integration

AKS Workload Identity replaces AAD Pod Identity v1 (deprecated). The flow is:

1. Enable OIDC issuer on the AKS cluster (`--enable-oidc-issuer`)
2. Enable Workload Identity webhook (`--enable-workload-identity`)
3. Create a user-assigned managed identity in Azure
4. Create a federated identity credential on the managed identity — issuer is the AKS OIDC issuer URL, subject is `system:serviceaccount:{namespace}:{service-account-name}`
5. Annotate the Kubernetes service account with `azure.workload.identity/client-id`
6. Label pods with `azure.workload.identity/use: "true"`

> **Defer to Wave 1:** Federated identity credential lifecycle, trust boundary design, and token exchange patterns are documented in `workload-identity-federation`. This skill covers AKS-side configuration only; federated credential design lives in the prerequisite skill.

```bash
# Enable OIDC issuer and workload identity on an existing cluster
az aks update \
  --resource-group rg-aks-prod \
  --name aks-prod \
  --enable-oidc-issuer \
  --enable-workload-identity

# Retrieve OIDC issuer URL for federated credential setup
az aks show \
  --resource-group rg-aks-prod \
  --name aks-prod \
  --query "oidcIssuerProfile.issuerUrl" \
  -o tsv
```

### 4. Ingress Architecture

| Controller | When to use | Integration model |
|------------|------------|-------------------|
| **AGIC (Application Gateway Ingress Controller)** | Clusters requiring WAF integration (Azure WAF v2), SSL offload at the Application Gateway tier, or static public IP management by the platform team | AGIC runs as a pod; reads Kubernetes Ingress resources; programs Application Gateway rules. Requires Application Gateway in the same or peered VNet. Use `azure-application-gateway` skill for WAF policy design. |
| **nginx ingress** | General-purpose ingress, advanced routing rules, multiple clusters sharing a load balancer, mutual TLS at the ingress tier | Deploy as Helm chart or AKS add-on; use Internal Load Balancer annotation for private ingress; pair with cert-manager for TLS automation |
| **Contour (Project Contour / Envoy)** | gRPC workloads, HTTP/2 first-class support, or Envoy-based traffic management without full service mesh complexity | Requires HTTPProxy CRD — not standard Kubernetes Ingress; evaluate team familiarity |

**Private ingress pattern:** Annotate the ingress service with `service.beta.kubernetes.io/azure-load-balancer-internal: "true"` to create an internal load balancer. Front with Azure Front Door or Application Gateway for external TLS termination and WAF.

### 5. Autoscaling Stack

| Component | Scope | Configuration note |
|-----------|-------|-------------------|
| **HPA** | Pod count based on CPU, memory, or custom metrics | Default metric server sufficient for CPU/memory; Prometheus adapter required for custom metrics |
| **KEDA** | Pod count based on external event sources (Service Bus, Event Hubs, HTTP request count, Cosmos DB RU) | Deploy via KEDA add-on or Helm; define `ScaledObject` per workload; KEDA does not replace HPA — they coexist when scaler types differ |
| **VPA** | Pod resource requests (right-sizing) | Run in `Recommendation` mode first; `Auto` mode causes pod restarts on resize — validate workload tolerance before enabling |
| **Cluster autoscaler** | Node count | Set `--min-count` and `--max-count` per node pool; configure `skip-nodes-with-local-storage` based on stateful workload presence |
| **Node Auto-Provision (NAP)** | Node SKU selection | Preview feature; AKS selects VM SKU based on pending pod resource profile — reduces manual node pool SKU maintenance |

### 6. GitOps with Flux v2

Flux v2 is the authoritative GitOps engine for AKS in this accelerator. All production cluster state flows through git — no `kubectl apply` in production pipelines.

```bash
# Enable Flux v2 GitOps extension on AKS cluster
az k8s-configuration flux create \
  --resource-group rg-aks-prod \
  --cluster-name aks-prod \
  --cluster-type managedClusters \
  --name cluster-config \
  --namespace cluster-config \
  --scope cluster \
  --url https://github.com/<org>/<fleet-config-repo> \
  --branch main \
  --kustomization name=infra path=./clusters/prod/infra prune=true \
  --kustomization name=apps path=./clusters/prod/apps prune=true dependsOn=infra
```

**Bootstrap order (canonical):** Infrastructure kustomization (namespaces, RBAC, network policy, secrets store CSI) runs first via `dependsOn`; application kustomization runs after infrastructure is healthy.

### 7. Private Cluster Pattern

A private AKS cluster disables the public API server endpoint, routing all kubectl traffic through a private endpoint inside the VNet. This satisfies Security Baseline rule #6 (public network disabled in prod).

| Element | Guidance |
|---------|----------|
| Private DNS zone | AKS creates `privatelink.<region>.azmk8s.io`; integrate with landing zone private DNS resolver for on-premises and hub reachability |
| Jump host / Bastion | Required for direct API server access; use `azure-bastion` skill for host design |
| GitOps agent connectivity | Flux v2 agents in the cluster initiate outbound git connections — no inbound to API server required; firewall egress rules in `azure-firewall` skill |
| Command invoke | `az aks command invoke` allows control-plane commands without VPN for emergency access |
| Authorized IP ranges (alternative) | For dev/test clusters where full private endpoint is overkill, restrict API server to known CIDR ranges; not acceptable for production under Security Baseline rule #6 |

## Security Baseline Reinforcement

This skill enforces all six non-negotiable Security Baseline rules in AKS context:

| Rule | AKS enforcement |
|------|----------------|
| **Rule 1 – TLS 1.2 minimum** | AKS API server enforces TLS 1.2+ by default. Ingress TLS policies must specify `ssl-protocols: TLSv1.2 TLSv1.3` in nginx annotations or Application Gateway TLS policy. |
| **Rule 2 – HTTPS-only** | Ingress controllers must redirect HTTP → HTTPS. Enforce via nginx annotation `nginx.ingress.kubernetes.io/ssl-redirect: "true"` or AGIC SSL policy. |
| **Rule 3 – No public blob access** | Container images should be pulled from private registries. Azure Policy `AKS should use private container registry` enforces this at policy scope. |
| **Rule 4 – Managed Identity preferred** | AKS system-assigned managed identity for Azure Resource Manager operations (node pool scaling, load balancer management). Workload identity (OIDC + FIC) for pod-to-Azure auth. No service principal credentials stored in cluster. |
| **Rule 5 – Azure AD-only auth** | Enable `--enable-azure-rbac` and `--enable-aad` to use Entra ID groups for Kubernetes RBAC. Disable local accounts (`--disable-local-accounts`) in production to enforce AAD-only API server access. |
| **Rule 6 – Public network disabled (prod)** | Deploy as private cluster (`--enable-private-cluster`). API server has no public endpoint. Monitor via Azure Policy `Azure Kubernetes Service Private Clusters should be enabled`. |

## Anti-Patterns

### Anti-Pattern 1: "Kubenet because it's simpler"

Kubenet is frequently chosen in initial AKS deployments because it avoids IP planning conversations. In practice, kubenet cannot support Azure or Calico network policy (it uses kube-proxy iptables only), cannot run Windows node pools, and requires user-defined routes on every node for pod-to-pod traffic across hosts — which creates a management surface that Azure CNI Overlay eliminates entirely. Starting with kubenet and later migrating to Azure CNI requires cluster recreation, not an in-place upgrade.

**Corrective action:** Default to Azure CNI Overlay for all new clusters. IP planning is simplified because pod IPs consume an overlay address space, not VNet IPs. If eBPF-based network policy or Hubble observability is a requirement, select Azure CNI Powered by Cilium at cluster creation — CNI mode cannot be changed after creation without node pool recreation.

### Anti-Pattern 2: "Single system node pool for everything"

Placing user workloads on the system node pool causes CoreDNS, the CSI drivers, and other kube-system services to compete for CPU and memory with application pods during peak load. When the application load spikes, DNS resolution degrades or fails — producing a cluster-wide outage that manifests as random pod failures rather than a recognizable DNS failure, because DNS dependencies are invisible until they break.

**Corrective action:** Always provision a separate user node pool. Taint the system node pool with `CriticalAddonsOnly=true:NoSchedule` to prevent workload scheduling. Configure the cluster autoscaler on user node pools, not the system node pool — system nodes should remain stable and slightly over-provisioned rather than dynamically scaled. This is non-negotiable for any production cluster.

### Anti-Pattern 3: "AAD Pod Identity v1 in 2026"

AAD Pod Identity v1 is deprecated. Microsoft stopped new feature development in 2022 and the community-maintained version is no longer receiving security patches. Clusters running AAD Pod Identity v1 have an unmaintained identity injection component in their security control plane. New Kubernetes versions (1.29+) have breaking changes with Pod Identity v1 that require shimming or workarounds.

**Corrective action:** Migrate to AKS Workload Identity (the OIDC + service account token + federated identity credential pattern). Enable `--enable-oidc-issuer` and `--enable-workload-identity` on the cluster. Refer to `workload-identity-federation` (Wave 1 skill) for federated credential design — that skill documents the identity trust model. Migration can be done incrementally per namespace without cluster recreation.

### Anti-Pattern 4: "AKS without private endpoint"

An AKS cluster with a public API server endpoint exposes the Kubernetes control plane to the internet. Even with authorized IP ranges configured, the public endpoint is an attack surface that violates Security Baseline rule #6 (public network disabled in prod). Authorized IP ranges are also operationally fragile — CI/CD runner IPs, developer IPs, and cloud shell IPs rotate, leading to "fix the firewall to deploy" incidents that create pressure to widen the allowed range over time.

**Corrective action:** Enable `--enable-private-cluster` at cluster creation. Private cluster mode disables the public API server endpoint entirely. For operational access, use `az aks command invoke` for emergency break-glass, Azure Bastion for developer access, and ensure CI/CD pipelines run from a network path that can reach the private endpoint (self-hosted runners in the VNet, or a deployment agent in a connected spoke). This is non-negotiable for any production cluster under this accelerator's Security Baseline.

### Anti-Pattern 5: "Manual kubectl applies in production"

`kubectl apply -f` in a production cluster from a developer laptop or an ad-hoc CI step creates configuration drift. The cluster's actual state diverges from any documented desired state within weeks of the first manual apply. Drift is invisible until something breaks or an audit demands proof of what is running. Manual applies also bypass code review, change management, and rollback evidence — the three minimum controls for regulated workload scenarios (S3).

**Corrective action:** All production cluster state must flow through GitOps (Flux v2). Desired state lives in a git repository; Flux continuously reconciles the cluster to match. Disable direct kubectl apply in production pipelines — the deployment artifact is a git commit, not a kubectl command. Break-glass exceptions (emergency manual apply to recover a broken Flux installation) must be documented, time-limited, and followed by a git commit that records the change in the canonical desired state.

## Brownfield Scenario (Scenario S8: Cloud-Native Modernization)

**Scenario:** An existing enterprise AKS estate — clusters deployed 18–36 months ago under pre-Overlay, pre-Workload-Identity, pre-GitOps defaults — needs to be assessed, classified by debt severity, and systematically modernized to meet current standards. Typical debt profile: kubenet CNI, AAD Pod Identity v1, public API server endpoint, no pod disruption budgets, no network policy, and imperative CI/CD pipelines applying manifests directly.

**Cross-skill sequencing:** Run after `workload-identity-federation` (Wave 1) is integrated. Assess existing AKS clusters for networking mode debt and pod identity migration. Hand off serverless-eligible workloads to `azure-container-apps`.

### Pre-Migration Discovery Checklist

| Discovery area | What to inventory | Why it matters |
|----------------|-------------------|----------------|
| CNI mode | `az aks show --query networkProfile.networkPlugin` per cluster | Kubenet clusters cannot be in-place migrated — requires blue-green node pool strategy |
| Kubernetes version | `az aks show --query kubernetesVersion` | Clusters within 2 minor versions of EOL must be upgraded before any other change |
| Node image version | `az aks nodepool show --query nodeImageVersion` | Stale node images have known CVEs; assess against current recommended version |
| Pod identity mechanism | Scan for `aadpodidentity` namespaces, `AzureIdentity`/`AzureIdentityBinding` CRDs | AAD Pod Identity v1 installations require migration before cluster upgrade to 1.29+ |
| API server exposure | `az aks show --query apiServerAccessProfile` | Public endpoint clusters violate Security Baseline rule #6 |
| Network policy | `az aks show --query networkProfile.networkPolicy` | Absence of network policy means all pods can communicate freely — common in dev clusters promoted to prod |
| Pod Disruption Budgets | `kubectl get pdb -A` | Missing PDBs allow simultaneous eviction of all replicas during upgrades or node drain |
| Workload identity readiness | Check for OIDC issuer enabled: `az aks show --query oidcIssuerProfile.enabled` | Required before workload identity migration can begin |
| GitOps state | Check for Flux or ArgoCD controller deployments | Absence means cluster state is imperative — assess blast radius of GitOps adoption |
| Defender for Containers | `az security pricing show --name KubernetesService` | Confirms whether runtime threat detection and KSPM are active (paid plan required) |

### Staged Modernization Playbook

| Step | Action | Exit criteria | Rollback gate |
|------|--------|---------------|---------------|
| 1 | **Stabilize control plane.** Upgrade any cluster within 2 minor versions of EOL. Enable node image auto-upgrade (`--auto-upgrade-channel node-image`). Document all cluster configurations before any change. | All clusters on supported Kubernetes version. Node image auto-upgrade enabled. Baseline configuration exported via `az aks show`. | If an upgrade breaks cluster health (API server unavailable, node pool scaling fails), revert to previous version snapshot and pause all further changes. |
| 2 | **Audit workload-to-tier fitness.** For each application running on AKS, evaluate against the AKS-vs-ACA decision tree in `docs/decisions/compute-tier-selection.md`. Identify workloads that are serverless-eligible (HTTP-only, stateless, no DaemonSet dependency). | Workload inventory complete. Serverless-eligible candidates identified and handed off to `azure-container-apps` track. | If workload migration to ACA is blocked (dependency on Kubernetes-native API), retain on AKS and document the blocking dependency. |
| 3 | **Migrate pod identity.** Enable OIDC issuer and Workload Identity webhook on each cluster. Migrate workloads from AAD Pod Identity v1 to Workload Identity namespace by namespace, validating Azure service calls after each migration wave. | All namespaces migrated. AAD Pod Identity v1 controller and CRDs removed. No `AzureIdentity` resources remain. | Re-enable Pod Identity v1 for the affected namespace if Azure service call failures are observed post-migration. Pause until root cause is isolated. |
| 4 | **Enforce network policy.** Enable Azure Network Policy or Calico on clusters without it. Start with `allow-all` baseline, then progressively add deny rules namespace by namespace. Install a policy manifest in each namespace's git path before enabling enforce mode. | Network policy CRD present. Deny-by-default applied to high-risk namespaces (payments, PII). No cross-namespace traffic observed that lacks an explicit allow rule. | Roll back network policy additions for the affected namespace if application errors correlate with policy application. Log denied traffic via `azure-network-watcher` skill before rollback. |
| 5 | **Adopt GitOps.** Install Flux v2 GitOps extension. Create a fleet config repository. Migrate current cluster state (manifests, Helm releases, ConfigMaps) into the repository. Shift pipeline to commit-based deploy. Validate Flux reconciliation health. | Flux `HelmRelease` and `Kustomization` objects healthy. `kubectl get gitrepository,kustomization -A` shows all resources `Ready`. CI/CD pipeline deploys by committing to the fleet repo, not by calling kubectl. | If Flux reconciliation stalls or overwrites an in-flight manual change, pause Flux (suspend the Kustomization) and diagnose before resuming. Keep pre-Flux imperative manifests in a `legacy/` directory until Flux adoption is confirmed stable. |
| 6 | **Harden pod security.** Apply PSA `warn` mode to all namespaces. Assess pods that generate warnings. Promote compliant namespaces to PSA `enforce` mode. Address non-compliant workloads (remove `hostNetwork`, `privileged`, `runAsRoot`) before enforce cutover. | All production namespaces running under PSA `enforce` mode. No privileged pods except designated infrastructure (CSI driver, Defender agent) with explicit exemptions. | Revert the namespace label from `enforce` to `warn` if pod scheduling failures are observed after PSA enforce activation. |
| 7 | **Enable private cluster.** For clusters with public API server endpoints, plan a cluster recreation using private cluster mode (in-place API server privatization is not supported). Use blue-green: create a new private cluster, migrate workloads via GitOps (point Flux at the same fleet repo), drain and decommission the public cluster. | New cluster has private API server. No public endpoint exists. DNS resolution of API server routes through private zone. | If workload migration to the private cluster reveals connectivity gaps (CI/CD runners, monitoring agents cannot reach the private endpoint), resolve connectivity before decommissioning the public cluster. Do not decommission until all pipelines and agents are validated. |
| 8 | **Close observability and DR gaps.** Enable Container Insights, Azure Monitor managed Prometheus, and Grafana. Configure AKS backup (Azure Backup for AKS) with a daily backup policy and cross-region restore target. Add Pod Disruption Budgets to all multi-replica deployments. | Container Insights enabled. Prometheus scraping cluster metrics. AKS backup vault configured and tested with a restore drill. PDBs present for all deployments with `replicas > 1`. | If backup agent installation causes resource pressure, reduce node pool size minimum to compensate. If PDB settings block node drain during upgrade, adjust `minAvailable` to allow rolling eviction. |

## Prerequisites and Caveats

Before applying this skill, verify the following assumptions hold for your environment. Unmet prerequisites are the most common cause of AKS architecture decisions that appear sound in design but fail in implementation.

1. **AKS LTS tier pricing:** AKS Long Term Support (LTS) is a paid add-on channel providing 2-year support windows for specific Kubernetes versions, compared to the standard 1-year community support. Guidance in this skill applies to both Standard and LTS tiers. LTS-specific notes are flagged where relevant (LTS forces node pool SKU compatibility with the supported LTS version; not all VM series are available for all LTS versions at launch).

2. **GPU node pool quota:** NC/ND/H100-series VM SKUs for GPU node pools require advance quota approval in the target region. GPU VM quota is not granted by default — submit a quota increase request (Azure Portal → Subscriptions → Usage + Quotas) before designing GPU node pools into an implementation plan. Regional GPU capacity is constrained; validate SKU availability in your target region before committing to a specific GPU series.

3. **Defender for Containers (paid plan):** Container image scanning, runtime threat detection, and Kubernetes Security Posture Management (KSPM) require the Defender for Containers plan enabled at the subscription level. This is a paid Microsoft Defender add-on — it is not included in the base AKS resource cost. Budget and authorize this plan explicitly. Without it, this skill's security recommendations for runtime protection are aspirational, not enforced.

4. **Confidential containers (Preview):** Pod sandboxing via Kata Containers (AKS confidential containers) and Confidential Computing node pools (DCsv3/ECsv5 with SEV-SNP) are in Preview in most regions as of the date of this skill. Do not design S3 regulated workload architectures that depend on Confidential Containers for production compliance without first verifying General Availability (GA) status in the target region. For GA-required confidential computing, refer to `azure-virtual-machines` and the DCsv3/ECsv5 VM series instead.

5. **AKS Edge Essentials and Azure Local:** AKS Edge Essentials (single-machine or multi-machine K8s on Windows IoT or Azure Local) is out of scope for this skill. This skill covers cloud-hosted AKS only. Arc-enabled Kubernetes on-premises extension patterns are deferred to the future `azure-arc-kubernetes` skill (Wave 5). Do not apply cloud-AKS networking mode guidance (Azure CNI Overlay) to AKS Edge Essentials deployments — the networking stack is different.

## Diagnostic Queries

### KQL: Identify AKS clusters with public API server endpoints

```kql
Resources
| where type == "microsoft.containerservice/managedclusters"
| extend apiServerAccessProfile = properties.apiServerAccessProfile
| where isnull(apiServerAccessProfile.enablePrivateCluster) or apiServerAccessProfile.enablePrivateCluster == false
| project name, resourceGroup, subscriptionId, location, apiServerAccessProfile
| order by name asc
```

### KQL: Node pool version drift detection

```kql
Resources
| where type == "microsoft.containerservice/managedclusters/agentpools"
| extend nodeImageVersion = properties.nodeImageVersion
| extend k8sVersion = properties.orchestratorVersion
| project name, resourceGroup, id, k8sVersion, nodeImageVersion
| order by k8sVersion asc
```

### KQL: Clusters missing Defender for Containers

```kql
SecurityResources
| where type == "microsoft.security/pricings"
| where name == "KubernetesService"
| where properties.pricingTier == "Free"
| project name, subscriptionId, properties
```

## References

| Topic | URL |
|-------|-----|
| AKS Landing Zone Accelerator (reference architecture) | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/app-platform/aks/landing-zone-accelerator |
| AKS baseline reference architecture | https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/containers/aks/baseline-aks |
| AKS networking concepts | https://learn.microsoft.com/en-us/azure/aks/concepts-network |
| Azure CNI Overlay | https://learn.microsoft.com/en-us/azure/aks/azure-cni-overlay |
| Azure CNI Powered by Cilium | https://learn.microsoft.com/en-us/azure/aks/azure-cni-powered-by-cilium |
| AKS Workload Identity | https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview |
| GitOps with Flux v2 on AKS | https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/tutorial-use-gitops-flux2 |
| AKS private cluster | https://learn.microsoft.com/en-us/azure/aks/private-cluster |
| Pod Security Admission | https://learn.microsoft.com/en-us/azure/aks/use-pod-security-admission |
| AKS autoscaler | https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler |
| KEDA on AKS | https://learn.microsoft.com/en-us/azure/aks/keda-about |
| Defender for Containers | https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-containers-introduction |
| AKS Backup | https://learn.microsoft.com/en-us/azure/backup/azure-kubernetes-service-backup-overview |
| Compute tier selection ADR | `docs/decisions/compute-tier-selection.md` (this repo) |
| Workload Identity Federation skill (Wave 1 prereq) | `.github/skills/workload-identity-federation/SKILL.md` (this repo) |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-18 | Saul | Initial Wave 2 authoring — AKS cluster architecture, node pool design, CNI selection, workload identity, GitOps, private cluster, brownfield modernization playbook (S8), 5 anti-patterns, prerequisites and caveats |

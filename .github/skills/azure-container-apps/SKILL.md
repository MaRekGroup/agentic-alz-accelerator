---
name: azure-container-apps
description: "Container Apps Environment architecture and serverless container patterns for Azure Landing Zones. USE FOR: Container Apps Environment design (workload profiles vs consumption), KEDA autoscaling rules, Dapr component integration, revision management (blue-green, traffic splitting), custom domain + managed certificate, Container Apps Jobs, multi-container apps, health probes, observability (structured logging, distributed tracing), and Container Apps landing zone patterns. DO NOT USE FOR: AKS cluster architecture (use azure-kubernetes-service), container registry setup (future: azure-container-registry), containerized Azure Functions (future skill), general virtual network design (use azure-virtual-network), App Service / Web Apps (different compute; future skill), or workload identity federation setup (use workload-identity-federation)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-compute
---

# Azure Container Apps Skill

## Overview

Azure Container Apps (ACA) is a fully managed serverless container platform that abstracts Kubernetes infrastructure while retaining powerful scaling, traffic management, and distributed application primitives. ACA is the preferred compute tier for stateless HTTP microservices, event-driven workloads, and Dapr-integrated services where the team does not need — or should not own — full Kubernetes cluster operations.

**The AKS-vs-ACA boundary is the most common confusion point in this accelerator.** This skill does not redefine that boundary. The canonical decision tree lives in `docs/decisions/compute-tier-selection.md`. Read that ADR before using this skill to confirm ACA is the correct tier for the workload under design. A concise summary: choose ACA when there is no need for DaemonSets, custom CNI, privileged containers, Kubernetes-native CRDs, or multi-cluster federation. When any of those needs exist, use `azure-kubernetes-service` instead.

## Boundary

### USE FOR

- Container Apps Environment architecture: Consumption vs. Dedicated workload profile selection, environment-level VNET injection, internal vs. external ingress
- KEDA autoscaling rules: HTTP concurrent-requests scaler, Azure Queue / Service Bus scalers, custom metrics scalers, scale-to-zero configuration
- Dapr building-block integration: state store, pub/sub, service invocation, secrets, bindings; sidecar configuration, Dapr component scoping
- Revision management: blue-green deployments, canary splits, traffic weight rules, revision lifecycle policies
- Custom domains + managed TLS certificates: DNS validation, certificate binding, managed cert rate-limit awareness
- Container Apps Jobs: scheduled (cron) jobs, event-triggered jobs, manual jobs for batch workloads
- Multi-container apps: sidecar patterns, init containers, shared volume mounts
- Health probes: startup, liveness, and readiness probes at the container-app level
- Observability: structured logging to Log Analytics, distributed tracing with Application Insights / Dapr tracing, scaling metrics dashboards
- Container Apps landing zone patterns: hub-spoke integration, private DNS zone wiring, workload identity via managed identity

### DO NOT USE FOR

- Full Kubernetes cluster architecture → use `azure-kubernetes-service`
- Container registry design, image scanning, and geo-replication → future `azure-container-registry` skill
- Containerized Azure Functions hosting → future dedicated skill
- General virtual network design, hub-spoke topology, UDRs → use `azure-virtual-network`
- App Service, Web Apps, or Static Web Apps → different compute surface; future skill
- Workload identity federation setup (OIDC trust, FIC, cross-cloud) → use `workload-identity-federation`

> **AKS-vs-ACA ADR:** The canonical tier-selection decision tree is `docs/decisions/compute-tier-selection.md`. This skill assumes you have already consulted that ADR and confirmed ACA is the right choice. Do NOT substitute inline guidance in this skill for the ADR's decision criteria.

## CAF Design Area Alignment

| CAF Design Area | Priority | How ACA applies |
|-----------------|----------|-----------------|
| **Platform Automation & DevOps** | **Primary** | Revision-based deployment model maps directly to CI/CD pipelines: each build produces a new revision; traffic weight rules implement blue-green and canary without external tooling. Forge generates ACA Bicep/Terraform modules; Strategist selects revision strategy per environment. |
| **Network Topology & Connectivity** | **Primary** | VNET injection places the ACA environment into a landing zone subnet with private DNS zone integration. Internal-only environments eliminate public ingress surface; UDR-based egress routes traffic through Azure Firewall. Subnet sizing is a hard prerequisite (see Prerequisites). |
| **Security** | **Primary** | Managed identity eliminates secrets in environment variables. Key Vault secret references surface secrets at runtime without storing them in container image or app config. Dapr mTLS encrypts inter-app traffic at the application layer. Internal environments remove public attack surface. |
| **Management** | Secondary | Structured log output to Log Analytics workspace provides unified observability across all apps in the environment. Application Insights distributed tracing spans Dapr service invocations. Scaling metrics feed Azure Monitor alerts for capacity planning. |

## WAF Pillar Mapping

| WAF Pillar | Priority | Contribution |
|------------|----------|--------------|
| **Performance Efficiency** | **Primary** | KEDA-native autoscaling responds to queue depth, HTTP concurrency, and custom metrics without cluster-level operator management. Workload profiles provide dedicated CPU/memory classes for compute-intensive apps while sharing environment-level infrastructure. |
| **Cost Optimization** | **Primary** | Consumption plan charges per vCPU-second and GiB-second; scale-to-zero eliminates idle cost entirely. Dedicated workload profiles reduce unit cost at sustained load by removing per-request billing overhead. Jobs on event triggers replace always-on polling workers. |
| **Reliability** | Secondary | Multi-revision traffic splitting provides revision rollback in seconds by shifting 100% weight to the prior revision. Health probes (startup, liveness, readiness) gate traffic away from unhealthy replicas. Zone redundancy at environment level distributes replicas across availability zones. |
| **Security** | Secondary | Security Baseline rules #4 (managed identity) and #6 (no public network in prod) are natively enforced via managed identity binding and internal-only environment configuration. Secret references prevent credential exposure in container specs. |

## Scenarios Unblocked

- **S2 — Multi-Region AI Platform:** Cannot architect serverless inference endpoints or event-driven AI data pipelines without ACA KEDA scaling patterns. ACA provides per-request scaling for inference APIs that are idle between bursts, eliminating the cost of reserved GPU capacity for low-frequency calls. Dapr pub/sub connects event sources to inference workers without bespoke queue-consumer code.
- **S5 — ISV Multi-Tenant SaaS:** Cannot design per-tenant microservice isolation with noisy-neighbor protection using a managed runtime. Workload profiles provide dedicated compute classes per tenant tier; Dapr state-store scoping enforces tenant data boundaries at the component level; revision traffic splitting enables per-tenant canary rollouts.
- **S8 — Cloud-Native Modernization:** Cannot deliver "replatform without Kubernetes complexity" for teams that do not need — and should not own — a full AKS cluster. ACA is the correct landing zone for workloads where `docs/decisions/compute-tier-selection.md` indicates ACA criteria are met and AKS criteria are not.

## Architecture Patterns

### Workload Profile Selection

| Profile Type | Use When | Cost Model |
|---|---|---|
| **Consumption** | Bursty or intermittent workloads; scale-to-zero acceptable; per-request pricing is favorable | Per vCPU-second + GiB-second; zero cost at zero replicas |
| **Dedicated (D-series)** | Predictable high-throughput; scale-to-zero NOT acceptable (latency-sensitive); sustained load makes per-request pricing expensive | Hourly per node; amortizes at ≥40% utilization vs consumption |
| **Spot (Consumption + spot)** | Batch jobs, non-latency-sensitive background processing; interruption tolerance required | Spot pricing discount; interruption possible at any time |

Selection rule: default to **Consumption** for new workloads. Switch to **Dedicated** only when a cost model comparison (90-day load data) shows dedicated is cheaper at the projected utilization rate, OR when cold-start latency at min=0 is unacceptable and min=1 on Dedicated is required.

### KEDA Scaler Patterns

| Scaler | Trigger Source | When to Use |
|---|---|---|
| `http` | Concurrent HTTP requests | HTTP microservices; scale-to-zero between idle periods |
| `azure-servicebus` | Service Bus queue / topic message count | Async message processors; event-driven workers |
| `azure-storage-queue` | Queue message count | Lightweight queue consumers; Jobs for one-shot processing |
| `azure-eventhubs` | Event Hub partition lag | Stream processing; telemetry ingestion pipelines |
| `custom` | External metrics endpoint | Domain-specific scaling (AI inference backlog, business KPIs) |

**Scale-to-zero rule:** Set `minReplicas: 0` only when cold start latency of 1–3 seconds is acceptable. For HTTP endpoints where P99 < 200ms is required, set `minReplicas: 1` to maintain a warm replica. See Prerequisites — cold start caveat.

### Dapr Building Blocks

| Building Block | GA Status | ACA Configuration |
|---|---|---|
| Service invocation | ✅ GA | Automatic mTLS; use app-id routing (`http://localhost:3500/v1.0/invoke/{appId}/method/{path}`) |
| State management | ✅ GA | Scope components per app-id; use Azure Table Storage or Cosmos DB as backend |
| Pub/Sub messaging | ✅ GA | Azure Service Bus or Event Grid as broker; scope subscriptions per component |
| Secrets management | ✅ GA | Reference Key Vault secrets via Dapr secret store; do not use environment variables for secrets |
| Input/output bindings | ✅ GA | Event-triggered ingress and egress without custom SDK code |
| Workflow | ⚠️ Beta | Durable, multi-step orchestration; **do not use in production without explicit preview acceptance** |
| Distributed lock | ⚠️ Alpha | Distributed mutex; **not production-ready; use Azure Blob Storage leases as alternative** |

**Sidecar overhead:** Each Dapr-enabled replica carries a ~128MB RAM sidecar. Factor this into workload profile sizing and KEDA scale calculations. A 512MB replica with Dapr enabled has ~384MB available to the app container. Set `minReplicas` and resource requests accordingly to avoid OOM kills during startup.

### Revision Management and Traffic Splitting

ACA's revision model is the primary zero-downtime deployment mechanism. Do not bypass it with in-place updates.

```bash
# Deploy a new revision without routing any traffic to it
az containerapp update \
  --name myapp --resource-group myrg \
  --image myregistry.azurecr.io/myapp:v2 \
  --revision-suffix v2 \
  --traffic-weight label=v1:100

# Canary: shift 10% to new revision
az containerapp ingress traffic set \
  --name myapp --resource-group myrg \
  --revision-weight myapp--v1=90 myapp--v2=10

# Full cutover after validation
az containerapp ingress traffic set \
  --name myapp --resource-group myrg \
  --revision-weight myapp--v2=100

# Emergency rollback: redirect all traffic to prior revision in one command
az containerapp ingress traffic set \
  --name myapp --resource-group myrg \
  --revision-weight myapp--v1=100
```

Enable `multiple` revision mode in the Container App before deploying multiple revisions:

```bash
az containerapp revision set-mode \
  --name myapp --resource-group myrg \
  --mode multiple
```

### VNET Injection Patterns

ACA environments can be deployed into a dedicated subnet for network isolation. Two injection topologies:

| Topology | Subnet Requirement | Use When |
|---|---|---|
| **Internal (private)** | `/27` minimum (Consumption-only) or `/23` minimum (Workload Profiles) | All production landing zone deployments; no public ingress; traffic enters via Private Link or internal load balancer |
| **External (public)** | Same subnet sizing | Dev/test environments; controlled public ingress acceptable; pair with Azure Front Door or App Gateway WAF for production |

Private DNS zone `privatelink.{region}.azurecontainerapps.io` must be linked to the VNET for internal environments. Hub-spoke topologies require DNS forwarder or Azure DNS Private Resolver to resolve ACA FQDNs from peered spokes.

> **Subnet sizing is a hard prerequisite.** Plan the subnet CIDR before environment creation — it cannot be changed after deployment. See Prerequisites for IP planning guidance.

### Container Apps Jobs

Jobs are the correct pattern for batch workloads, scheduled tasks, and one-shot event-triggered execution. Do not use long-running apps with polling loops as a substitute for Jobs.

| Job Trigger | Use Case | Example |
|---|---|---|
| **Schedule (cron)** | Periodic data processing, reports, cleanup tasks | Nightly ETL pipeline |
| **Event (KEDA)** | Queue-depth-triggered batch execution | Process items from Service Bus when queue > threshold |
| **Manual** | Ad-hoc execution via API or CLI | On-demand data migration, one-time seed job |

### Managed Identity for ACA

ACA apps support both system-assigned and user-assigned managed identities. See `workload-identity-federation` for federation patterns. ACA-specific guidance:

- Use **user-assigned managed identity** when the identity must persist across app redeployments or be shared across multiple apps (e.g., a shared Key Vault reference identity for an environment).
- Use **system-assigned managed identity** for single apps with no shared identity requirement.
- Always grant identity access to Key Vault (secret `Get`) and container registry (AcrPull) via RBAC — do not use access policies.
- Secret references in app configuration pull from Key Vault at startup; the app never sees the raw secret value in environment variables.

```bash
# Assign user-assigned managed identity to a container app
az containerapp identity assign \
  --name myapp --resource-group myrg \
  --user-assigned /subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}

# Grant Key Vault secret read access to the identity
az role assignment create \
  --assignee {identityPrincipalId} \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vaultName}
```

## Security Baseline Reinforcement

| Security Baseline Rule | ACA Enforcement |
|---|---|
| **#4 — Managed Identity preferred** | All ACA apps must use managed identity for Key Vault, ACR, and downstream Azure service access. No connection strings in environment variables. |
| **#6 — Public network disabled (prod)** | All production ACA environments must use internal-only ingress (`--ingress internal`). External ingress permitted only in dev/test with explicit approval. |
| **#1 / #2 — TLS 1.2, HTTPS-only** | ACA managed ingress enforces TLS 1.2 and redirects HTTP to HTTPS by default. Custom domains must use managed or customer-provided certificates — never plain HTTP. |
| **#3 — No public blob access** | Storage accounts used as Dapr state stores or volume mounts must have `allowBlobPublicAccess: false`. |
| Dapr mTLS | Enable Dapr mTLS in the environment to encrypt all Dapr service invocation traffic. Do not disable mTLS in shared environments. |
| Secret references | All sensitive configuration must use Key Vault secret references, not inline secret values. Warden validates this at policy enforcement time. |

## Anti-Patterns

### 1. "ACA for Everything"

ACA is not a Kubernetes replacement. It is a managed runtime for workloads that do not need Kubernetes primitives. Using ACA for workloads requiring DaemonSets (per-node log forwarders, security scanners), privileged containers (kernel modules, eBPF programs), custom CNI (Calico policy enforcement, Cilium encryption), or Kubernetes CRDs (operators, custom controllers) results in fragile workarounds — multiple ACA apps attempting to simulate DaemonSet behavior, or workloads silently losing capabilities they depend on.

**Corrective action:** Before choosing ACA, evaluate the workload against the decision tree in `docs/decisions/compute-tier-selection.md`. If any "Choose AKS When" criterion is met, use `azure-kubernetes-service`. ACA is the right choice only when all AKS criteria are absent.

### 2. "Consumption Plan for Predictable High-Throughput"

Consumption plan pricing (per vCPU-second) is cost-effective for bursty or intermittent workloads. For sustained, predictable high-throughput — e.g., an API receiving 500 req/s continuously — the per-request cost of Consumption exceeds the hourly cost of a Dedicated workload profile at equivalent compute. Teams who deploy high-throughput services on Consumption and then wonder why ACA is "expensive" have the wrong profile.

**Corrective action:** Run a 90-day utilization projection. If the workload will run at ≥40% CPU utilization for more than 60% of hours, a Dedicated workload profile (D-series) will be cheaper. Use Consumption only where scale-to-zero genuinely saves cost.

### 3. "Dapr Without Understanding Sidecar Overhead"

Dapr injects a sidecar container into every replica of a Dapr-enabled app. That sidecar consumes approximately 128MB of RAM per replica regardless of app activity. Teams that set resource limits without accounting for the sidecar hit OOM restarts during startup spikes, misattribute OOM kills to their application code, or under-provision workload profiles and experience performance degradation.

**Corrective action:** Add 128MB to every per-replica memory estimate for Dapr-enabled apps. If the app is allocated 256MB, the effective app memory is ~128MB. Adjust resource requests accordingly. Use Dapr's metrics endpoint (`http://localhost:9090/metrics`) to monitor actual sidecar consumption before finalizing sizing.

### 4. "Ignoring Scale-to-Zero Cold Start"

Setting `minReplicas: 0` eliminates idle compute cost — a genuine benefit. But it introduces a cold-start latency of 1–3 seconds on the first request after a zero-replica period. For most background processors and asynchronous workers, this is acceptable. For synchronous HTTP APIs where clients expect sub-200ms P99 latency, scale-to-zero introduces tail latency spikes that will appear in SLOs as violations.

**Corrective action:** Set `minReplicas: 1` for any HTTP API with a P99 latency SLO below 1 second. Reserve `minReplicas: 0` for async workers, scheduled jobs, and APIs where occasional cold-start latency is acceptable. Document the decision per-app in the implementation plan.

### 5. "Single Revision with In-Place Updates"

ACA's default revision mode is `single`, which means every container update replaces the running revision immediately with zero ability to split traffic or roll back without redeployment. Teams operating in single-revision mode cannot perform canary deployments, cannot roll back in seconds, and cannot validate a new build with a subset of traffic before full cutover.

**Corrective action:** Enable `multiple` revision mode before deploying any production workload. Implement a CI/CD pipeline that deploys new revisions with 0% traffic weight, validates via health checks and synthetic traffic, then shifts weight incrementally. Keep the prior revision active for at least one deployment cycle to enable instant rollback via weight redistribution.

## Brownfield Scenario (Scenario S8: Cloud-Native Modernization)

### Sub-Narrative: Migrating to Serverless Containers

ACA's S8 narrative differs from AKS's S8 narrative. AKS S8 addresses **modernizing existing clusters** — assessing technical debt in running Kubernetes deployments. ACA S8 addresses **migrating away from over-engineered or legacy container runtimes** to a serverless model: Docker Compose stacks on VMs, App Service containers, Azure Container Instances singletons, and AKS clusters that are running simple stateless workloads at full cluster overhead without exploiting any Kubernetes primitive.

The goal is to reduce operational burden and eliminate idle cost by moving appropriately-scoped workloads to a managed runtime. Before performing any migration, verify the workload does not meet "Choose AKS When" criteria in `docs/decisions/compute-tier-selection.md`. Migration to ACA is only correct when the workload genuinely does not need Kubernetes.

### Pre-Migration Discovery Checklist

Audit each candidate workload for the following before selecting ACA as the migration target:

| Check | Signal | Action |
|---|---|---|
| **Container runtime?** | Dockerfile or container image exists | ACA candidate — proceed to tier evaluation |
| **DaemonSet / privileged?** | Per-node agents, kernel modules, eBPF | NOT an ACA candidate — use AKS or VM |
| **Kubernetes CRDs / operators?** | Custom resources, admission webhooks | NOT an ACA candidate — use AKS |
| **Stable pod identity / StatefulSet?** | Ordered naming, persistent PVC per replica | NOT an ACA candidate — use AKS |
| **Custom CNI / network policy?** | Calico, Cilium, custom egress policy | NOT an ACA candidate — use AKS |
| **State externalized?** | No in-memory state; state in DB, cache, or blob | ACA candidate — stateless is prerequisite |
| **HTTP or event-triggered?** | REST API, queue consumer, scheduler | ACA candidate — aligns with ACA scaling model |
| **Acceptable cold start?** | Latency SLO > 1s, or async path | Scale-to-zero viable; if SLO < 1s, min=1 required |
| **AKS cluster single deployment?** | One Deployment, no CRDs, no operators | Over-engineered — strong ACA migration candidate per ADR brownfield lens |
| **Docker Compose stack?** | Multi-service compose file | Convert services to separate Container Apps; shared network becomes ACA Environment |
| **App Service container?** | Containerized app on App Service plan | Lift directly to ACA; evaluate KEDA for scaling over App Service autoscale rules |
| **ACI singleton?** | Azure Container Instances without orchestration | Migrate to ACA for revision management, health probes, and scaling |

### Staged Rollout Playbook

Execute migration per workload, not per environment. Each step has an associated rollback gate.

| Step | Action | Rollback Gate |
|---|---|---|
| **1. Classify candidates** | Run discovery checklist; produce a scored candidate list from Assessor inventory. Disqualify any workload with AKS criteria. | Stop: candidate classification; no infrastructure changed yet. |
| **2. Containerize (if needed)** | For Docker-on-VM workloads: validate Dockerfile, externalize state, remove hard-coded hostnames. For existing container images: validate 12-factor alignment. | Revert to existing VM/App Service; no ACA resources exist yet. |
| **3. Select workload profile** | Apply profile selection table. For bursty workloads: Consumption. For sustained: Dedicated. For batch: Consumption + Jobs. | No infrastructure deployed; profile decision is reversible at this step. |
| **4. Provision ACA Environment** | Create Container Apps Environment with VNET injection. Configure private DNS zone. Validate internal vs. external ingress choice. Enable zone redundancy in production. | Delete environment; no apps deployed yet; DNS rollback is manual but contained. |
| **5. Migrate with KEDA scaling** | Deploy apps to ACA with KEDA scalers matching the original scaling trigger (HTTP, queue, schedule). Set initial `minReplicas: 1` for all services until cold start behavior is validated. | Delete container apps; re-route traffic to legacy compute. Environment persists for next iteration. |
| **6. Validate and compare** | Run synthetic traffic. Compare latency, throughput, and error rate against legacy baseline. Validate Dapr component connectivity if applicable. | Rollback via traffic redirection to legacy; ACA environment remains for debugging. |
| **7. Cut traffic via revision splitting** | Use revision traffic weight to shift a percentage of production traffic to ACA. Start at 10%; increase in 25% increments on successful validation intervals. | Shift weight back to legacy revision (or legacy compute) with a single `az containerapp ingress traffic set` command. |
| **8. Decommission legacy compute** | After 100% traffic on ACA and ≥72 hours of stable operation: delete legacy App Service plan, ACI, or AKS deployment. Scale down over-provisioned AKS clusters if partial migration. | No automatic rollback after this step. Ensure ACA revision history retains prior revision for at least one sprint before decommission. |

### Cross-Skill Sequencing

Run after `azure-kubernetes-service` assessment determines which workloads don't need full K8s. Migrate identified candidates from VMs or over-engineered AKS deployments to ACA with KEDA scaling. References `docs/decisions/compute-tier-selection.md` for tier selection criteria.

## Prerequisites and Caveats

Surface all five items below with the architecture team before environment provisioning. These are the most common causes of rework in ACA deployments.

| Assumption | Detail | Action |
|---|---|---|
| **ACA Workload Profile regional availability** | Dedicated workload profiles are GA as of late 2024, but specific D-series SKUs are not available in all Azure regions. The Consumption plan is universally available. | Before committing to a Dedicated profile architecture, verify SKU availability in the target region via the [ACA regional availability matrix](https://learn.microsoft.com/en-us/azure/container-apps/quotas). Confirm with `az containerapp env workload-profile list-supported --location {region}`. |
| **VNET injection subnet sizing** | ACA Environments with VNET injection require a dedicated subnet. Minimum size: `/27` (32 addresses) for Consumption-only environments; `/23` (512 addresses) for Workload Profile environments (dedicated or mixed). The subnet CIDR cannot be changed after environment creation. | Plan subnet CIDR before environment provisioning. Coordinate with the network team for the hub-spoke address space. Record the decision in the implementation plan — this is irreversible. |
| **Custom domain managed certificate rate limits** | Azure-managed certificates for custom domains are free but subject to Azure App Service certificate issuance rate limits. High-volume domain binding scenarios (many subdomains in rapid succession) may hit throttling. | For standard deployments (< 20 custom domain bindings per environment), managed certs are safe. For ISV SaaS scenarios with many per-tenant subdomains, evaluate wildcard certificates or customer-provided certificates to avoid rate-limit exposure. |
| **Dapr GA vs. preview component status** | Core Dapr building blocks (service invocation, state management, pub/sub, secrets, bindings) are GA. Dapr Workflow is **Beta**. Dapr Distributed Lock is **Alpha**. Preview-status components can change API surface or be deprecated without standard notice. | Use only GA Dapr components in production. If Workflow or Distributed Lock is required, obtain explicit stakeholder acceptance of the preview risk and document it in the governance constraints. Track component status at [Dapr component certification](https://docs.dapr.io/operations/components/certification-lifecycle/). |
| **Scale-to-zero cold start latency** | Setting `minReplicas: 0` saves cost by eliminating idle compute but introduces a cold-start delay of approximately 1–3 seconds when the first request arrives after a zero-replica period. This latency includes container image pull time (mitigated by image layer caching), Dapr sidecar initialization (if enabled), and application startup time. | Cold start is acceptable for async workers, batch Jobs, and APIs with relaxed latency SLOs. Set `minReplicas: 1` for any synchronous HTTP API where P99 latency < 1 second is required. Document the min-replicas decision per app in the implementation plan. |

## References

| Resource | Notes |
|---|---|
| **[`docs/decisions/compute-tier-selection.md`](../../../docs/decisions/compute-tier-selection.md)** | **Primary reference — read first.** Canonical AKS vs. ACA vs. VM decision tree. This skill assumes you have consulted this ADR. Use it to confirm ACA is the correct tier before applying any guidance from this skill. |
| [`workload-identity-federation`](../workload-identity-federation/SKILL.md) | Wave 1 soft prereq. Covers federated identity credentials, AKS Workload Identity, and cross-cloud federation patterns. ACA managed identity for Azure service access is covered in this skill; federation with external OIDC providers requires the Wave 1 skill. |
| [`azure-kubernetes-service`](../azure-kubernetes-service/SKILL.md) | Wave 2 sibling. Brownfield S8 sequencing: run AKS assessment first to identify workloads that do not need K8s; those candidates are ACA migration targets. |
| [`azure-virtual-network`](../azure-virtual-network/SKILL.md) | General VNET design, hub-spoke topology, and UDR patterns. Defer VNET injection subnet placement and hub-spoke peering to this skill. |
| [Azure Container Apps — Overview](https://learn.microsoft.com/en-us/azure/container-apps/overview) | Microsoft Learn: capabilities, quotas, regional availability. |
| [ACA Landing Zone Accelerator](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/app-platform/container-apps/landing-zone-accelerator) | CAF-aligned reference architecture for ACA in enterprise landing zones. Hub-spoke integration, private DNS, and governance baseline. |
| [KEDA scalers documentation](https://keda.sh/docs/scalers/) | Authoritative scaler reference for HTTP, queue, Event Hub, and custom metrics scalers used in ACA KEDA configuration. |
| [Dapr component certification lifecycle](https://docs.dapr.io/operations/components/certification-lifecycle/) | GA vs. Beta vs. Alpha component status. Consult before using any non-core building block in production. |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-18 | Saul | Initial Wave 2 authoring. ACA skill covering workload profiles, KEDA, Dapr, revision management, VNET injection, Jobs, managed identity, Security Baseline reinforcement, 5 anti-patterns, Brownfield S8 migration playbook, and 5 hidden-assumption caveats. |

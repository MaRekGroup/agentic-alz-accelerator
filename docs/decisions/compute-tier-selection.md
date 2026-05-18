# ADR: Compute Tier Selection (AKS vs Container Apps vs Virtual Machines)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-18 |
| **Decision Makers** | Linus (Architect, on behalf of Squad) |
| **Related Skills** | `azure-kubernetes-service`, `azure-container-apps`, `azure-virtual-machines` (Wave 2), `workload-identity-federation`, `azure-rbac`, `azure-networking` (Wave 1 / existing) |

## Context

Enterprise landing zones host workloads spanning legacy virtual machines, containerized microservices, event-driven serverless functions, and GPU-accelerated AI inference. The "right" compute tier depends on workload characteristics, team Kubernetes expertise, scaling profile, compliance posture, and operational tolerance. Selecting the wrong tier creates architecture debt that compounds across the estate — over-engineering with AKS where Container Apps suffices wastes operational budget, while under-engineering with VMs where containers belong locks teams into manual scaling and patching cycles.

Approximately 80% of brownfield engagements assessed by this accelerator involve at least one mis-tiered workload: an HTTP API running on a full AKS cluster with a single deployment, a stateless function running on a persistent VM, or a database workload forced into containers without persistent volume planning. These mis-tierings trace to absent decision criteria at the architecture phase — the moment when the workload-to-tier mapping should have been made explicit.

This ADR establishes the canonical decision boundary between Azure Kubernetes Service (AKS), Azure Container Apps (ACA), and Azure Virtual Machines (VMs). The three Wave 2 SKILL.md files (`.github/skills/azure-kubernetes-service/SKILL.md`, `.github/skills/azure-container-apps/SKILL.md`, `.github/skills/azure-virtual-machines/SKILL.md`) reference this document for tier selection — they do NOT redefine these boundaries inline. Each SKILL.md goes deep on its tier's internals; this ADR stays in the boundary layer.

## Decision Tree

### Choose AKS When

| Criterion | Rationale |
|-----------|-----------|
| Workload requires custom CNI (Calico, Cilium, Azure CNI Overlay) | ACA only supports managed networking; custom CNI requires cluster-level control |
| DaemonSets needed (per-node agents: log forwarders, security scanners, GPU drivers) | ACA has no DaemonSet equivalent — every container is an app, not an infrastructure sidecar |
| Privileged containers required (host namespace, custom kernels, eBPF) | ACA runs in a shared multitenant environment — no host-level access |
| StatefulSets at scale (databases, message brokers with persistent identity and stable network IDs) | ACA supports volume mounts but not stable pod identity or ordinal-based naming |
| Multi-cluster federation needed (multi-region active-active, fleet management) | AKS Fleet Manager enables cross-cluster orchestration; ACA is single-environment |
| Service mesh required at cluster level (Istio, Linkerd, OSM) | ACA has built-in Dapr but not arbitrary service mesh injection |
| Windows Server containers on Kubernetes | ACA does not support Windows container workload profiles (GA as of 2026) |
| Workload needs Kubernetes-native APIs (CRDs, operators, admission webhooks) | ACA abstracts Kubernetes — no direct API server access |
| Team has Kubernetes operational expertise OR committed investment plan | AKS operational overhead is justified when the team can exploit K8s-native capabilities |
| GPU node pools for AI/ML model hosting with custom scheduling | AKS supports NC/ND-series GPU node pools with taint-based scheduling; ACA GPU profiles are limited |

### Choose Azure Container Apps When

| Criterion | Rationale |
|-----------|-----------|
| HTTP microservices with simple ingress (path/host routing, TLS termination) | ACA managed ingress handles this without maintaining an ingress controller |
| Event-driven workloads (queue processors, blob triggers, custom KEDA scalers) | ACA has native KEDA integration without cluster-level KEDA operator management |
| Scale-to-zero is acceptable and desirable (cost optimization over cold-start latency) | ACA Consumption plan scales to zero automatically; AKS requires KEDA + node autoscaler |
| Dapr building blocks fit the architecture (pub/sub, state, service invocation) | ACA has native Dapr sidecar injection — no Helm charts or operator lifecycle management |
| Team prefers managed runtime over cluster ownership | ACA abstracts infrastructure: no node patching, no control plane upgrades, no etcd management |
| Per-app revision management and traffic splitting (blue-green, canary) | Built-in revision model without Flagger, Argo Rollouts, or custom Kubernetes resources |
| Microservices that don't need Kubernetes-native primitives | If you aren't using CRDs, operators, or DaemonSets, the K8s overhead isn't earning its keep |
| Rapid prototyping that may graduate to AKS later | ACA-to-AKS migration path is well-defined (same container images, similar scaling concepts) |
| Jobs and background tasks with scheduled or event-triggered execution | ACA Jobs support cron and event triggers without CronJob/Job resource management |

### Choose Azure Virtual Machines When

| Criterion | Rationale |
|-----------|-----------|
| Legacy workload not yet containerized (no Dockerfile, binary-only deployment) | VMs accept any installable software without containerization investment |
| License requires bare-OS access (per-VM ISV licensing, BYOL with host affinity) | Some ISV licenses bind to VM identity, MAC address, or require direct OS audit access |
| Specialized hardware (HPC with InfiniBand, FPGA, custom GPU driver stacks) | VMs expose raw hardware; containers add a layer that blocks some HPC interconnects |
| Confidential computing required (DCsv3/DCdsv3/ECsv5 with SEV-SNP or SGX enclaves) | Confidential VMs provide hardware-based attestation; AKS Confidential Containers is preview-only |
| Dedicated Hosts required for regulatory compliance (physical isolation) | Azure Dedicated Host guarantees hardware isolation — not available for ACA, limited for AKS |
| Application not container-friendly (Windows GUI apps, heavy stateful desktop workloads) | Containers assume headless, stateless-by-default design |
| Mainframe/midrange modernization (COBOL-to-.NET rehosting) | Rehosted binaries often depend on file system layout, registry, and OS services |
| Regulatory hold requiring OS-level audit agents (EDR, DLP with kernel hooks) | Some compliance regimes mandate specific kernel-level agents not installable in containers |

### Mixed Estate Guidance (Most Enterprises)

Most enterprises will use multiple tiers simultaneously. This is correct and expected.

| Principle | Guidance |
|-----------|----------|
| Decision granularity is per-workload, not per-environment | A production environment may contain AKS for platform services, ACA for API tiers, and VMs for legacy backends — all in the same landing zone |
| AKS for stateful platform services | Databases, message brokers, monitoring infrastructure with persistent storage and stable identity |
| ACA for stateless API and event tiers | Request-handling services, webhook receivers, background processors |
| VMs for legacy and hardware-bound workloads | Anything that cannot be containerized without disproportionate effort |
| Avoid tier mixing within a single workload boundary | A single microservice should not span AKS and ACA — pick one tier per bounded context |
| Plan tier transitions explicitly | Brownfield VMs → AKS (containerize + orchestrate) or VMs → ACA (containerize + simplify) are both valid graduation paths |

## Trade-Off Matrix (WAF Pillars)

| WAF Pillar | AKS | Azure Container Apps | Virtual Machines |
|------------|-----|---------------------|------------------|
| **Reliability** | Zone-redundant node pools, pod disruption budgets, multi-cluster federation for active-active. Highest ceiling but requires explicit configuration. | Managed zone redundancy, automatic health probes and restarts, revision-based rollback. Simpler reliability posture with lower ceiling. | Availability Sets, VMSS zone spanning, Azure Site Recovery for DR. Mature but operationally heavy — requires manual health management. |
| **Security** | Network policies (Calico/Cilium), pod security standards, Defender for Containers (paid add-on), workload identity federation. Deep control but large attack surface to manage. | Managed VNet injection, built-in mTLS between apps, Defender for Containers support. Reduced attack surface through abstraction. | NSGs, Azure Firewall integration, Defender for Servers (paid add-on), JIT VM access, disk encryption. Full OS-level control; highest patching burden. |
| **Cost Optimization** | Node pool autoscaler + KEDA for efficient bin-packing. Reserved Instances for base capacity. Cost-effective at scale but high minimum (≥3 nodes for production). | Scale-to-zero eliminates idle cost. Consumption plan has no minimum. Cost-effective for bursty/intermittent workloads. Dedicated workload profiles for predictable cost. | Reserved Instances, Spot VMs for batch, Azure Hybrid Benefit for Windows/SQL licenses. Right-sizing via Advisor. Idle VMs are pure waste. |
| **Operational Excellence** | Full Kubernetes ecosystem (GitOps, Helm, Kustomize). AKS upgrades require planning. Cluster-level observability with Prometheus/Grafana or Azure Monitor. High operational investment. | Minimal operational surface — no cluster upgrades, no node patches. Revision management is the primary operational concern. Azure Monitor integration built-in. | OS patching (Update Manager), image management, configuration drift. Highest operational burden per workload. Azure Automation for scale. |
| **Performance Efficiency** | Custom node pools (CPU, memory, GPU), pod resource requests/limits, horizontal and vertical pod autoscaling. Maximum tuning control. | Workload profiles for resource classes, KEDA-based autoscaling. Less granular than AKS but sufficient for most HTTP/event workloads. | VM SKU selection for exact resource profile, proximity placement groups for latency-sensitive workloads, accelerated networking. |

## Brownfield Assessment Lens

When the Assessor agent (Step 0) evaluates an existing estate, it should classify each compute workload into one of three categories and recommend a tier transition where appropriate:

| Current State | Assessment Signal | Recommended Action |
|---------------|-------------------|--------------------|
| VM running a containerized workload (Docker on VM) | Container runtime detected, no orchestrator | Candidate for AKS or ACA migration — evaluate against decision tree above |
| VM running a legacy binary (no container runtime) | No Dockerfile, binary-only deployment, ISV licensing | Assess containerization feasibility; if low → stay on VM; if medium/high → plan ACA/AKS migration |
| AKS cluster with single deployment, no custom resources | No CRDs, no DaemonSets, no operators, single namespace | Over-engineered — candidate for ACA replatform (reduce operational overhead) |
| AKS cluster fully utilizing K8s primitives | CRDs, operators, multi-namespace, network policies | Correctly tiered — optimize within AKS (node pool sizing, autoscaling) |
| ACA environment at resource ceiling | Hitting CPU/memory limits, needing DaemonSets or privileged access | Under-powered — candidate for AKS graduation |
| VM running a stateless HTTP service | No persistent state, no ISV license constraints | Strong candidate for ACA migration (eliminate patching, gain scale-to-zero) |

**Composite brownfield modernization path:**

```
VMs (assess) ──► AKS (modernize/orchestrate) ──► ACA (simplify/replatform)
     │                      │                              │
     │                      │                              │
     ▼                      ▼                              ▼
 Stay on VM            Stay on AKS                   Stay on ACA
 (legacy/HW/ISV)      (complex K8s needs)            (right-sized)
```

Each arrow represents an assessment decision, not an inevitable migration. Workloads move RIGHT only when the decision tree criteria warrant the destination tier. Many workloads will correctly remain at their current tier.

## Scenario Mapping

| Scenario | Code | Recommended Tier(s) | Rationale |
|----------|------|---------------------|-----------|
| Identity Platform | S1 | VMs (AD DS domain controllers) + AKS (identity microservices) | Domain controllers require bare-OS; identity APIs benefit from K8s native service mesh and pod identity |
| AI/ML Platform | S2 | AKS (GPU node pools for inference/training) + ACA (API gateway, event triggers) | GPU scheduling requires node-level control; surrounding APIs are stateless |
| Regulated Industry (Healthcare/Finance) | S3 | VMs (Confidential VMs for HSM-bound workloads) + AKS (compliant containerized services) | Regulatory requirements for hardware attestation push some workloads to Confidential VMs; others containerize safely |
| ISV SaaS Platform | S5 | AKS (multi-tenant control plane) + ACA (per-tenant isolated workloads) | Control plane needs operator patterns and CRDs; tenant workloads benefit from ACA isolation and scale-to-zero |
| Hybrid Edge | S7 | AKS (Arc-enabled edge clusters) + VMs (on-premises legacy) | Arc-enabled AKS extends to edge; legacy on-premises workloads remain on VMs until containerized |
| Cloud-Native Modernization | S8 | ACA (new stateless services) + AKS (platform services needing K8s primitives) | Default to ACA for new services; graduate to AKS only when ACA criteria are insufficient |

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **AKS for a simple HTTP API** | Full cluster overhead (control plane, node pools, upgrades) for a workload that needs only an HTTP endpoint and autoscaling | Use ACA — managed ingress, scale-to-zero, zero cluster management |
| **ACA for a workload needing DaemonSets** | ACA has no DaemonSet equivalent; attempting per-node infrastructure via multiple apps creates fragile workarounds | Use AKS — DaemonSets are first-class Kubernetes primitives |
| **VMs in 2026 because the team didn't want to learn containers** | Organizational inertia is not an architecture criterion; VMs carry the highest operational burden per workload | Invest in container skills; start with ACA (lowest K8s barrier) before AKS |
| **Lift-and-shift to AKS without containerizing first** | Moving VM workloads into AKS without proper containerization creates "VMs in containers" — worst of both worlds | Containerize properly (12-factor alignment) before selecting orchestration tier |
| **Mixing tiers within a single workload boundary** | A single bounded context split across AKS and ACA creates deployment coupling, inconsistent observability, and complex networking | One tier per bounded context; split at service boundaries, not within them |
| **ACA for stateful workloads requiring stable network identity** | ACA replicas don't have stable hostnames or ordinal identity; StatefulSet semantics don't exist | Use AKS StatefulSets for databases, message brokers, and clustered middleware |
| **Selecting tier based on environment instead of workload** | "AKS for prod, ACA for dev" ignores that the workload's characteristics don't change between environments | Same tier in all environments; use SKU/scaling differences for cost optimization between dev and prod |

## Prerequisites and Caveats

The following cost and availability factors influence tier selection and must be surfaced during architecture assessment:

| Factor | Impact | Guidance |
|--------|--------|----------|
| AKS Long Term Support (LTS) | LTS tier is a paid add-on; budgets must account for it if selected | Note LTS pricing in cost estimates; Standard tier is the default assumption |
| Confidential VM regional availability | DCsv3/DCdsv3/ECsv5 SKUs are not available in all regions | Validate region availability before committing to Confidential VM architecture |
| ACA Workload Profile SKU availability | Dedicated workload profiles are GA but specific SKUs vary by region | Confirm desired SKU availability in target region during planning |
| GPU node pool quota | NC/ND-series VMs require explicit quota pre-provisioning (not default) | Submit quota increase requests during Step 4 (Planning); do not assume availability |
| Defender for Containers | Required for full AKS/ACA security posture; paid Defender plan | Include Defender plan cost in security architecture; note it's an add-on, not included |
| Defender for Servers | Required for full VM security posture; paid Defender plan | Same as above — budget explicitly |

## References

### Wave 2 SKILL.md Files (Authored After This ADR)

- [`.github/skills/azure-kubernetes-service/SKILL.md`](../../.github/skills/azure-kubernetes-service/SKILL.md) — AKS-specific architecture, networking modes, node pool design, operator patterns
- [`.github/skills/azure-container-apps/SKILL.md`](../../.github/skills/azure-container-apps/SKILL.md) — ACA-specific architecture, workload profiles, Dapr integration, revision management
- [`.github/skills/azure-virtual-machines/SKILL.md`](../../.github/skills/azure-virtual-machines/SKILL.md) — VM-specific architecture, image management, VMSS, Update Manager patterns

### Existing Skills (Cross-Referenced)

- [`.github/skills/azure-networking/SKILL.md`](../../.github/skills/azure-networking/SKILL.md) — Hub-spoke network design (AKS integrates with this for egress/ingress topology)
- [`.github/skills/azure-rbac/SKILL.md`](../../.github/skills/azure-rbac/SKILL.md) — RBAC patterns for VM operator access, AKS cluster-admin roles
- [`.github/skills/workload-identity-federation/SKILL.md`](../../.github/skills/workload-identity-federation/SKILL.md) — AKS workload identity (hard prereq); ACA managed identity; VM managed identity

### Microsoft Learn References

- [Choose an Azure compute service](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree) — Official compute decision tree
- [AKS Landing Zone Accelerator](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/app-platform/aks/landing-zone-accelerator) — CAF-aligned AKS deployment guidance
- [Azure Container Apps overview](https://learn.microsoft.com/en-us/azure/container-apps/overview) — ACA capabilities and constraints

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-18 | Linus | Initial ADR for Wave 2 skill authoring. Establishes canonical AKS/ACA/VM decision boundary referenced by all 3 Wave 2 SKILL.md files. |

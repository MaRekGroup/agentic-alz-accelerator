# ADR: Hybrid Onboarding Strategy (Arc-Enabled Servers vs Arc-Enabled Kubernetes)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-05-19 |
| **Decision Makers** | Linus (Architect), Yeselam (Sponsor) |
| **Related Skills** | `azure-arc-servers`, `azure-arc-kubernetes` (Wave 5), `azure-policy`, `azure-monitor`, `workload-identity-federation` (existing) |

## Context

Enterprise landing zones extend governance to resources inside the Azure subscription boundary — but many enterprises operate substantial fleets of on-premises servers and off-Azure Kubernetes clusters that remain invisible to the accelerator. Without hybrid projection, the Step 0 Assessor terminates at the Azure subscription edge, the Step 3.5 Warden assigns Azure Policy only to ARM-registered resources, and the Sentinel monitoring loop has no telemetry from non-Azure workloads. This blind spot is the defining gap in brownfield engagements: M&A acquisitions bring on-premises server estates (S6), modernization projects carry Kubernetes clusters in off-Azure environments (S8), and hub-spoke network extensions require connected non-Azure compute to participate in the same governance posture as native resources.

Azure Arc resolves this by projecting non-Azure resources into ARM as first-class objects — servers as `Microsoft.HybridCompute/machines`, Kubernetes clusters as `Microsoft.Kubernetes/connectedClusters`. Once projected, these resources become subject to the same Azure Policy, Resource Graph, Defender for Cloud, and Monitor infrastructure already established for native Azure resources. This ADR establishes the canonical decision boundary between `azure-arc-servers` and `azure-arc-kubernetes`, defines when Arc is the right governance extension versus native Azure migration, and locks the onboarding sequence model referenced by both Wave 5 SKILL.md files.

**Arc data services (SQL Managed Instance on Arc, PostgreSQL on Arc) are explicitly out of scope.** No current accelerator customer profile maps to Arc-hosted managed data services. They are a potential future post-catalog addition — not a Wave 6 micro-wave. The skill catalog is final at 14.

## Connect to Arc When

### Arc-Enabled Servers (`azure-arc-servers`)

| Criterion | Rationale |
|-----------|-----------|
| On-premises or multi-cloud VMs must participate in Azure Policy and Resource Graph | Arc projection makes them first-class ARM resources subject to the same governance as native VMs (CAF: Governance, Management) |
| Guest configuration / machine configuration policy enforcement required on non-Azure hosts | `Microsoft.HybridCompute/machines` supports guest config assignments via Azure Policy; no equivalent exists without Arc (CAF: Security) |
| Defender for Servers Plan 2 coverage needed for non-Azure hosts | Defender requires Arc enrollment for non-Azure servers — Arc is the mandatory enrollment layer (WAF: Security) |
| Azure Monitor AMA or Update Manager patch compliance required at hybrid scale | AMA extension and Update Manager deploy centrally to Arc-enrolled servers; unenrolled servers are unmanageable from Azure (WAF: Operational Excellence) |
| Brownfield hybrid estate inventory must surface in Step 0 Assessor KQL collectors | Arc-enrolled servers appear in Resource Graph; unenrolled servers are invisible to the Assessor discovery queries (CAF: Management) |

### Arc-Enabled Kubernetes (`azure-arc-kubernetes`)

| Criterion | Rationale |
|-----------|-----------|
| Off-Azure K8s clusters require GitOps-driven configuration management | Flux v2 via Arc K8s extension applies the same patterns used on AKS to any CNCF-conformant cluster (CAF: Platform Automation) |
| Azure Policy constraint templates required on non-AKS clusters | OPA Gatekeeper constraint templates enforce pod security standards on Arc-connected clusters; not deployable without Arc (CAF: Governance) |
| Defender for Containers or Container Insights required for off-Azure clusters | Both deploy as Arc cluster extensions; not available on clusters without Arc enrollment (WAF: Security, Operational Excellence) |
| Workload identity via OIDC issuer needed on off-Azure cluster workloads | Arc K8s OIDC issuer extension enables service account token projection compatible with `workload-identity-federation` patterns (WAF: Security) |
| Brownfield K8s fleet governance required across heterogeneous environments | Arc unifies governance across EKS, GKE, on-prem clusters, and edge devices under a single Policy + Monitor surface (CAF: Governance) |

## Migrate to Azure When

| Criterion | Signal | Recommended Path |
|-----------|--------|-----------------|
| On-premises VMs have no long-term hardware or regulatory residency justification | Lease/licensing renewal within 24 months; no sovereign residency mandate | Lift to Azure VMs (`azure-virtual-machines`); Arc adds management overhead without migration value |
| Off-Azure K8s cluster is a single-tenant workload with no edge or sovereignty requirement | No regulation forces off-Azure compute; Azure-native networking preferred | Migrate to AKS (`azure-kubernetes-service`); Arc adds connectivity complexity for a cluster Azure can host natively |
| Arc connectivity investment equals or exceeds migration cost | ExpressRoute / VPN provisioning cost exceeds re-platform cost on TCO analysis | Re-platform to Azure-native; do not Arc-enable to avoid connectivity investment migration also requires |
| Regulatory boundary prohibits cloud control-plane registration | Air-gapped environments that legally cannot reach Azure Resource Manager endpoints | Arc not permitted; governance must remain on-premises via on-prem tooling |

## Onboarding Sequence Model

**Default credential pattern: Managed Identity via Azure Automation Hybrid Runbook Worker (MI-first).** This is the non-negotiable default, aligned with Security Baseline Rule #4 (Managed Identity preferred). It eliminates service principal secret rotation risk and credentials stored in pipelines. Service principal with `Azure Connected Machine Onboarding` role scoped to the target subscription is the fallback ONLY when the environment cannot reach a Hybrid Runbook Worker (e.g., isolated legacy on-premises environments predating HRW support). Both skill brownfield playbooks carry ⛔ HARD GATE annotations at the credential-scoping step — see each SKILL.md for gate details.

| Phase | Activity | Arc Servers | Arc K8s | Gate |
|-------|----------|-------------|---------|------|
| 1. Assess | Inventory resources; confirm connectivity prerequisites | Resource Graph + CMDB cross-reference | Cluster CMDB cross-reference | — |
| 2. Identity | Establish MI or SP credential at minimum required scope | `Azure Connected Machine Onboarding` role | Cluster-admin or equivalent | ⛔ Credential scope (both) |
| 3. Connectivity | Confirm outbound HTTPS to Arc endpoints; proxy / private-endpoint path if required | Port 443 to Arc endpoints | Port 443 to Arc endpoints | — |
| 4. Onboard | Execute onboarding at scale | `azcmagent` / portal deployment scripts | `az connectedk8s connect` helm install | ⛔ Arc agent helm install (K8s) |
| 5. Policy | Assign guest config (servers) or Flux + constraint templates (K8s); audit before deny | Machine config policy at MG scope | Azure Policy initiative + Flux v2 GitOps | — |
| 6. Monitor | Deploy AMA + Defender extensions; validate posture via Resource Graph and Defender score | AMA → MDE → Dependency Agent | Container Insights → Defender → OIDC issuer | ⛔ Extension removal (both) |

Greenfield hybrid estates follow the same sequence at day 0 rather than retrofitting. The Arc-vs-migrate decision tree (§3–§4) must be re-evaluated for every workload before Phase 4 — Arc onboarding is additive to the ARM namespace but disconnection requires explicit steps and namespace cleanup.

## WAF Trade-Off Matrix

| WAF Pillar | Arc-Enabled Servers | Arc-Enabled Kubernetes | Re-Platform to Azure-Native |
|------------|---------------------|----------------------|-----------------------------|
| **Reliability** | Desired-state via guest config; Update Manager maintains patch compliance. No Azure SLA on the underlying host hardware. | Flux v2 reconciliation enforces desired state. Cluster availability is customer-managed; Arc control-plane carries 99.9% SLA for the projection layer only. | Full Azure SLA coverage; zone-redundancy, availability sets, and AKS node pool auto-repair available. Highest reliability ceiling for the combined projection and compute layers. |
| **Security** | Defender for Servers P2, MDE, and guest config baselines bring Azure security posture to on-prem. MI-first credential default eliminates SP secret leakage risk at scale. | Defender for Containers, OIDC WIF, and constraint templates extend K8s security controls to off-Azure clusters. OIDC issuer enablement is irrevocable — HARD GATE enforced in SKILL.md. | Full security baseline enforcement with no connectivity dependency on customer premises. Private endpoints, managed identity, and Entra-only auth apply natively. |
| **Cost Optimization** | Arc control plane and extensions are free; Defender for Servers P2 billed per server/month. On-premises hardware and DC costs remain with the customer. | Arc control plane is free; Container Insights and Defender for Containers billed per node. On-premises cluster infrastructure cost remains with the customer. | Eliminates on-premises hardware and DC costs; replaces with Azure VM / AKS compute cost. Reservation pricing (1/3-year) reduces compute cost 30–65%. TCO analysis required per workload. |
| **Performance Efficiency** | Arc is control-plane only — no impact on workload data path. Telemetry upload to Arc endpoints is background, not in-path. | Arc control plane is out-of-band; GitOps pull-based reconciliation is asynchronous. Cluster networking and compute performance determined by on-premises infrastructure. | Full Azure performance primitives: Accelerated Networking, Ultra Disk, HBv3 compute, VMSS autoscale, KEDA on AKS. Performance ceiling determined by Azure SKU selection. |
| **Operational Excellence** | Single pane of glass for hybrid inventory via Resource Graph and Azure Portal. AMA unifies logging. Update Manager centralizes patch compliance. Agent version drift is an ongoing operational responsibility. | GitOps provides declarative desired-state visibility and drift detection per cluster. Multi-cluster fleet governance at scale. Flux reconciliation logs feed into Azure Monitor. | Eliminates hybrid connectivity management overhead. Full GitHub Actions / Azure DevOps pipeline integration. Azure Automation and Update Manager apply natively without Arc agent hygiene burden. |

## Anti-Patterns

**Vanity Arc onboarding ("hybrid checkbox").** Connecting servers or clusters to Arc without consuming any governance capabilities — no policy assignments, no monitoring extensions, no Defender enrollment — produces Arc projection with zero enforcement value. The resource appears in compliance dashboards as covered but delivers nothing. Every Arc-enrolled resource should have at minimum one active policy assignment and one monitoring extension within 30 days of enrollment. Resources enrolled without consuming governance primitives should be remediated or decommissioned.

**Credential proliferation via per-resource service principals.** Creating a dedicated SP per onboarding batch or per server group generates a secret management burden that negates Arc's security benefit. The MI-first default via Azure Automation Hybrid Runbook Worker eliminates per-resource credentials entirely. When SP fallback is required, a single SP scoped to the target subscription or resource group is the maximum — never per-server or per-cluster SPs.

**Policy fragmentation between Arc and native resources.** Assigning different policy sets to Arc-enrolled resources versus native Azure resources within the same MG creates a bifurcated compliance posture the Warden and Sentinel cannot evaluate consistently. Arc-enrolled resources inherit MG-scoped policy assignments the same way native resources do. Arc-specific additions (guest config, constraint templates) should be additive policy, not substitutive policy.

**Agent drift on long-lived Arc machines.** Arc agent versions (`azcmagent`, Arc K8s Helm chart) require active version management. Machines enrolled once and never updated accumulate version debt that breaks extension compatibility and telemetry pipelines. Update Manager surfaces stale agent alerts for Arc servers; the Arc K8s operator exposes extension version states in the cluster's Azure resource object. Both must be included in the operational runbook and tracked in the Sentinel monitoring baseline.

**Governance bypass via Arc exemptions on high-risk legacy resources.** Some teams connect resources to Arc for Resource Graph inventory visibility while applying open-ended policy exemptions to exclude the highest-risk legacy machines from enforcement. This creates the appearance of hybrid coverage while exempting the resources that most need policy controls. Policy exemptions on Arc-enrolled production resources require explicit justification and time-bound scope — open-ended exemptions are a governance bypass pattern the Challenger flags at Gate 2.

## Scenario Mapping

| Scenario | Code | Arc-Servers Role | Arc-K8s Role | Key Constraint |
|----------|------|-----------------|-------------|----------------|
| Hybrid Estate Governance | S6 | **Primary** — onboards existing on-premises server fleet; enables Defender for Servers P2, machine config baselines, Update Manager, and Resource Graph visibility across the full estate | Supporting — off-Azure clusters in the estate connect for Policy + Monitor; Flux not required if cluster config is managed by existing on-premises tooling | MI-first credential default required; ⛔ HARD GATE on credential scope before at-scale onboarding |
| Brownfield K8s Fleet | S8 | Supporting — on-premises compute hosting cluster nodes may also enroll for host-level governance (Defender for Servers on the node VMs) | **Primary** — connects heterogeneous K8s clusters (EKS, GKE, RKE, on-prem) to unified GitOps + Policy + Monitor surface; Flux v2 provides desired-state fleet management | OIDC issuer ⛔ HARD GATE requires workload team coordination before prod enablement; AKS skill (W2) is hard prereq for Flux v2 reference patterns |
| Brownfield M&A Integration | S4 | Supporting — acquired company's on-premises servers enrolled in acquirer's Azure governance; feeds MG restructuring defined in `management-group-architecture` | Supporting — acquired company's off-Azure clusters connected to acquirer's Arc fleet; policy alignment phased per MG hierarchy migration schedule | Sequence: MG hierarchy established first (`billing-tenant-hierarchy.md` ADR) before Arc onboarding assigns governance scope |

## References

### Wave 5 SKILL.md Files (Authored After This ADR)

- `.github/skills/azure-arc-servers/SKILL.md` — Arc-enabled server onboarding, guest config, extensions, Defender for Servers P2, Update Manager, brownfield S6 playbook
- `.github/skills/azure-arc-kubernetes/SKILL.md` — Arc-enabled K8s connection, Flux v2 GitOps, constraint templates, OIDC issuer, Defender for Containers, brownfield S8 playbook

### Existing Skills (Cross-Referenced)

- [`.github/skills/azure-policy/SKILL.md`](../../.github/skills/azure-policy/SKILL.md) — Guest config policy authoring and constraint template syntax (hard prereq for both Arc skills)
- [`.github/skills/azure-monitor/SKILL.md`](../../.github/skills/azure-monitor/SKILL.md) — AMA deployment and Container Insights for Arc-enrolled resources
- [`.github/skills/workload-identity-federation/SKILL.md`](../../.github/skills/workload-identity-federation/SKILL.md) — OIDC issuer and service account token projection (Arc K8s WIF prerequisite)
- [`.github/skills/azure-kubernetes-service/SKILL.md`](../../.github/skills/azure-kubernetes-service/SKILL.md) — Flux v2 GitOps reference patterns (hard prereq for Arc K8s)

### Prior ADRs

- [`docs/decisions/compute-tier-selection.md`](./compute-tier-selection.md) — Wave 2: Arc K8s does not substitute for AKS when Azure-native hosting is available
- [`docs/decisions/billing-tenant-hierarchy.md`](./billing-tenant-hierarchy.md) — Wave 3: MG hierarchy must be established before Arc policy scope is assigned (S4 sequencing dependency)
- [`docs/decisions/data-tier-selection.md`](./data-tier-selection.md) — Wave 4: Arc data services (SQL MI / PostgreSQL on Arc) explicitly excluded from Wave 5 scope per this ADR

### Microsoft Learn References

- [Azure Arc-enabled servers overview](https://learn.microsoft.com/azure/azure-arc/servers/overview) — Connected Machine agent, supported OS, Arc server lifecycle
- [Azure Arc-enabled Kubernetes overview](https://learn.microsoft.com/azure/azure-arc/kubernetes/overview) — Cluster connection, extensions, GitOps, supported distributions
- [Connected Machine agent deployment options](https://learn.microsoft.com/azure/azure-arc/servers/deployment-options) — At-scale onboarding, Automation Hybrid Worker, deployment scripts
- [Azure Policy machine configuration overview](https://learn.microsoft.com/azure/governance/machine-configuration/overview) — Guest config / machine configuration policy authoring and assignment for Arc servers
- [Flux v2 GitOps on Arc-enabled Kubernetes](https://learn.microsoft.com/azure/azure-arc/kubernetes/conceptual-gitops-flux2) — GitOps bootstrap, Flux v2 extension, kustomization targets
- [Azure Monitor Agent management](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage) — AMA extension installation and data collection rules for Arc-enrolled servers

> **Downstream catalog update (Yeselam Q5):** When Wave 5 ships, `AGENTS.md` and `.github/copilot-instructions.md` receive a new **"Hybrid"** section for `azure-arc-servers` and `azure-arc-kubernetes`. This is a Scribe responsibility at PR time — not part of this ADR.

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-19 | Linus | v1.0 — Initial publication (Linus-8, Wave 5). Establishes canonical Arc-Enabled Servers vs Arc-Enabled Kubernetes decision boundary, MI-first credential default, and onboarding sequence model. Referenced by both W5 SKILL.md files. |

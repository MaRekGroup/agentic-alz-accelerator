---
name: azure-virtual-machines
description: "VM availability architecture, security hardening, and compute governance for Azure Landing Zones. USE FOR: VM zone strategy (VMSS Flex, availability sets legacy), VM SKU selection, accelerated networking, proximity placement groups, Trusted Launch, Confidential VMs, Azure Dedicated Host, OS disk encryption (PMK/CMK/DES), VM extensions strategy, Azure Compute Gallery, managed identity for VMs, Update Manager integration awareness, and VM backup/DR integration points. DO NOT USE FOR: AKS node pool VMs (use azure-kubernetes-service), VM networking NSGs/UDRs (use azure-virtual-network), Azure Backup vault configuration (use azure-backup), Azure Site Recovery replication setup (use azure-site-recovery), Azure Bastion connection setup (use azure-bastion), Azure Monitor agent configuration (use azure-monitor), or workload identity federation (use workload-identity-federation)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: saul
  version: "1.0"
  category: azure-compute
---

# Azure Virtual Machines Skill

## Overview

Virtual Machines remain the dominant compute tier in enterprise Azure estates and the entry point for most brownfield assessments. This skill covers VM availability architecture, security hardening, SKU governance, and lifecycle management — from zone-redundant VMSS Flex through Trusted Launch, Confidential VMs, OS disk encryption with customer-managed keys, managed identity enablement, and Azure Compute Gallery.

Before applying this skill, confirm with `docs/decisions/compute-tier-selection.md` that a VM tier is the correct choice. Container-ready workloads should graduate to `azure-kubernetes-service` or `azure-container-apps` instead; this skill classifies the estate and executes the handoff, but does not architect the container landing.

## Boundary

### USE FOR

- VM availability architecture: zone-redundant VMSS Flex (recommended), availability sets (legacy brownfield only), fault domain control
- Proximity placement groups for low-latency co-location and HPC workloads
- Accelerated networking enablement and multi-NIC configuration patterns
- VM SKU selection guidance: right-sizing, reserved instances, Spot VMs, GPU/HPC families (NC/ND-series)
- Trusted Launch (Secure Boot, vTPM, Integrity Monitoring) for Gen2 VMs
- Confidential VMs (DCsv3, DCdsv3, ECsv5, ECdsv5) with AMD SEV-SNP or Intel SGX attestation
- Azure Dedicated Host — physical isolation for compliance mandates and per-VM ISV licensing
- OS disk encryption: Platform-Managed Keys (PMK), Customer-Managed Keys (CMK via Key Vault), Disk Encryption Sets (DES)
- VM extensions strategy (dependency agent, custom script extension, Azure Monitor Agent awareness)
- Azure Compute Gallery for golden image management, versioning, and cross-subscription sharing
- Managed identity (SystemAssigned) for VM workloads — Security Baseline rule #4
- Update Manager integration awareness and maintenance window design
- VM backup and DR integration points (awareness only — defer vault config and ASR replication setup to dedicated skills)

### DO NOT USE FOR

- AKS node pool VMs → use `azure-kubernetes-service`
- VM networking: NSGs, UDRs, NIC-level filtering → use `azure-virtual-network`
- Azure Backup vault configuration and policy assignment → use `azure-backup` (future skill)
- Azure Site Recovery replication, failover, and test failover → use `azure-site-recovery` (future skill)
- Remote access via Azure Bastion host → use `azure-bastion`
- Azure Monitor Agent installation and data collection rules → use `azure-monitor` (future skill)
- Workload identity federation for service-to-service auth → use `workload-identity-federation`
- RBAC role assignments at VM or resource group scope → use `azure-rbac`

> **Compute tier selection:** Confirm VM is the right tier before proceeding.
> See `docs/decisions/compute-tier-selection.md` for the canonical AKS vs. Azure Container Apps vs. VM decision tree.

## CAF Design Area Alignment

| CAF Design Area | Priority | VM contribution |
|-----------------|----------|-----------------|
| **Security** | **Primary** | Trusted Launch (Secure Boot, vTPM), Confidential VMs with hardware attestation, OS disk encryption (PMK/CMK/DES), host-level isolation via Dedicated Host, Defender for Servers integration |
| **Identity & Access** | **Primary** | System-assigned managed identity (Security Baseline rule #4), RBAC for VM operators, JIT VM access via Defender for Cloud (paid), Key Vault integration for CMK disk encryption keys |
| Network Topology & Connectivity | Secondary | Accelerated networking enablement, proximity placement groups for latency-sensitive workloads, multi-NIC configuration, private IP assignment strategy |
| Management | Secondary | Update Manager maintenance windows, VM extensions lifecycle governance, Azure Compute Gallery image versioning, monitoring agent strategy, maintenance control configuration |

## WAF Pillar Mapping

| WAF Pillar | Priority | Why it matters |
|------------|----------|----------------|
| **Reliability** | **Primary** | Zone-redundant VMSS Flex eliminates single-zone failures; fault domain and update domain planning determine blast radius; ASR integration enables cross-region DR with defined RPO/RTO |
| **Security** | **Primary** | Trusted Launch hardens the boot chain; CMK disk encryption satisfies regulatory audit requirements; Confidential VMs provide hardware-backed memory encryption for sensitive regulated workloads |
| Performance Efficiency | Secondary | SKU right-sizing avoids over-provisioned waste; proximity placement groups and accelerated networking minimize east-west latency; ephemeral OS disks reduce IOPS bottlenecks for stateless VMs |
| Cost Optimization | Secondary | Right-sizing via Advisor + 90-day utilization data; reserved instances post-stabilization; Spot VMs for fault-tolerant batch workloads; VMSS scale-in policy alignment to avoid idle instances |

## Scenarios Unblocked

- **S2 (Multi-Region AI Platform):** Cannot architect GPU VM pools (NC/ND-series) for model training or inference without VM zone strategy, proximity placement group configuration, and accelerated networking guidance.
- **S3 (Regulated Workloads):** Cannot deliver Confidential VMs (DCsv3/ECsv5) or Azure Dedicated Host for HIPAA/FedRAMP compliance without this skill. CMK disk encryption with a customer-controlled audit trail is mandatory — PMK alone does not satisfy regulated attestation requirements.
- **S5 (ISV Multi-Tenant SaaS):** Cannot design per-tenant VM isolation, VMSS stamp patterns, or Dedicated Host placement for ISV licensing compliance without VM availability architecture guidance.
- **S7 (Hybrid Edge):** Cannot architect Azure Stack HCI VM placement or guide the VM-to-container migration path for edge-to-cloud modernization scenarios.
- **S8 (Cloud-Native Modernization):** Cannot assess existing VMs for containerization readiness — the "lift and shift" starting point. This skill classifies the estate; `azure-kubernetes-service` or `azure-container-apps` handles the graduation path.

## Architecture Patterns

### 1. Zone-Redundant VMSS Flex (Default for New Workloads)

| Element | Guidance |
|---------|----------|
| Use when | New production deployments with ≥2 instances; all multi-region AI, SaaS, and regulated scenarios |
| Topology | VMSS Flex with `platformFaultDomainCount: 1` and `zones: ['1', '2', '3']`; prefer zone spanning over availability sets for all new deployments |
| Orchestration mode | Use **Flexible** (not Uniform); supports individual VM management, mixed instance types, and Spot mixing |
| Load balancing | Pair with Standard Load Balancer (zone-redundant SKU); never use Basic LB with zonal VMSS |
| Legacy guidance | Availability sets remain valid only for brownfield workloads that cannot yet migrate; they provide no cross-zone protection and have no future investment from Microsoft |

**Bicep: VMSS Flex with zone spanning**

```bicep
resource vmss 'Microsoft.Compute/virtualMachineScaleSets@2023-09-01' = {
  name: 'vmss-${workloadName}-flex'
  location: location
  zones: ['1', '2', '3']
  sku: { name: skuName, tier: 'Standard', capacity: instanceCount }
  properties: {
    orchestrationMode: 'Flexible'
    platformFaultDomainCount: 1
    virtualMachineProfile: {
      storageProfile: {
        osDisk: { createOption: 'FromImage', managedDisk: { storageAccountType: 'Premium_LRS' } }
      }
      networkProfile: { networkApiVersion: '2020-11-01' }
    }
  }
}
```

### 2. Trusted Launch and Secure Boot (Gen2 VMs)

| Element | Guidance |
|---------|----------|
| Prerequisite | **Gen2 VM image only.** Gen1 VMs cannot enable Trusted Launch — they must be migrated to Gen2 first. |
| Capabilities | Enables Secure Boot, vTPM, and Integrity Monitoring via Defender for Cloud |
| Default | Enable on all new Gen2 production VMs; disable only with explicit documented justification |
| Attestation path | vTPM provides boot-chain measurements required by Confidential VMs for remote attestation (DCsv3/ECsv5) |

**Bicep: Trusted Launch configuration**

```bicep
securityProfile: {
  securityType: 'TrustedLaunch'
  uefiSettings: {
    secureBootEnabled: true
    vTpmEnabled: true
  }
}
```

### 3. Confidential VMs (Regulated Workloads)

Confidential VMs use AMD SEV-SNP or Intel SGX to provide hardware-based memory encryption and remote attestation. Use for regulated workloads requiring cryptographic proof of the execution environment — HIPAA, FedRAMP High, and financial confidentiality use cases.

| Decision point | Guidance |
|----------------|----------|
| SKU selection | DCsv3/DCdsv3 for SGX enclave workloads; ECsv5/ECdsv5 for SEV-SNP full-VM memory encryption |
| Regional check | **Not available in all Azure regions.** Verify the current availability matrix before architecting. See Prerequisites. |
| Attestation | Pair with Microsoft Azure Attestation (MAA) for remote attestation in regulated pipelines |
| Disk encryption | Confidential OS disk encryption with CMK is recommended — PMK does not satisfy FedRAMP/HIPAA CMK mandate |

### 4. OS Disk Encryption: PMK → CMK → DES

| Level | When to use | Compliance posture |
|-------|-------------|-------------------|
| Platform-Managed Keys (PMK) | Dev/test environments only | Audit trail is Microsoft-controlled; insufficient for regulated frameworks |
| Customer-Managed Keys (CMK) | All production and regulated workloads | Customer controls Key Vault lifecycle; provides audit trail for HIPAA, FedRAMP, PCI-DSS |
| Disk Encryption Sets (DES) | CMK at fleet scale | Centralizes CMK association; pairs with Key Vault or Managed HSM for enterprise key governance |

**Bicep: CMK disk encryption via Disk Encryption Set**

```bicep
resource des 'Microsoft.Compute/diskEncryptionSets@2023-01-02' = {
  name: 'des-${workloadName}'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    activeKey: { sourceVault: { id: keyVaultId }, keyUrl: keyUrl }
    encryptionType: 'EncryptionAtRestWithCustomerKey'
    rotationToLatestKeyVersionEnabled: true
  }
}
```

### 5. Azure Dedicated Host (Physical Isolation)

Azure Dedicated Host reserves a physical Azure server for a single customer's exclusive use. Required when workloads need regulatory-grade physical isolation attestation, per-VM ISV licensing with host affinity, or fine-grained maintenance window control (no unplanned host updates).

| Consideration | Guidance |
|---------------|----------|
| SKU eligibility | Not all VM SKUs are eligible for Dedicated Host; map your required VM family to a supported host SKU before committing |
| Billing model | Billed per host regardless of VM density — maximize VM packing to contain cost |
| Capacity reservation | Pair with Capacity Reservations for guaranteed capacity on regulated SLA-bearing workloads |
| HA model | Spread hosts across fault domains (`platformFaultDomainCount ≥ 2`); pair with VMSS Flex or multi-zone VM placement |

### 6. Azure Compute Gallery (Golden Image Management)

| Element | Guidance |
|---------|----------|
| Purpose | Version-controlled VM images shared across subscriptions and regions |
| Image definition | Capture security-hardened baseline: OS security updates, monitoring agents, compliance tooling, Trusted Launch enabled |
| Replication | Replicate to each deployment region; target replica count ≥ 3 per production region to avoid throttle on parallel deployments |
| Lifecycle | Tie image deprecation to Update Manager patch baseline; retire old versions after all VMs migrate forward |

### 7. Managed Identity for VMs (Security Baseline Rule #4)

All production VMs must be assigned a **SystemAssigned managed identity**. Managed identity eliminates credential-bearing code, satisfies Security Baseline rule #4, and is the required authentication mechanism for CMK Key Vault access, storage auth, and internal service tokens. For cross-resource access patterns that outlive a single VM lifecycle, use UserAssigned managed identity.

```bicep
identity: {
  type: 'SystemAssigned'
}
```

## Security Baseline Reinforcement

This skill enforces the following non-negotiable security baseline rules in the VM context:

| Rule | VM enforcement |
|------|----------------|
| **Rule #4: Managed Identity preferred** | Every production VM must have `identity.type: 'SystemAssigned'`. Eliminates stored credentials and enables Key Vault CMK access, storage auth, and internal service tokens without secret management. |
| **Rule #6: Public network disabled (prod)** | Production VMs must not have public IPs. Route all operator access through `azure-bastion` or JIT VM access (Defender for Servers Plan 2). Enforce via Azure Policy. |
| **Rule #1: TLS 1.2 minimum** | Enforce via OS hardening baseline or VM extensions; applies to any VM-hosted web service or API endpoint. Pair with Application Gateway or Load Balancer TLS offload where applicable. |
| **Rule #2: HTTPS-only** | Enforce at application and OS layer for any VM-hosted service; no unencrypted HTTP listener in production environments. |

> **JIT VM Access:** When Defender for Servers Plan 2 is enabled, JIT VM access replaces always-open management ports (22/3389). Requests are approved per-session, time-bounded, and source-IP scoped. This is the recommended operator access pattern when Azure Bastion is not deployed.

## Anti-Patterns

### 1. Availability Sets for New Deployments

Availability sets distribute VMs across fault and update domains within a **single datacenter** — they provide no cross-zone protection whatsoever. New workloads that use availability sets instead of zone-redundant VMSS Flex are architecturally equivalent to single-zone deployments for the purposes of zone-level failure scenarios. Availability sets are a compatibility bridge for brownfield workloads already deployed under that model; they must not be the default for any new landing zone deployment. Corrective action: deploy all new workloads with VMSS Flex, `zones: ['1', '2', '3']`, and `orchestrationMode: 'Flexible'`.

### 2. Single-Instance VM in Production

A single VM has no SLA guarantee from Microsoft and represents a single point of failure for every workload running on it. Single-instance VMs are acceptable in dev/test environments and non-critical internal tooling, but must never back production workloads, compliance-facing systems, or any service with an uptime or availability requirement. The absence of a published SLA is a contract-level gap, not just a best-practice concern. Corrective action: deploy a minimum of two instances across two availability zones using VMSS Flex, or a zone-balanced VM pair behind a Standard Load Balancer (zone-redundant SKU).

### 3. Platform-Managed Keys for Regulated Workloads

PMK encryption is Microsoft-controlled: Microsoft holds the key, manages rotation, and owns the audit trail. This is insufficient for HIPAA, FedRAMP, PCI-DSS, and most financial regulatory frameworks, which require the customer to control encryption keys, manage their own rotation lifecycle, and produce their own audit evidence from Key Vault diagnostic logs. Organizations that select PMK for regulated workloads discover this gap at their first compliance audit. Corrective action: implement CMK via a customer-owned Key Vault with Disk Encryption Sets; enable `rotationToLatestKeyVersionEnabled: true`; configure Key Vault diagnostic logs routed to Log Analytics as the compliance audit trail.

### 4. Gen1 VMs in 2026

Gen1 VMs cannot enable Trusted Launch, Secure Boot, or vTPM — these capabilities require UEFI firmware, which Gen1 images do not expose. Running Gen1 images in 2026 means the boot chain is unprotected, firmware-level attestation is unavailable, and the Security Baseline cannot be fully enforced at the VM layer. This is not a neutral legacy default; it is an active security gap. Corrective action: identify all Gen1 VMs via Azure Resource Graph, validate application compatibility against a Gen2 image in a non-production environment, and schedule migration to Gen2. Enable Trusted Launch immediately after migration.

### 5. Over-Sized SKU "Just in Case"

Deploying larger SKUs than workload demand justifies is the most common and most expensive VM governance failure in enterprise estates. Over-provisioning wastes compute budget, inflates reserved instance commitments, and produces misleading utilization baselines that compound across the estate at scale. "Just in case" capacity should be handled by VMSS autoscale policies, not by SKU inflation at deployment time. Corrective action: export 90-day CPU, memory, and network utilization data from Azure Advisor right-sizing recommendations; apply the Advisor-recommended SKU in a staged rollout; purchase reserved instances only after a minimum 30-day post-right-sizing stabilization window confirms the new baseline.

## Brownfield Scenario (Scenario S3: Regulated Workloads)

*Right-size existing VMs using Advisor data, zone-balance unprotected workloads, enable Trusted Launch on Gen2-compatible VMs, and enforce OS disk encryption with customer-managed keys (CMK via Key Vault) to meet regulatory compliance baselines.*

**Cross-skill sequencing:** Run after Wave 1 identity hardening is complete. Assess VM estate for zone-balancing, right-sizing, and containerization readiness. Hand off container-ready workloads to `azure-kubernetes-service` or `azure-container-apps` based on complexity (see `docs/decisions/compute-tier-selection.md`).

### Pre-Migration Discovery Checklist

| Discovery area | What to inventory | Why it matters |
|----------------|-------------------|----------------|
| Generation status | Count Gen1 vs. Gen2 VMs per subscription; tag all Gen1 VMs for migration tracking | Gen1 VMs block Trusted Launch — must be migrated before security baseline enforcement |
| Encryption posture | Identify PMK-only VMs in regulated subscriptions; map existing CMK associations | PMK fails HIPAA/FedRAMP CMK requirements; these are compliance blockers |
| Zone distribution | Map VMs to availability zones; flag single-zone and non-zonal VMs by workload tier | Unzoned VMs have no SLA; zone distribution drives blast-radius and DR analysis |
| SKU sprawl | Export Advisor right-sizing recommendations; identify over-provisioned SKUs vs. workload baselines | Right-sizing must precede reserved instance purchase to avoid locking in waste |
| Dedicated Host candidates | Identify workloads requiring physical isolation attestation or ISV host-affinity licensing | Dedicated Host capacity commitment must be planned before migration waves start |
| Managed identity gaps | List VMs without SystemAssigned managed identity; identify any using stored credentials | Security Baseline rule #4 — any VM using stored credentials must be remediated |
| Public IP exposure | List VMs with public IPs in production subscriptions; map to Bastion or JIT coverage | Security Baseline rule #6 violation; public IPs must be removed |
| Update Manager enrollment | Check VMs enrolled in maintenance windows vs. those in unmanaged patch state | Unmanaged patching creates compliance and availability risk; must be remediated before go-live |
| Containerization readiness | Classify VMs against `docs/decisions/compute-tier-selection.md` criteria | Container-ready workloads should graduate — document handoff candidates before migration waves |

### Staged Rollout Playbook

| Step | Action | Exit criteria | Rollback gate |
|------|--------|---------------|---------------|
| 1 | **Establish inventory baseline.** Run Resource Graph query to classify all VMs by generation, encryption type, zone placement, SKU, managed identity status, and public IP exposure. Tag all findings. | Full inventory complete with generation and encryption classification; all findings tagged | If Resource Graph access is unavailable, halt until RBAC grants Reader access to all target subscriptions |
| 2 | **Remove public IPs from production VMs.** Validate Bastion or JIT VM access for all affected VMs before removal. Remove public IPs after access-path confirmation. | Zero public IPs on production VMs; Bastion or JIT confirmed for all operator access paths | If a workload breaks after public IP removal, restore the IP and open a tracked exception; do not proceed until access path is confirmed |
| 3 | **Assign managed identity to all VMs.** Enable SystemAssigned on every VM lacking it. Update Key Vault access policies or RBAC to accept VM identity tokens where CMK is planned next. | 100% managed identity coverage on production VMs | If identity assignment fails (policy conflict, SKU limitation, quota), remediate the blocker before proceeding |
| 4 | **Right-size over-provisioned VMs.** Apply Advisor recommendations in waves: dev/test first, then non-critical production, then business-critical. Validate CPU and memory headroom post-resize before advancing each wave. | Advisor recommendation coverage reduced; no application SLA breach observed post-resize | Retain original SKU as a resize rollback option for 7 days; revert immediately if performance SLA degrades |
| 5 | **Migrate Gen1 VMs to Gen2.** Pilot with non-critical workloads. Test application compatibility under Gen2 images in a staging environment before production migration waves. | All Gen1 VMs in regulated subscriptions migrated, or documented exception with remediation deadline | If application fails under Gen2, keep Gen1 with a tracked exception; escalate to app owner for compatibility fix before rescheduling |
| 6 | **Enable Trusted Launch on Gen2 VMs.** Enable Secure Boot and vTPM after Gen2 migration. Validate Integrity Monitoring alert baseline captured in Defender for Cloud before advancing. | Trusted Launch enabled on all Gen2 production VMs; Integrity Monitoring baseline captured | If Secure Boot blocks an unsigned driver or boot component, disable Secure Boot and file a tracked exception with a remediation timeline |
| 7 | **Enforce CMK disk encryption via Disk Encryption Sets.** Create DES per subscription or workload tier. Associate with customer Key Vault (Key Vault diagnostic logs enabled). Migrate PMK disks to CMK by re-encryption. | Zero PMK VMs in regulated subscriptions; DES associations verified; Key Vault diagnostic logs confirm audit trail | If DES association fails (Key Vault soft-delete state, access policy gap), restore PMK association and fix Key Vault before retrying |
| 8 | **Enroll in Update Manager and zone-balance.** Enroll all VMs in Update Manager maintenance windows. Identify non-zonal VMs and schedule redeployment to zonal or VMSS Flex. Perform final Defender for Cloud Secure Score delta scan. | All VMs under maintenance control; zone coverage documented; Secure Score improvement confirmed against pre-assessment baseline | No automatic rollback for zone redeployment — plan application downtime window and validate failover path before executing redeployment |

### Container-Ready Workload Handoff

During discovery (Step 1), classify VMs against the containerization criteria in `docs/decisions/compute-tier-selection.md`. Workloads flagged as container-ready should be planned for graduation:

- **Graduate to `azure-kubernetes-service`** — stateful platform services, custom CNI requirements, DaemonSet dependencies, Kubernetes-native operators
- **Graduate to `azure-container-apps`** — stateless HTTP APIs, event-driven workloads, scale-to-zero candidates, Dapr-compatible services

VM skill scope ends at the handoff classification. Do not architect the container landing within this skill.

## Prerequisites and Caveats

| Assumption | Caveat |
|------------|--------|
| **Confidential VM regional availability** | DCsv3, DCdsv3, ECsv5, ECdsv5 SKUs are **not available in all Azure regions.** Verify the current regional availability matrix on Microsoft Learn before selecting Confidential VMs as an architecture component. Regional gaps can block the design for regulated tenants with strict data-residency constraints. |
| **Trusted Launch requires Gen2** | Trusted Launch cannot be enabled on Gen1 VMs — the capability depends on UEFI firmware, which Gen1 images do not expose. Gen1 VMs must be migrated to Gen2 images before Secure Boot and vTPM can be enabled. This is a migration prerequisite, not a configuration toggle. |
| **Azure Dedicated Host SKU eligibility and billing** | Not all VM SKUs are supported on Dedicated Host. Map your required VM family to an eligible host SKU before committing capacity. Dedicated Host is billed per host regardless of VM density — poorly-packed hosts carry premium cost. Verify subscription quota before ordering; capacity is regionally constrained. |
| **Defender for Servers — paid plan required** | JIT VM access, file integrity monitoring, adaptive application controls, and vulnerability assessment (Defender Vulnerability Management) all require **Defender for Servers Plan 1 or Plan 2**. These capabilities do not activate at the Defender for Cloud free tier. Regulated scenarios (S3) must budget for the Defender plan as a non-optional line item. |
| **Spot VMs — 30-second eviction notice** | Azure Spot VMs can be evicted with 30 seconds' notice when Azure requires capacity back. Spot is suitable for fault-tolerant batch processing, stateless dev/test, and ML training jobs with checkpointing. Spot VMs must never back production state-bearing workloads, databases, or any service with an availability SLA requirement. |

## References

| Topic | URL |
|-------|-----|
| Compute tier selection ADR | `docs/decisions/compute-tier-selection.md` (repo-local) |
| VM landing zone guidance — CAF | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/compute |
| Trusted Launch overview | https://learn.microsoft.com/en-us/azure/virtual-machines/trusted-launch |
| Confidential VMs overview | https://learn.microsoft.com/en-us/azure/confidential-computing/confidential-vm-overview |
| OS disk encryption overview (CMK, DES) | https://learn.microsoft.com/en-us/azure/virtual-machines/disk-encryption-overview |
| VMSS Flex orchestration modes | https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-orchestration-modes |
| Azure Dedicated Host | https://learn.microsoft.com/en-us/azure/virtual-machines/dedicated-hosts |
| Azure Compute Gallery | https://learn.microsoft.com/en-us/azure/virtual-machines/azure-compute-gallery |
| Defender for Servers overview | https://learn.microsoft.com/en-us/azure/defender-for-cloud/defender-for-servers-introduction |

## Revision History

| Date | Author | Notes |
|------|--------|-------|
| 2026-05-18 | Saul | Initial Wave 2 authoring — VM availability architecture, security hardening, CMK disk encryption, Trusted Launch, Confidential VMs, Dedicated Host, Compute Gallery, managed identity, brownfield S3 playbook (8-step), 5 anti-patterns, 5 hidden-assumption caveats |

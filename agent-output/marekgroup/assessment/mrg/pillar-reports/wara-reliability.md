# Reliability — Detailed Assessment Report

> **Scope**: `mrg` | **Assessed**: 2026-05-26T19:33:36.636068+00:00

---

## Overview

Ensure your workload meets uptime commitments. Reliability encompasses availability zones, redundancy, disaster recovery, backup, and monitoring.

## Score

| Metric | Value |
|--------|-------|
| **Pillar Score** | **15.0/100** |
| Critical findings | 0 |
| High findings | 6 |
| Medium findings | 5 |
| Low findings | 0 |
| Total findings | 11 |

**Assessment**: 🔴 Poor — critical remediation required.

## Related CAF Design Areas

| Design Area | Relevance |
|-------------|-----------|
| Network Topology & Connectivity | Primary |
| Management | Primary |
| Security | Primary |

## Findings Summary

| # | ID | Severity | Title | Confidence | Resources |
|---|-----|----------|-------|-----------|-----------|
| 1 | `APRL-REL-E6C7E1CC` | 🟠 High | Ensure that storage accounts are zone or region redundant (storageAccounts) | high | 5 |
| 2 | `APRL-REL-C63B81FB` | 🟠 High | Use Standard SKU and Zone-Redundant IPs when applicable (publicIPAddresses) | high | 2 |
| 3 | `APRL-REL-273F6B30` | 🟠 High | Run production workloads on two or more VMs using VMSS Flex (virtualMachines) | high | 1 |
| 4 | `APRL-REL-2BD0BE95` | 🟠 High | Deploy VMs across Availability Zones (virtualMachines) | high | 1 |
| 5 | `REL-001` | 🟠 High | VMs without availability zones | high | 1 |
| 6 | `REL-003` | 🟠 High | VMs without backup enabled | high | 1 |
| 7 | `APRL-REL-3538AA48` | 🟡 Medium | Ensure Time-To-Live (TTL) is set appropriately to ensure RTOs can be met (privateDnsZones) | medium | 10 |
| 8 | `APRL-REL-1ADBA190` | 🟡 Medium | Use NAT gateway for outbound connectivity to avoid SNAT Exhaustion (publicIPAddresses) | high | 1 |
| 9 | `APRL-REL-CFE22A65` | 🟡 Medium | Replicate VMs using Azure Site Recovery (virtualMachines) | high | 1 |
| 10 | `APRL-REL-1981F704` | 🟡 Medium | Backup VMs with Azure Backup service (virtualMachines) | high | 1 |
| 11 | `REL-007` | 🟡 Medium | Storage accounts without geo-redundant replication | high | 5 |

## Detailed Findings

### APRL-REL-E6C7E1CC: Ensure that storage accounts are zone or region redundant (storageAccounts)

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 5 |

**Recommendation**: Redundancy ensures storage accounts meet availability and durability targets amidst failures, weighing lower costs against higher availability. Locally redundant storage offers the least durability at the lowest cost.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcapsb9337e00020542b2` | mcapsb9337e00020542b2 |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/rg-ytesfaye-4803/providers/Microsoft.Storage/storageAccounts/stglxystrb4bmr2m` | stglxystrb4bmr2m |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps8c734350c450220e` | mcaps8c734350c450220e |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcapsb13aaeea0d0d7c35` | mcapsb13aaeea0d0d7c35 |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps8f810dbef6d6d9e7` | mcaps8f810dbef6d6d9e7 |

**References**:

- [https://learn.microsoft.com/azure/storage/common/storage-redundancy](https://learn.microsoft.com/azure/storage/common/storage-redundancy)

---

### APRL-REL-C63B81FB: Use Standard SKU and Zone-Redundant IPs when applicable (publicIPAddresses)

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 2 |

**Recommendation**: Public IP addresses in Azure can be of standard SKU, available as non-zonal, zonal, or zone-redundant. Zone-redundant IPs are accessible across all zones, resisting any single zone failure, thereby providing higher resilience.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Network/publicIPAddresses/gh-runner-pip` | gh-runner-pip |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/mrg-conn-hub-scus-rg/providers/Microsoft.Network/publicIPAddresses/mrg-bastion-pip` | mrg-bastion-pip |

**References**:

- [https://learn.microsoft.com/azure/virtual-network/ip-services/public-ip-addresses#availability-zone](https://learn.microsoft.com/azure/virtual-network/ip-services/public-ip-addresses#availability-zone)

---

### APRL-REL-273F6B30: Run production workloads on two or more VMs using VMSS Flex (virtualMachines)

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Production VM workloads should be deployed on multiple VMs and grouped in a VMSS Flex instance to intelligently distribute across the platform, minimizing the impact of platform faults and updates.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-orchestration-modes#what-has-changed-with-flexible-orchestration-mode](https://learn.microsoft.com/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-orchestration-modes#what-has-changed-with-flexible-orchestration-mode)

---

### APRL-REL-2BD0BE95: Deploy VMs across Availability Zones (virtualMachines)

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Azure Availability Zones, within each Azure region, are tolerant to local failures, protecting applications and data against unlikely Datacenter failures by being physically separate.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/virtual-machines/create-portal-availability-zone?tabs=standard](https://learn.microsoft.com/azure/virtual-machines/create-portal-availability-zone?tabs=standard)

---

### REL-001: VMs without availability zones

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | network |
| ALZ Area | networking |
| Resources Affected | 1 |

**Recommendation**: Deploy VMs across availability zones for high availability.

**Remediation Steps**:

1. Redeploy VMs into availability zones (requires VM recreate)

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/reliability/availability-zones-overview](https://learn.microsoft.com/azure/reliability/availability-zones-overview)

---

### REL-003: VMs without backup enabled

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Enable Azure Backup for production virtual machines to improve recovery readiness.

**Remediation Steps**:

1. Create or select a Recovery Services vault in the target region
2. Configure backup protection for each VM and validate restore points are created

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/backup/backup-overview](https://learn.microsoft.com/azure/backup/backup-overview)

---

### APRL-REL-3538AA48: Ensure Time-To-Live (TTL) is set appropriately to ensure RTOs can be met (privateDnsZones)

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | medium |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 10 |

**Recommendation**: Azure Private DNS allows the Time-To-Live (TTL) for record sets in the zone to be set to a value between 1 and 2147483647 seconds. You should ensure that the TTL for the DNS record sets in your DNS Zones are set appropriately to meet your RTO targets.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/contosoresourcegroup/providers/microsoft.network/privatednszones/contoso.com/SOA/@` | @ |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-dns-scus-rg/providers/microsoft.network/privatednszones/privatelink.azurecr.io/SOA/@` | @ |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-dns-scus-rg/providers/microsoft.network/privatednszones/privatelink.azurewebsites.net/SOA/@` | @ |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-dns-scus-rg/providers/microsoft.network/privatednszones/privatelink.blob.core.windows.net/SOA/@` | @ |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-dns-scus-rg/providers/microsoft.network/privatednszones/privatelink.cognitiveservices.azure.com/SOA/@` | @ |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-dns-scus-rg/providers/microsoft.network/privatednszones/privatelink.database.windows.net/SOA/@` | @ |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-dns-scus-rg/providers/microsoft.network/privatednszones/privatelink.file.core.windows.net/SOA/@` | @ |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-dns-scus-rg/providers/microsoft.network/privatednszones/privatelink.openai.azure.com/SOA/@` | @ |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-dns-scus-rg/providers/microsoft.network/privatednszones/privatelink.servicebus.windows.net/SOA/@` | @ |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-dns-scus-rg/providers/microsoft.network/privatednszones/privatelink.vaultcore.azure.net/SOA/@` | @ |

**References**:

- [https://learn.microsoft.com/azure/reliability/reliability-dns](https://learn.microsoft.com/azure/reliability/reliability-dns)

---

### APRL-REL-1ADBA190: Use NAT gateway for outbound connectivity to avoid SNAT Exhaustion (publicIPAddresses)

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Prevent connectivity failures due to SNAT port exhaustion by employing NAT gateway for outbound traffic from virtual networks, ensuring dynamic scaling and secure internet connections.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Network/publicIPAddresses/gh-runner-pip` | gh-runner-pip |

**References**:

- [https://learn.microsoft.com/azure/advisor/advisor-reference-reliability-recommendations#use-nat-gateway-for-outbound-connectivity](https://learn.microsoft.com/azure/advisor/advisor-reference-reliability-recommendations#use-nat-gateway-for-outbound-connectivity)

---

### APRL-REL-CFE22A65: Replicate VMs using Azure Site Recovery (virtualMachines)

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Replicating Azure VMs via Site Recovery entails continuous, asynchronous disk replication to a target region. Recovery points are generated every few minutes, ensuring a Recovery Point Objective (RPO) in minutes.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/architecture/checklist/resiliency-per-service#virtual-machines](https://learn.microsoft.com/azure/architecture/checklist/resiliency-per-service#virtual-machines)

---

### APRL-REL-1981F704: Backup VMs with Azure Backup service (virtualMachines)

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Enable backups for your virtual machines with Azure Backup to secure and quickly recover your data. This service offers simple, secure, and cost-effective solutions for backing up and recovering data from the Microsoft Azure cloud.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/backup/backup-overview](https://learn.microsoft.com/azure/backup/backup-overview)

---

### REL-007: Storage accounts without geo-redundant replication

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 5 |

**Recommendation**: Use GRS, RA-GRS, GZRS, or RA-GZRS for storage accounts that require regional disaster recovery.

**Remediation Steps**:

1. Review workload recovery objectives and select an appropriate geo-redundant SKU
2. Update the storage account replication setting during a planned maintenance window

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcapsb9337e00020542b2` | mcapsb9337e00020542b2 |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/rg-ytesfaye-4803/providers/Microsoft.Storage/storageAccounts/stglxystrb4bmr2m` | stglxystrb4bmr2m |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps8c734350c450220e` | mcaps8c734350c450220e |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcapsb13aaeea0d0d7c35` | mcapsb13aaeea0d0d7c35 |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps8f810dbef6d6d9e7` | mcaps8f810dbef6d6d9e7 |

**References**:

- [https://learn.microsoft.com/azure/storage/common/storage-redundancy](https://learn.microsoft.com/azure/storage/common/storage-redundancy)

---

## Remediation Priority Matrix

| Priority | ID | Title | Effort | Impact |
|----------|-----|-------|--------|--------|
| 1 | `APRL-REL-E6C7E1CC` | Ensure that storage accounts are zone or region redundant (storageAccounts) | Low | High |
| 2 | `APRL-REL-C63B81FB` | Use Standard SKU and Zone-Redundant IPs when applicable (publicIPAddresses) | Low | High |
| 3 | `APRL-REL-273F6B30` | Run production workloads on two or more VMs using VMSS Flex (virtualMachines) | Low | High |
| 4 | `APRL-REL-2BD0BE95` | Deploy VMs across Availability Zones (virtualMachines) | Low | High |
| 5 | `REL-001` | VMs without availability zones | Low | High |
| 6 | `REL-003` | VMs without backup enabled | Medium | High |
| 7 | `APRL-REL-3538AA48` | Ensure Time-To-Live (TTL) is set appropriately to ensure RTOs can be met (privateDnsZones) | Low | Medium |
| 8 | `APRL-REL-1ADBA190` | Use NAT gateway for outbound connectivity to avoid SNAT Exhaustion (publicIPAddresses) | Low | Medium |
| 9 | `APRL-REL-CFE22A65` | Replicate VMs using Azure Site Recovery (virtualMachines) | Low | Medium |
| 10 | `APRL-REL-1981F704` | Backup VMs with Azure Backup service (virtualMachines) | Low | Medium |
| 11 | `REL-007` | Storage accounts without geo-redundant replication | Medium | Medium |

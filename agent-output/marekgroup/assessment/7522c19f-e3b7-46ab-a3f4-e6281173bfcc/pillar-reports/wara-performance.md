# Performance Efficiency — Detailed Assessment Report

> **Scope**: `7522c19f-e3b7-46ab-a3f4-e6281173bfcc` | **Assessed**: 2026-05-04T21:00:05.733455+00:00

---

## Overview

Ensure your workload meets performance targets. Performance efficiency covers scaling, caching, load balancing, and resource sizing.

## Score

| Metric | Value |
|--------|-------|
| **Pillar Score** | **88.0/100** |
| Critical findings | 0 |
| High findings | 1 |
| Medium findings | 0 |
| Low findings | 1 |
| Total findings | 2 |

**Assessment**: ⚠️ Good — some improvements recommended.

## Related CAF Design Areas

| Design Area | Relevance |
|-------------|-----------|
| Network Topology & Connectivity | Primary |
| Management | Primary |

## Findings Summary

| # | ID | Severity | Title | Confidence | Resources |
|---|-----|----------|-------|-----------|-----------|
| 1 | `APRL-PER-DF0FF862` | 🟠 High | Mission Critical Workloads should consider using Premium or Ultra Disks (virtualMachines) | high | 1 |
| 2 | `PER-001` | 🔵 Low | Storage accounts using legacy SKU | medium | 11 |

## Detailed Findings

### APRL-PER-DF0FF862: Mission Critical Workloads should consider using Premium or Ultra Disks (virtualMachines)

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Compared to Standard HDD and SSD, Premium SSD, SSD v2, and Ultra Disks offer improved performance, configurability, and higher single-instance VM uptime SLAs. The lowest SLA of all disks on a VM applies, so it is best to use Premium or Ultra Disks for the highest uptime SLA.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/virtual-machines/disks-types#disk-type-comparison](https://learn.microsoft.com/azure/virtual-machines/disks-types#disk-type-comparison)

---

### PER-001: Storage accounts using legacy SKU

| Attribute | Value |
|-----------|-------|
| Severity | 🔵 Low |
| Confidence | medium |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 11 |

**Recommendation**: Evaluate if ZRS or GRS replication is appropriate for production workloads.

**Remediation Steps**:

1. Assess replication needs per workload; upgrade to ZRS/GRS where needed

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcapsb9337e00020542b2` | mcapsb9337e00020542b2 |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/rg-ytesfaye-4803/providers/Microsoft.Storage/storageAccounts/stglxystrb4bmr2m` | stglxystrb4bmr2m |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps8c734350c450220e` | mcaps8c734350c450220e |
| `/subscriptions/29b08c4f-2190-4b60-9a18-f171cde8a007/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps9a18f171cde8a007` | mcaps9a18f171cde8a007 |
| `/subscriptions/67c7b3ae-08e7-49d4-8cf4-c4e3c74d41f3/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps8cf4c4e3c74d41f3` | mcaps8cf4c4e3c74d41f3 |
| `/subscriptions/71d5e806-d26a-45b6-9a46-234a7851bd2d/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps9a46234a7851bd2d` | mcaps9a46234a7851bd2d |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcapsb13aaeea0d0d7c35` | mcapsb13aaeea0d0d7c35 |
| `/subscriptions/e56ced5d-d05f-45a2-9ac3-821ab51454e9/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps9ac3821ab51454e9` | mcaps9ac3821ab51454e9 |
| `/subscriptions/e9a25ee1-a88a-4af0-88a7-cdc86edbe853/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps88a7cdc86edbe853` | mcaps88a7cdc86edbe853 |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps8f810dbef6d6d9e7` | mcaps8f810dbef6d6d9e7 |
| `/subscriptions/f85d0678-f17c-4695-abd1-55ae93516337/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcapsabd155ae93516337` | mcapsabd155ae93516337 |

**References**:

- [https://learn.microsoft.com/azure/storage/common/storage-redundancy](https://learn.microsoft.com/azure/storage/common/storage-redundancy)

---

## Remediation Priority Matrix

| Priority | ID | Title | Effort | Impact |
|----------|-----|-------|--------|--------|
| 1 | `APRL-PER-DF0FF862` | Mission Critical Workloads should consider using Premium or Ultra Disks (virtualMachines) | Low | High |
| 2 | `PER-001` | Storage accounts using legacy SKU | Low | Medium |

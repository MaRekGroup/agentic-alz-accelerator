# Security — Detailed Assessment Report

> **Scope**: `7522c19f-e3b7-46ab-a3f4-e6281173bfcc` | **Assessed**: 2026-05-04T21:00:05.733455+00:00

---

## Overview

Protect your workload against security threats. Security controls include network segmentation, identity management, encryption, threat detection, and vulnerability management.

## Score

| Metric | Value |
|--------|-------|
| **Pillar Score** | **30.0/100** |
| Critical findings | 1 |
| High findings | 3 |
| Medium findings | 4 |
| Low findings | 0 |
| Total findings | 8 |

**Assessment**: 🔴 Poor — critical remediation required.

## Related CAF Design Areas

| Design Area | Relevance |
|-------------|-----------|
| Security | Primary |
| Identity & Access Management | Primary |
| Network Topology & Connectivity | Primary |

## Findings Summary

| # | ID | Severity | Title | Confidence | Resources |
|---|-----|----------|-------|-----------|-----------|
| 1 | `SEC-010` | 🔴 Critical | Defender for Cloud enabled on subscriptions | high | 39 |
| 2 | `SEC-014` | 🟠 High | DDoS Protection Plan on hub VNet | high | 1 |
| 3 | `SEC-025` | 🟠 High | Managed Identity preferred over service principal secrets | medium | 1 |
| 4 | `SEC-029` | 🟠 High | Storage accounts require secure transfer (SMB encryption) | high | 11 |
| 5 | `SEC-008` | 🟡 Medium | Public IP addresses detected | medium | 2 |
| 6 | `SEC-018` | 🟡 Medium | Diagnostic settings on security-critical resources | medium | 16 |
| 7 | `SEC-020` | 🟡 Medium | JIT VM access enabled for management | medium | 1 |
| 8 | `SEC-026` | 🟡 Medium | Activity log exported to Log Analytics | medium | 1 |

## Detailed Findings

### SEC-010: Defender for Cloud enabled on subscriptions

| Attribute | Value |
|-----------|-------|
| Severity | 🔴 Critical |
| Confidence | high |
| CAF Area | security |
| ALZ Area | security |
| Resources Affected | 39 |

**Recommendation**: Enable Defender for Cloud Standard tier on all subscriptions.

**Remediation Steps**:

1. Enable via: az security pricing create --name default --tier Standard

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/providers/Microsoft.Security/pricings/Api` | Api |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/providers/Microsoft.Security/pricings/ContainerRegistry` | ContainerRegistry |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/providers/Microsoft.Security/pricings/Dns` | Dns |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/providers/Microsoft.Security/pricings/KubernetesService` | KubernetesService |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/providers/Microsoft.Security/pricings/Api` | Api |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/providers/Microsoft.Security/pricings/ContainerRegistry` | ContainerRegistry |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/providers/Microsoft.Security/pricings/Dns` | Dns |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/providers/Microsoft.Security/pricings/KubernetesService` | KubernetesService |
| `/subscriptions/29b08c4f-2190-4b60-9a18-f171cde8a007/providers/Microsoft.Security/pricings/Api` | Api |
| `/subscriptions/29b08c4f-2190-4b60-9a18-f171cde8a007/providers/Microsoft.Security/pricings/ContainerRegistry` | ContainerRegistry |
| `/subscriptions/29b08c4f-2190-4b60-9a18-f171cde8a007/providers/Microsoft.Security/pricings/Dns` | Dns |
| `/subscriptions/29b08c4f-2190-4b60-9a18-f171cde8a007/providers/Microsoft.Security/pricings/KubernetesService` | KubernetesService |
| `/subscriptions/67c7b3ae-08e7-49d4-8cf4-c4e3c74d41f3/providers/Microsoft.Security/pricings/Api` | Api |
| `/subscriptions/67c7b3ae-08e7-49d4-8cf4-c4e3c74d41f3/providers/Microsoft.Security/pricings/ContainerRegistry` | ContainerRegistry |
| `/subscriptions/67c7b3ae-08e7-49d4-8cf4-c4e3c74d41f3/providers/Microsoft.Security/pricings/Dns` | Dns |
| `/subscriptions/67c7b3ae-08e7-49d4-8cf4-c4e3c74d41f3/providers/Microsoft.Security/pricings/KubernetesService` | KubernetesService |
| `/subscriptions/71d5e806-d26a-45b6-9a46-234a7851bd2d/providers/Microsoft.Security/pricings/Api` | Api |
| `/subscriptions/71d5e806-d26a-45b6-9a46-234a7851bd2d/providers/Microsoft.Security/pricings/ContainerRegistry` | ContainerRegistry |
| `/subscriptions/71d5e806-d26a-45b6-9a46-234a7851bd2d/providers/Microsoft.Security/pricings/Dns` | Dns |
| `/subscriptions/71d5e806-d26a-45b6-9a46-234a7851bd2d/providers/Microsoft.Security/pricings/KubernetesService` | KubernetesService |
| ... | *19 more* |

**References**:

- [https://learn.microsoft.com/azure/defender-for-cloud/enable-enhanced-security](https://learn.microsoft.com/azure/defender-for-cloud/enable-enhanced-security)

---

### SEC-014: DDoS Protection Plan on hub VNet

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | network |
| ALZ Area | networking |
| Resources Affected | 1 |

**Recommendation**: Enable DDoS Network Protection on hub virtual networks.

**Remediation Steps**:

1. Create DDoS protection plan and associate with hub VNet

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/mrg-conn-hub-scus-rg/providers/Microsoft.Network/virtualNetworks/mrg-hub-vnet` | mrg-hub-vnet |

**References**:

- [https://learn.microsoft.com/azure/ddos-protection/ddos-protection-overview](https://learn.microsoft.com/azure/ddos-protection/ddos-protection-overview)

---

### SEC-025: Managed Identity preferred over service principal secrets

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | medium |
| CAF Area | identity_access |
| ALZ Area | identity |
| Resources Affected | 1 |

**Recommendation**: Assign managed identity to compute resources instead of using service principal secrets.

**Remediation Steps**:

1. Enable system-assigned or user-assigned managed identity on the resource

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)

---

### SEC-029: Storage accounts require secure transfer (SMB encryption)

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | security |
| ALZ Area | security |
| Resources Affected | 11 |

**Recommendation**: Require secure transfer and enable infrastructure encryption on storage accounts.

**Remediation Steps**:

1. Enable HTTPS-only and infrastructure encryption on storage accounts

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

- [https://learn.microsoft.com/azure/storage/common/storage-require-secure-transfer](https://learn.microsoft.com/azure/storage/common/storage-require-secure-transfer)

---

### SEC-008: Public IP addresses detected

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | medium |
| CAF Area | network |
| ALZ Area | networking |
| Resources Affected | 2 |

**Recommendation**: Review public IP addresses — remove unnecessary public exposure.

**Remediation Steps**:

1. Audit each public IP for necessity
2. Replace with Private Endpoints where possible

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Network/publicIPAddresses/gh-runner-pip` | gh-runner-pip |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/mrg-conn-hub-scus-rg/providers/Microsoft.Network/publicIPAddresses/mrg-bastion-pip` | mrg-bastion-pip |

**References**:

- [https://learn.microsoft.com/azure/virtual-network/ip-services/public-ip-addresses](https://learn.microsoft.com/azure/virtual-network/ip-services/public-ip-addresses)

---

### SEC-018: Diagnostic settings on security-critical resources

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | medium |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 16 |

**Recommendation**: Configure diagnostic settings on Key Vaults, NSGs, and Firewalls to ship logs to Log Analytics.

**Remediation Steps**:

1. Create diagnostic setting: az monitor diagnostic-settings create --resource {id} --workspace {law-id}

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/contosoresourcegroup/providers/Microsoft.Network/networkSecurityGroups/CoreServicesVnet-DatabaseSubnet-nsg-eastus` | CoreServicesVnet-DatabaseSubnet-nsg-eastus |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/contosoresourcegroup/providers/Microsoft.Network/networkSecurityGroups/CoreServicesVnet-PublicWebServiceSubnet-nsg-eastus` | CoreServicesVnet-PublicWebServiceSubnet-nsg-eastus |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/contosoresourcegroup/providers/Microsoft.Network/networkSecurityGroups/CoreServicesVnet-SharedServicesSubnet-nsg-eastus` | CoreServicesVnet-SharedServicesSubnet-nsg-eastus |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/contosoresourcegroup/providers/Microsoft.Network/networkSecurityGroups/ManufacturingVnet-ManufacturingSystemsSubnet-nsg-westeurope` | ManufacturingVnet-ManufacturingSystemsSubnet-nsg-westeurope |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/contosoresourcegroup/providers/Microsoft.Network/networkSecurityGroups/ManufacturingVnet-SensorSubnet1-nsg-westeurope` | ManufacturingVnet-SensorSubnet1-nsg-westeurope |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/contosoresourcegroup/providers/Microsoft.Network/networkSecurityGroups/ManufacturingVnet-SensorSubnet2-nsg-westeurope` | ManufacturingVnet-SensorSubnet2-nsg-westeurope |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/contosoresourcegroup/providers/Microsoft.Network/networkSecurityGroups/ManufacturingVnet-SensorSubnet3-nsg-westeurope` | ManufacturingVnet-SensorSubnet3-nsg-westeurope |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/contosoresourcegroup/providers/Microsoft.Network/networkSecurityGroups/ResearchVnet-ResearchSystemSubnet-nsg-southeastasia` | ResearchVnet-ResearchSystemSubnet-nsg-southeastasia |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ContosoResourceGroup/providers/Microsoft.Network/networkSecurityGroups/vnet-westus3-nic01-nsg` | vnet-westus3-nic01-nsg |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/mrg-identity-scus-rg/providers/Microsoft.Network/networkSecurityGroups/mrg-identity-dc-nsg` | mrg-identity-dc-nsg |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/mrg-identity-scus-rg/providers/Microsoft.Network/networkSecurityGroups/mrg-identity-svc-nsg` | mrg-identity-svc-nsg |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Network/networkSecurityGroups/vnet-centralus-nic01-95267e0b-nsg` | vnet-centralus-nic01-95267e0b-nsg |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/mrg-conn-hub-scus-rg/providers/Microsoft.Network/networkSecurityGroups/mrg-hub-vnet-AzureBastionSubnet-nsg-southcentralus` | mrg-hub-vnet-AzureBastionSubnet-nsg-southcentralus |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/mrg-conn-hub-scus-rg/providers/Microsoft.Network/networkSecurityGroups/mrg-hub-vnet-DnsResolverInbound-nsg-southcentralus` | mrg-hub-vnet-DnsResolverInbound-nsg-southcentralus |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/mrg-conn-hub-scus-rg/providers/Microsoft.Network/networkSecurityGroups/mrg-hub-vnet-DnsResolverOutbound-nsg-southcentralus` | mrg-hub-vnet-DnsResolverOutbound-nsg-southcentralus |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/mrg-sec-automation-scus-rg/providers/Microsoft.KeyVault/vaults/mrg-sec-kv` | mrg-sec-kv |

**References**:

- [https://learn.microsoft.com/azure/azure-monitor/essentials/diagnostic-settings](https://learn.microsoft.com/azure/azure-monitor/essentials/diagnostic-settings)

---

### SEC-020: JIT VM access enabled for management

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | medium |
| CAF Area | security |
| ALZ Area | security |
| Resources Affected | 1 |

**Recommendation**: Enable Just-In-Time VM access to reduce attack surface for management ports.

**Remediation Steps**:

1. Configure JIT access in Defender for Cloud for VMs requiring management access

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `—` | — |

**References**:

- [https://learn.microsoft.com/azure/defender-for-cloud/just-in-time-access-overview](https://learn.microsoft.com/azure/defender-for-cloud/just-in-time-access-overview)

---

### SEC-026: Activity log exported to Log Analytics

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | medium |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Export Activity Log to Log Analytics workspace for audit and threat detection.

**Remediation Steps**:

1. Create subscription-level diagnostic setting to ship Activity Log to LAW

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `—` | — |

**References**:

- [https://learn.microsoft.com/azure/azure-monitor/essentials/activity-log](https://learn.microsoft.com/azure/azure-monitor/essentials/activity-log)

---

## Remediation Priority Matrix

| Priority | ID | Title | Effort | Impact |
|----------|-----|-------|--------|--------|
| 1 | `SEC-010` | Defender for Cloud enabled on subscriptions | Low | Critical |
| 2 | `SEC-014` | DDoS Protection Plan on hub VNet | Low | High |
| 3 | `SEC-025` | Managed Identity preferred over service principal secrets | Low | High |
| 4 | `SEC-029` | Storage accounts require secure transfer (SMB encryption) | Low | High |
| 5 | `SEC-008` | Public IP addresses detected | Medium | Medium |
| 6 | `SEC-018` | Diagnostic settings on security-critical resources | Low | Medium |
| 7 | `SEC-020` | JIT VM access enabled for management | Low | Medium |
| 8 | `SEC-026` | Activity log exported to Log Analytics | Low | Medium |

# Operational Excellence — Detailed Assessment Report

> **Scope**: `mrg` | **Assessed**: 2026-05-26T19:33:36.636068+00:00

---

## Overview

Maintain operational health of your workload. Operational excellence includes IaC practices, policy-driven governance, logging, alerting, and automation.

## Score

| Metric | Value |
|--------|-------|
| **Pillar Score** | **50.0/100** |
| Critical findings | 0 |
| High findings | 1 |
| Medium findings | 6 |
| Low findings | 5 |
| Total findings | 12 |

**Assessment**: 🟡 Fair — significant gaps require attention.

## Related CAF Design Areas

| Design Area | Relevance |
|-------------|-----------|
| Governance | Primary |
| Management | Primary |
| Platform Automation & DevOps | Primary |

## Findings Summary

| # | ID | Severity | Title | Confidence | Resources |
|---|-----|----------|-------|-----------|-----------|
| 1 | `OPE-006` | 🟠 High | No hub VNet or firewall detected | medium | 0 |
| 2 | `APRL-OPE-1E28BBC1` | 🟡 Medium | Configure Network Watcher Connection monitor (networkWatchers) | high | 7 |
| 3 | `APRL-OPE-06B77BE9` | 🟡 Medium | Enable Virtual Network Flow Logs (virtualNetworks) | high | 7 |
| 4 | `OPE-005` | 🟡 Medium | Resources missing required tags | high | 17 |
| 5 | `OPE-007` | 🟡 Medium | Virtual machines without diagnostic settings | high | 1 |
| 6 | `OPE-011` | 🟡 Medium | Key Vaults without diagnostic logging | high | 1 |
| 7 | `OPE-012` | 🟡 Medium | Network security groups without flow logs | high | 15 |
| 8 | `APRL-OPE-8BB4A57B` | 🔵 Low | Monitor changes in Network Security Groups with Azure Monitor (networkSecurityGroups) | high | 15 |
| 9 | `APRL-OPE-4E133BD0` | 🔵 Low | Deploy Network Watcher in all regions where you have networking services (networkWatchers) | high | 8 |
| 10 | `APRL-OPE-73D1BB04` | 🔵 Low | When AccelNet is enabled, you must manually update the GuestOS NIC driver (virtualMachines) | high | 1 |
| 11 | `APRL-OPE-B72214BB` | 🔵 Low | Enable VM Insights (virtualMachines) | high | 1 |
| 12 | `OPE-013` | 🔵 Low | Storage accounts without diagnostic logging | high | 5 |

## Detailed Findings

### OPE-006: No hub VNet or firewall detected

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | medium |
| CAF Area | network |
| ALZ Area | networking |
| Resources Affected | 0 |

**Recommendation**: Deploy a hub VNet with Azure Firewall for centralized network governance.

**Remediation Steps**:

1. Deploy connectivity landing zone with hub-spoke topology

**References**:

- [https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke](https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke)

---

### APRL-OPE-1E28BBC1: Configure Network Watcher Connection monitor (networkWatchers)

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 7 |

**Recommendation**: Improves monitoring for Azure and Hybrid connectivity

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG/providers/Microsoft.Network/networkWatchers/NetworkWatcher_centralus` | NetworkWatcher_centralus |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG/providers/Microsoft.Network/networkWatchers/NetworkWatcher_eastus` | NetworkWatcher_eastus |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG/providers/Microsoft.Network/networkWatchers/NetworkWatcher_southcentralus` | NetworkWatcher_southcentralus |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG/providers/Microsoft.Network/networkWatchers/NetworkWatcher_southeastasia` | NetworkWatcher_southeastasia |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG/providers/Microsoft.Network/networkWatchers/NetworkWatcher_westeurope` | NetworkWatcher_westeurope |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG/providers/Microsoft.Network/networkWatchers/NetworkWatcher_westus3` | NetworkWatcher_westus3 |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/NetworkWatcherRG/providers/Microsoft.Network/networkWatchers/NetworkWatcher_southcentralus` | NetworkWatcher_southcentralus |

**References**:

- [https://learn.microsoft.com/azure/network-watcher/connection-monitor-overview](https://learn.microsoft.com/azure/network-watcher/connection-monitor-overview)

---

### APRL-OPE-06B77BE9: Enable Virtual Network Flow Logs (virtualNetworks)

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 7 |

**Recommendation**: Improves monitoring and security for Azure and Hybrid connectivity

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/contosoresourcegroup/providers/microsoft.network/virtualnetworks/coreservicesvnet` | CoreServicesVnet |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/contosoresourcegroup/providers/microsoft.network/virtualnetworks/manufacturingvnet` | ManufacturingVnet |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/contosoresourcegroup/providers/microsoft.network/virtualnetworks/researchvnet` | ResearchVnet |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourcegroups/mrg-conn-hub-scus-rg/providers/microsoft.network/virtualnetworks/mrg-hub-vnet` | mrg-hub-vnet |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/mrg-identity-scus-rg/providers/microsoft.network/virtualnetworks/mrg-identity-spoke-vnet` | mrg-identity-spoke-vnet |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/rg-nottagged-vmss/providers/microsoft.network/virtualnetworks/vnet-centralus` | vnet-centralus |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/contosoresourcegroup/providers/microsoft.network/virtualnetworks/vnet-westus3` | vnet-westus3 |

**References**:

- [https://learn.microsoft.com/azure/network-watcher/vnet-flow-logs-overview](https://learn.microsoft.com/azure/network-watcher/vnet-flow-logs-overview)

---

### OPE-005: Resources missing required tags

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | resource_org |
| ALZ Area | policy |
| Resources Affected | 17 |

**Recommendation**: Apply required tags (Environment, Owner, CostCenter) to all resource groups.

**Remediation Steps**:

1. Assign tagging policy at MG scope to enforce required tags
2. Remediate existing resources with tagging task

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/rg-ytesfaye-4803` | rg-ytesfaye-4803 |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ContosoResourceGroup` | ContosoResourceGroup |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/DefaultResourceGroup-EUS2` | DefaultResourceGroup-EUS2 |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ExpressRouteResourceGroup` | ExpressRouteResourceGroup |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG` | NetworkWatcherRG |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ResourceMoverRG-southcentralus-centralus-eus2` | ResourceMoverRG-southcentralus-centralus-eus2 |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss` | rg-nottagged-vmss |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/secure-logc-app` | secure-logc-app |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/NetworkWatcherRG` | NetworkWatcherRG |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/McapsGovernance` | McapsGovernance |

**References**:

- [https://learn.microsoft.com/azure/azure-resource-manager/management/tag-resources](https://learn.microsoft.com/azure/azure-resource-manager/management/tag-resources)

---

### OPE-007: Virtual machines without diagnostic settings

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Configure diagnostic settings on virtual machines to stream guest and platform telemetry to a monitoring destination.

**Remediation Steps**:

1. Create VM diagnostic settings: az monitor diagnostic-settings create --resource {vm-id} --workspace {law-id}

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/azure-monitor/essentials/diagnostic-settings](https://learn.microsoft.com/azure/azure-monitor/essentials/diagnostic-settings)

---

### OPE-011: Key Vaults without diagnostic logging

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Configure Key Vault diagnostic settings to export audit and access logs to a centralized monitoring sink.

**Remediation Steps**:

1. Create diagnostic settings: az monitor diagnostic-settings create --resource {vault-id} --workspace {law-id}

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/mrg-sec-automation-scus-rg/providers/Microsoft.KeyVault/vaults/mrg-sec-kv` | mrg-sec-kv |

**References**:

- [https://learn.microsoft.com/azure/key-vault/general/howto-logging](https://learn.microsoft.com/azure/key-vault/general/howto-logging)

---

### OPE-012: Network security groups without flow logs

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | network |
| ALZ Area | networking |
| Resources Affected | 15 |

**Recommendation**: Enable NSG flow logs to improve traffic analysis, investigation, and troubleshooting coverage.

**Remediation Steps**:

1. Create flow logs: az network watcher flow-log create --nsg {nsg-id} --enabled true

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

**References**:

- [https://learn.microsoft.com/azure/network-watcher/nsg-flow-logging](https://learn.microsoft.com/azure/network-watcher/nsg-flow-logging)

---

### APRL-OPE-8BB4A57B: Monitor changes in Network Security Groups with Azure Monitor (networkSecurityGroups)

| Attribute | Value |
|-----------|-------|
| Severity | 🔵 Low |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 15 |

**Recommendation**: Create Alerts with Azure Monitor for operations like creating or updating Network Security Group rules to catch unauthorized/undesired changes to resources and spot attempts to bypass firewalls or access resources from the outside.

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

**References**:

- [https://learn.microsoft.com/azure/azure-monitor/essentials/activity-log?tabs=powershell](https://learn.microsoft.com/azure/azure-monitor/essentials/activity-log?tabs=powershell)

---

### APRL-OPE-4E133BD0: Deploy Network Watcher in all regions where you have networking services (networkWatchers)

| Attribute | Value |
|-----------|-------|
| Severity | 🔵 Low |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 8 |

**Recommendation**: Azure Network Watcher offers tools for monitoring, diagnosing, viewing metrics, and managing logs for IaaS resources. It helps maintain the health of VMs, VNets, application gateways, load balancers, but not for PaaS or Web analytics.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7` | NetworkWatcher_southcentralus |
| `27f84456-9d87-4d58-8c73-4350c450220e` | NetworkWatcher_eastus2 |
| `f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7` | NetworkWatcher_westus2 |
| `27f84456-9d87-4d58-8c73-4350c450220e` | NetworkWatcher_westus2 |
| `009ae910-a172-4aac-b933-7e00020542b2` | NetworkWatcher_westus2 |
| `009ae910-a172-4aac-b933-7e00020542b2` | NetworkWatcher_eastus2 |
| `009ae910-a172-4aac-b933-7e00020542b2` | NetworkWatcher_southcentralus |
| `a2343e21-1c22-42a2-b13a-aeea0d0d7c35` | NetworkWatcher_westus2 |

**References**:

- [https://learn.microsoft.com/azure/network-watcher/network-watcher-overview](https://learn.microsoft.com/azure/network-watcher/network-watcher-overview)

---

### APRL-OPE-73D1BB04: When AccelNet is enabled, you must manually update the GuestOS NIC driver (virtualMachines)

| Attribute | Value |
|-----------|-------|
| Severity | 🔵 Low |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: When Accelerated Networking is enabled, the default Azure VNet interface in GuestOS is swapped for a Mellanox, and its driver comes from a 3rd party. Marketplace images have the latest Mellanox drivers, but post-deployment, updating the driver is the user's responsibility.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Compute/virtualMachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/virtual-network/accelerated-networking-overview](https://learn.microsoft.com/azure/virtual-network/accelerated-networking-overview)

---

### APRL-OPE-B72214BB: Enable VM Insights (virtualMachines)

| Attribute | Value |
|-----------|-------|
| Severity | 🔵 Low |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: VM Insights monitors VM and scale set performance, health, running processes, and dependencies. It enhances the predictability of application performance and availability by pinpointing performance bottlenecks and network issues, and it clarifies if problems are related to other dependencies.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/rg-nottagged-vmss/providers/microsoft.compute/virtualmachines/vm-github-runner-01` | vm-github-runner-01 |

**References**:

- [https://learn.microsoft.com/azure/azure-monitor/vm/vminsights-overview](https://learn.microsoft.com/azure/azure-monitor/vm/vminsights-overview)

---

### OPE-013: Storage accounts without diagnostic logging

| Attribute | Value |
|-----------|-------|
| Severity | 🔵 Low |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 5 |

**Recommendation**: Configure storage account diagnostic settings to forward logs and metrics for operations and investigations.

**Remediation Steps**:

1. Create diagnostic settings: az monitor diagnostic-settings create --resource {storage-id} --workspace {law-id}

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcapsb9337e00020542b2` | mcapsb9337e00020542b2 |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/rg-ytesfaye-4803/providers/Microsoft.Storage/storageAccounts/stglxystrb4bmr2m` | stglxystrb4bmr2m |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps8c734350c450220e` | mcaps8c734350c450220e |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcapsb13aaeea0d0d7c35` | mcapsb13aaeea0d0d7c35 |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/McapsGovernance/providers/Microsoft.Storage/storageAccounts/mcaps8f810dbef6d6d9e7` | mcaps8f810dbef6d6d9e7 |

**References**:

- [https://learn.microsoft.com/azure/storage/common/monitor-storage](https://learn.microsoft.com/azure/storage/common/monitor-storage)

---

## Remediation Priority Matrix

| Priority | ID | Title | Effort | Impact |
|----------|-----|-------|--------|--------|
| 1 | `OPE-006` | No hub VNet or firewall detected | Low | High |
| 2 | `APRL-OPE-1E28BBC1` | Configure Network Watcher Connection monitor (networkWatchers) | Low | Medium |
| 3 | `APRL-OPE-06B77BE9` | Enable Virtual Network Flow Logs (virtualNetworks) | Low | Medium |
| 4 | `OPE-005` | Resources missing required tags | Medium | Medium |
| 5 | `OPE-007` | Virtual machines without diagnostic settings | Low | Medium |
| 6 | `OPE-011` | Key Vaults without diagnostic logging | Low | Medium |
| 7 | `OPE-012` | Network security groups without flow logs | Low | Medium |
| 8 | `APRL-OPE-8BB4A57B` | Monitor changes in Network Security Groups with Azure Monitor (networkSecurityGroups) | Low | Medium |
| 9 | `APRL-OPE-4E133BD0` | Deploy Network Watcher in all regions where you have networking services (networkWatchers) | Low | Medium |
| 10 | `APRL-OPE-73D1BB04` | When AccelNet is enabled, you must manually update the GuestOS NIC driver (virtualMachines) | Low | Medium |
| 11 | `APRL-OPE-B72214BB` | Enable VM Insights (virtualMachines) | Low | Medium |
| 12 | `OPE-013` | Storage accounts without diagnostic logging | Low | Medium |

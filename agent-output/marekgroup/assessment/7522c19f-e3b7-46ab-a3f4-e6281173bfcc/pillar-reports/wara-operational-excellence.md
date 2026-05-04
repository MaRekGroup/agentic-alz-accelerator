# Operational Excellence — Detailed Assessment Report

> **Scope**: `7522c19f-e3b7-46ab-a3f4-e6281173bfcc` | **Assessed**: 2026-05-04T18:19:20.499872+00:00

---

## Overview

Maintain operational health of your workload. Operational excellence includes IaC practices, policy-driven governance, logging, alerting, and automation.

## Score

| Metric | Value |
|--------|-------|
| **Pillar Score** | **57.0/100** |
| Critical findings | 0 |
| High findings | 2 |
| Medium findings | 3 |
| Low findings | 4 |
| Total findings | 9 |

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
| 1 | `APRL-OPE-9729C89D` | 🟠 High | Configure Service Health Alerts (Subscriptions) | high | 10 |
| 2 | `OPE-006` | 🟠 High | No hub VNet or firewall detected | medium | 0 |
| 3 | `APRL-OPE-1E28BBC1` | 🟡 Medium | Configure Network Watcher Connection monitor (networkWatchers) | high | 7 |
| 4 | `APRL-OPE-06B77BE9` | 🟡 Medium | Enable Virtual Network Flow Logs (virtualNetworks) | high | 7 |
| 5 | `OPE-005` | 🟡 Medium | Resources missing required tags | high | 22 |
| 6 | `APRL-OPE-8BB4A57B` | 🔵 Low | Monitor changes in Network Security Groups with Azure Monitor (networkSecurityGroups) | high | 15 |
| 7 | `APRL-OPE-4E133BD0` | 🔵 Low | Deploy Network Watcher in all regions where you have networking services (networkWatchers) | high | 14 |
| 8 | `APRL-OPE-73D1BB04` | 🔵 Low | When AccelNet is enabled, you must manually update the GuestOS NIC driver (virtualMachines) | high | 1 |
| 9 | `APRL-OPE-B72214BB` | 🔵 Low | Enable VM Insights (virtualMachines) | high | 1 |

## Detailed Findings

### APRL-OPE-9729C89D: Configure Service Health Alerts (Subscriptions)

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 10 |

**Recommendation**: Service health gives a personalized health view of Azure services and regions used, offering the best place for notifications on outages, planned maintenance, and health advisories by knowing the services used.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2` | ME-MngEnvMCAP084543-ytesfaye-1 |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e` | ME-MngEnvMCAP084543-ytesfaye-3 |
| `/subscriptions/29b08c4f-2190-4b60-9a18-f171cde8a007` | ME-MngEnvMCAP084543-ytesfaye-6 |
| `/subscriptions/67c7b3ae-08e7-49d4-8cf4-c4e3c74d41f3` | ME-MngEnvMCAP084543-ytesfaye-8 |
| `/subscriptions/71d5e806-d26a-45b6-9a46-234a7851bd2d` | ME-MngEnvMCAP084543-ytesfaye-9 |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35` | ME-MngEnvMCAP084543-ytesfaye-2 |
| `/subscriptions/e56ced5d-d05f-45a2-9ac3-821ab51454e9` | ME-MngEnvMCAP084543-ytesfaye-7 |
| `/subscriptions/e9a25ee1-a88a-4af0-88a7-cdc86edbe853` | ME-MngEnvMCAP084543-ytesfaye-5 |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7` | ME-MngEnvMCAP084543-ytesfaye-4 |
| `/subscriptions/f85d0678-f17c-4695-abd1-55ae93516337` | ME-MngEnvMCAP084543-ytesfaye-10 |

**References**:

- [https://learn.microsoft.com/azure/service-health/alerts-activity-log-service-notifications-portal](https://learn.microsoft.com/azure/service-health/alerts-activity-log-service-notifications-portal)

---

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
| Resources Affected | 22 |

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
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ExpressRouteResourceGroup` | ExpressRouteResourceGroup |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG` | NetworkWatcherRG |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ResourceMoverRG-southcentralus-centralus-eus2` | ResourceMoverRG-southcentralus-centralus-eus2 |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss` | rg-nottagged-vmss |
| `/subscriptions/29b08c4f-2190-4b60-9a18-f171cde8a007/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/67c7b3ae-08e7-49d4-8cf4-c4e3c74d41f3/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/71d5e806-d26a-45b6-9a46-234a7851bd2d/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/NetworkWatcherRG` | NetworkWatcherRG |
| `/subscriptions/e56ced5d-d05f-45a2-9ac3-821ab51454e9/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/e56ced5d-d05f-45a2-9ac3-821ab51454e9/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/e9a25ee1-a88a-4af0-88a7-cdc86edbe853/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| ... | *2 more* |

**References**:

- [https://learn.microsoft.com/azure/azure-resource-manager/management/tag-resources](https://learn.microsoft.com/azure/azure-resource-manager/management/tag-resources)

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
| Resources Affected | 14 |

**Recommendation**: Azure Network Watcher offers tools for monitoring, diagnosing, viewing metrics, and managing logs for IaaS resources. It helps maintain the health of VMs, VNets, application gateways, load balancers, but not for PaaS or Web analytics.

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `e9a25ee1-a88a-4af0-88a7-cdc86edbe853` | NetworkWatcher_westus2 |
| `f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7` | NetworkWatcher_southcentralus |
| `27f84456-9d87-4d58-8c73-4350c450220e` | NetworkWatcher_eastus2 |
| `e56ced5d-d05f-45a2-9ac3-821ab51454e9` | NetworkWatcher_westus2 |
| `f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7` | NetworkWatcher_westus2 |
| `27f84456-9d87-4d58-8c73-4350c450220e` | NetworkWatcher_westus2 |
| `71d5e806-d26a-45b6-9a46-234a7851bd2d` | NetworkWatcher_westus2 |
| `f85d0678-f17c-4695-abd1-55ae93516337` | NetworkWatcher_westus2 |
| `009ae910-a172-4aac-b933-7e00020542b2` | NetworkWatcher_westus2 |
| `009ae910-a172-4aac-b933-7e00020542b2` | NetworkWatcher_eastus2 |
| `67c7b3ae-08e7-49d4-8cf4-c4e3c74d41f3` | NetworkWatcher_westus2 |
| `29b08c4f-2190-4b60-9a18-f171cde8a007` | NetworkWatcher_westus2 |
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

## Remediation Priority Matrix

| Priority | ID | Title | Effort | Impact |
|----------|-----|-------|--------|--------|
| 1 | `APRL-OPE-9729C89D` | Configure Service Health Alerts (Subscriptions) | Low | High |
| 2 | `OPE-006` | No hub VNet or firewall detected | Low | High |
| 3 | `APRL-OPE-1E28BBC1` | Configure Network Watcher Connection monitor (networkWatchers) | Low | Medium |
| 4 | `APRL-OPE-06B77BE9` | Enable Virtual Network Flow Logs (virtualNetworks) | Low | Medium |
| 5 | `OPE-005` | Resources missing required tags | Medium | Medium |
| 6 | `APRL-OPE-8BB4A57B` | Monitor changes in Network Security Groups with Azure Monitor (networkSecurityGroups) | Low | Medium |
| 7 | `APRL-OPE-4E133BD0` | Deploy Network Watcher in all regions where you have networking services (networkWatchers) | Low | Medium |
| 8 | `APRL-OPE-73D1BB04` | When AccelNet is enabled, you must manually update the GuestOS NIC driver (virtualMachines) | Low | Medium |
| 9 | `APRL-OPE-B72214BB` | Enable VM Insights (virtualMachines) | Low | Medium |

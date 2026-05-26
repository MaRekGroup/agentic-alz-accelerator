# Cost Optimization — Detailed Assessment Report

> **Scope**: `mrg` | **Assessed**: 2026-05-26T19:33:36.636068+00:00

---

## Overview

Deliver business value while minimizing cost. Cost optimization covers right-sizing, reserved instances, waste elimination, budgets, and governance.

## Score

| Metric | Value |
|--------|-------|
| **Pillar Score** | **33.0/100** |
| Critical findings | 0 |
| High findings | 4 |
| Medium findings | 5 |
| Low findings | 1 |
| Total findings | 10 |

**Assessment**: 🔴 Poor — critical remediation required.

## Related CAF Design Areas

| Design Area | Relevance |
|-------------|-----------|
| Governance | Primary |
| Management | Primary |

## Findings Summary

| # | ID | Severity | Title | Confidence | Resources |
|---|-----|----------|-------|-----------|-----------|
| 1 | `COS-001` | 🟠 High | No budget resources found | high | 0 |
| 2 | `COS-014` | 🟠 High | Azure Advisor cost recommendations pending | high | 3 |
| 3 | `COS-017` | 🟠 High | Resource groups missing CostCenter tag | high | 17 |
| 4 | `COS-009` | 🟠 High | Long-running VMs without Reserved Instances | medium | 1 |
| 5 | `COS-004` | 🟡 Medium | Orphan network interfaces (unattached) | high | 1 |
| 6 | `COS-005` | 🟡 Medium | Empty resource groups | medium | 18 |
| 7 | `COS-020` | 🟡 Medium | No Cost Management scheduled exports | medium | 1 |
| 8 | `COS-011` | 🟡 Medium | Potentially over-provisioned VMs (B-series recommended) | medium | 1 |
| 9 | `COS-026` | 🟡 Medium | Standard SKU public IPs not associated with load balancers | medium | 2 |
| 10 | `COS-028` | 🔵 Low | Idle network interfaces | high | 1 |

## Detailed Findings

### COS-001: No budget resources found

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | governance |
| ALZ Area | policy |
| Resources Affected | 0 |

**Recommendation**: Create budget resources with 80/100/120% forecast alerts.

**Remediation Steps**:

1. Deploy budget resource via IaC with parameterized thresholds

**References**:

- [https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets](https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets)

---

### COS-014: Azure Advisor cost recommendations pending

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | governance |
| ALZ Area | policy |
| Resources Affected | 3 |

**Recommendation**: Review and act on Azure Advisor cost recommendations to reduce waste.

**Remediation Steps**:

1. Review recommendations: az advisor recommendation list --category Cost
2. Implement or dismiss each recommendation

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/providers/Microsoft.Advisor/recommendations/cc20d24328e0aef3f3b6d77ded603f0f591bd470c8d0ea6515c7bac9e2c60c0e` | Consider virtual machine reserved instance to save over the on-demand costs |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/rg-nottagged-vmss/providers/microsoft.compute/virtualmachines/vm-github-runner-01/providers/Microsoft.Advisor/recommendations/ff10582f1f5e0dc0257620d6420d2b7b5e726e3e4987aca4a2e18a68a457f109` | Right-size or shutdown underutilized virtual machines |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/providers/Microsoft.Advisor/recommendations/eaa188b0f2bf43d89b1b650afdb621747aa81099bdb18c40008f645815c7cc57` | Consider purchasing a savings plan to unlock lower prices |

**References**:

- [https://learn.microsoft.com/azure/advisor/advisor-cost-recommendations](https://learn.microsoft.com/azure/advisor/advisor-cost-recommendations)

---

### COS-017: Resource groups missing CostCenter tag

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | high |
| CAF Area | governance |
| ALZ Area | policy |
| Resources Affected | 17 |

**Recommendation**: Apply CostCenter tag to all resource groups for cost allocation and chargeback.

**Remediation Steps**:

1. Tag resource group: az tag update --resource-id <rg-id> --operation merge --tags CostCenter=<value>

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

- [https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-tagging](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-tagging)

---

### COS-009: Long-running VMs without Reserved Instances

| Attribute | Value |
|-----------|-------|
| Severity | 🟠 High |
| Confidence | medium |
| CAF Area | governance |
| ALZ Area | policy |
| Resources Affected | 1 |

**Recommendation**: Purchase Reserved Instances for VMs running 24/7 to save up to 72% vs pay-as-you-go.

**Remediation Steps**:

1. Review Advisor RI recommendations and purchase via Azure portal or API

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/providers/Microsoft.Advisor/recommendations/cc20d24328e0aef3f3b6d77ded603f0f591bd470c8d0ea6515c7bac9e2c60c0e` | Consider virtual machine reserved instance to save over the on-demand costs |

**References**:

- [https://learn.microsoft.com/azure/cost-management-billing/reservations/save-compute-costs-reservations](https://learn.microsoft.com/azure/cost-management-billing/reservations/save-compute-costs-reservations)

---

### COS-004: Orphan network interfaces (unattached)

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | high |
| CAF Area | network |
| ALZ Area | networking |
| Resources Affected | 1 |

**Recommendation**: Delete orphan NICs left behind after VM deletion.

**Remediation Steps**:

1. Verify NIC is not needed, then delete: az network nic delete --ids <id>

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Network/networkInterfaces/nic2` | nic2 |

**References**:

- [https://learn.microsoft.com/azure/virtual-network/virtual-network-network-interface](https://learn.microsoft.com/azure/virtual-network/virtual-network-network-interface)

---

### COS-005: Empty resource groups

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | medium |
| CAF Area | governance |
| ALZ Area | policy |
| Resources Affected | 18 |

**Recommendation**: Review and delete empty resource groups to reduce clutter and simplify governance.

**Remediation Steps**:

1. Verify RG is unused, then delete: az group delete --name <rg-name>

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/009ae910-a172-4aac-b933-7e00020542b2/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ContosoResourceGroup` | ContosoResourceGroup |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/DefaultResourceGroup-EUS2` | DefaultResourceGroup-EUS2 |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ExpressRouteResourceGroup` | ExpressRouteResourceGroup |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG` | NetworkWatcherRG |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ResourceMoverRG-southcentralus-centralus-eus2` | ResourceMoverRG-southcentralus-centralus-eus2 |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/secure-logc-app` | secure-logc-app |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/mrg-conn-gateways-scus-rg` | mrg-conn-gateways-scus-rg |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/NetworkWatcherRG` | NetworkWatcherRG |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/mrg-sec-governance-scus-rg` | mrg-sec-governance-scus-rg |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/mrg-sec-posture-scus-rg` | mrg-sec-posture-scus-rg |

**References**:

- [https://learn.microsoft.com/azure/azure-resource-manager/management/manage-resource-groups-portal](https://learn.microsoft.com/azure/azure-resource-manager/management/manage-resource-groups-portal)

---

### COS-020: No Cost Management scheduled exports

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | medium |
| CAF Area | governance |
| ALZ Area | policy |
| Resources Affected | 1 |

**Recommendation**: Configure scheduled Cost Management exports for cost data analysis and FinOps reporting.

**Remediation Steps**:

1. Create export: az costmanagement export create --scope <sub-id> --name daily-export

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `—` | — |

**References**:

- [https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-export-acm-data](https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-export-acm-data)

---

### COS-011: Potentially over-provisioned VMs (B-series recommended)

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | medium |
| CAF Area | management |
| ALZ Area | logging |
| Resources Affected | 1 |

**Recommendation**: Right-size over-provisioned VMs per Azure Advisor recommendations.

**Remediation Steps**:

1. Resize VM to recommended SKU: az vm resize --size <recommended-size>

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/rg-nottagged-vmss/providers/microsoft.compute/virtualmachines/vm-github-runner-01/providers/Microsoft.Advisor/recommendations/ff10582f1f5e0dc0257620d6420d2b7b5e726e3e4987aca4a2e18a68a457f109` | — |

**References**:

- [https://learn.microsoft.com/azure/advisor/advisor-cost-recommendations](https://learn.microsoft.com/azure/advisor/advisor-cost-recommendations)

---

### COS-026: Standard SKU public IPs not associated with load balancers

| Attribute | Value |
|-----------|-------|
| Severity | 🟡 Medium |
| Confidence | medium |
| CAF Area | network |
| ALZ Area | networking |
| Resources Affected | 2 |

**Recommendation**: Remove or consolidate Standard public IPs that are not serving load-balanced workloads.

**Remediation Steps**:

1. Review the public IP association and delete unused addresses: az network public-ip delete --ids <pip-id>

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Network/publicIPAddresses/gh-runner-pip` | gh-runner-pip |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/mrg-conn-hub-scus-rg/providers/Microsoft.Network/publicIPAddresses/mrg-bastion-pip` | mrg-bastion-pip |

**References**:

- [https://learn.microsoft.com/azure/virtual-network/ip-services/public-ip-addresses](https://learn.microsoft.com/azure/virtual-network/ip-services/public-ip-addresses)

---

### COS-028: Idle network interfaces

| Attribute | Value |
|-----------|-------|
| Severity | 🔵 Low |
| Confidence | high |
| CAF Area | network |
| ALZ Area | networking |
| Resources Affected | 1 |

**Recommendation**: Delete unused network interfaces that are no longer attached to virtual machines.

**Remediation Steps**:

1. Delete idle NICs after dependency review: az network nic delete --ids <nic-id>

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/rg-nottagged-vmss/providers/Microsoft.Network/networkInterfaces/nic2` | nic2 |

**References**:

- [https://learn.microsoft.com/azure/virtual-network/virtual-network-network-interface](https://learn.microsoft.com/azure/virtual-network/virtual-network-network-interface)

---

## Remediation Priority Matrix

| Priority | ID | Title | Effort | Impact |
|----------|-----|-------|--------|--------|
| 1 | `COS-001` | No budget resources found | Low | High |
| 2 | `COS-014` | Azure Advisor cost recommendations pending | Medium | High |
| 3 | `COS-017` | Resource groups missing CostCenter tag | Low | High |
| 4 | `COS-009` | Long-running VMs without Reserved Instances | Low | High |
| 5 | `COS-004` | Orphan network interfaces (unattached) | Low | Medium |
| 6 | `COS-005` | Empty resource groups | Low | Medium |
| 7 | `COS-020` | No Cost Management scheduled exports | Low | Medium |
| 8 | `COS-011` | Potentially over-provisioned VMs (B-series recommended) | Low | Medium |
| 9 | `COS-026` | Standard SKU public IPs not associated with load balancers | Low | Medium |
| 10 | `COS-028` | Idle network interfaces | Low | Medium |

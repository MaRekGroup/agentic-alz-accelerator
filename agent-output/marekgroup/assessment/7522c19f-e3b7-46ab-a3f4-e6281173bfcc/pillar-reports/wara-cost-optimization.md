# Cost Optimization — Detailed Assessment Report

> **Scope**: `7522c19f-e3b7-46ab-a3f4-e6281173bfcc` | **Assessed**: 2026-05-04T21:00:05.733455+00:00

---

## Overview

Deliver business value while minimizing cost. Cost optimization covers right-sizing, reserved instances, waste elimination, budgets, and governance.

## Score

| Metric | Value |
|--------|-------|
| **Pillar Score** | **40.0/100** |
| Critical findings | 0 |
| High findings | 4 |
| Medium findings | 4 |
| Low findings | 0 |
| Total findings | 8 |

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
| 3 | `COS-017` | 🟠 High | Resource groups missing CostCenter tag | high | 22 |
| 4 | `COS-009` | 🟠 High | Long-running VMs without Reserved Instances | medium | 1 |
| 5 | `COS-004` | 🟡 Medium | Orphan network interfaces (unattached) | high | 1 |
| 6 | `COS-005` | 🟡 Medium | Empty resource groups | medium | 23 |
| 7 | `COS-020` | 🟡 Medium | No Cost Management scheduled exports | medium | 1 |
| 8 | `COS-011` | 🟡 Medium | Potentially over-provisioned VMs (B-series recommended) | medium | 2 |

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
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/rg-nottagged-vmss/providers/microsoft.compute/virtualmachines/vm-github-runner-01/providers/Microsoft.Advisor/recommendations/4275dc26-48f7-3fc4-e4ac-ecae1bb76f95` | Right-size or shutdown underutilized virtual machines |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/rg-nottagged-vmss/providers/microsoft.compute/virtualmachines/vm-github-runner-01/providers/Microsoft.Advisor/recommendations/ff10582f1f5e0dc0257620d6420d2b7b5e726e3e4987aca4a2e18a68a457f109` | Right-size or shutdown underutilized virtual machines |

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
| Resources Affected | 22 |

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
| Resources Affected | 23 |

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
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ExpressRouteResourceGroup` | ExpressRouteResourceGroup |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/NetworkWatcherRG` | NetworkWatcherRG |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourceGroups/ResourceMoverRG-southcentralus-centralus-eus2` | ResourceMoverRG-southcentralus-centralus-eus2 |
| `/subscriptions/29b08c4f-2190-4b60-9a18-f171cde8a007/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/67c7b3ae-08e7-49d4-8cf4-c4e3c74d41f3/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/71d5e806-d26a-45b6-9a46-234a7851bd2d/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/mrg-conn-gateways-scus-rg` | mrg-conn-gateways-scus-rg |
| `/subscriptions/a2343e21-1c22-42a2-b13a-aeea0d0d7c35/resourceGroups/NetworkWatcherRG` | NetworkWatcherRG |
| `/subscriptions/e56ced5d-d05f-45a2-9ac3-821ab51454e9/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/e56ced5d-d05f-45a2-9ac3-821ab51454e9/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/e9a25ee1-a88a-4af0-88a7-cdc86edbe853/resourceGroups/McapsGovernance` | McapsGovernance |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/Default-ActivityLogAlerts` | Default-ActivityLogAlerts |
| `/subscriptions/f7c2c8aa-f2ae-4e22-8f81-0dbef6d6d9e7/resourceGroups/McapsGovernance` | McapsGovernance |
| ... | *3 more* |

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
| Resources Affected | 2 |

**Recommendation**: Right-size over-provisioned VMs per Azure Advisor recommendations.

**Remediation Steps**:

1. Resize VM to recommended SKU: az vm resize --size <recommended-size>

**Affected Resources**:

| Resource ID | Name |
|------------|------|
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/rg-nottagged-vmss/providers/microsoft.compute/virtualmachines/vm-github-runner-01/providers/Microsoft.Advisor/recommendations/4275dc26-48f7-3fc4-e4ac-ecae1bb76f95` | — |
| `/subscriptions/27f84456-9d87-4d58-8c73-4350c450220e/resourcegroups/rg-nottagged-vmss/providers/microsoft.compute/virtualmachines/vm-github-runner-01/providers/Microsoft.Advisor/recommendations/ff10582f1f5e0dc0257620d6420d2b7b5e726e3e4987aca4a2e18a68a457f109` | — |

**References**:

- [https://learn.microsoft.com/azure/advisor/advisor-cost-recommendations](https://learn.microsoft.com/azure/advisor/advisor-cost-recommendations)

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

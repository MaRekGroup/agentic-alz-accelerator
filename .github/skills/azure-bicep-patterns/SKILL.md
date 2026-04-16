---
name: azure-bicep-patterns
description: "Reusable Bicep patterns and AVM module examples for Azure Landing Zone deployments. USE FOR: Bicep code generation, module composition, hub-spoke networking. DO NOT USE FOR: Terraform patterns (use terraform-patterns)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: iac-bicep
---

# Azure Bicep Patterns Skill

Reusable Bicep patterns for the ALZ Accelerator.

## Hub-Spoke Network Pattern

```bicep
// Hub VNet with Firewall, Bastion, and Gateway subnets
module hubVnet 'br/public:avm/res/network/virtual-network:0.4.0' = {
  name: 'hub-vnet'
  params: {
    name: 'vnet-hub-${environment}-${location}'
    addressPrefixes: [hubAddressPrefix]
    subnets: [
      { name: 'AzureFirewallSubnet', addressPrefix: firewallSubnetPrefix }
      { name: 'AzureBastionSubnet', addressPrefix: bastionSubnetPrefix }
      { name: 'GatewaySubnet', addressPrefix: gatewaySubnetPrefix }
    ]
    tags: tags
  }
}
```

## Private Endpoint Pattern

```bicep
module privateEndpoint 'br/public:avm/res/network/private-endpoint:0.7.0' = {
  name: 'pe-${resourceName}'
  params: {
    name: 'pe-${resourceName}'
    subnetResourceId: subnetId
    privateLinkServiceConnections: [
      {
        name: 'plsc-${resourceName}'
        privateLinkServiceId: targetResourceId
        groupIds: [groupId]
      }
    ]
    privateDnsZoneGroups: [
      {
        privateDnsZoneGroupConfigs: [
          { privateDnsZoneResourceId: dnsZoneId }
        ]
      }
    ]
    tags: tags
  }
}
```

## Diagnostic Settings Pattern

```bicep
resource diagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diag-${resourceName}'
  scope: targetResource
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      { categoryGroup: 'allLogs', enabled: true }
    ]
    metrics: [
      { category: 'AllMetrics', enabled: true }
    ]
  }
}
```

## Budget Pattern

```bicep
resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-${environment}'
  properties: {
    category: 'Cost'
    amount: budgetAmount
    timeGrain: 'Monthly'
    timePeriod: { startDate: budgetStartDate }
    notifications: {
      forecast80: {
        enabled: true
        threshold: 80
        operator: 'GreaterThanOrEqualTo'
        thresholdType: 'Forecasted'
        contactEmails: alertEmails
      }
      forecast100: {
        enabled: true
        threshold: 100
        operator: 'GreaterThanOrEqualTo'
        thresholdType: 'Forecasted'
        contactEmails: alertEmails
        contactGroups: [actionGroupId]
      }
      forecast120: {
        enabled: true
        threshold: 120
        operator: 'GreaterThanOrEqualTo'
        thresholdType: 'Forecasted'
        contactEmails: alertEmails
        contactGroups: [actionGroupId]
      }
    }
  }
}
```

## Security Baseline Enforcement

Every storage account:
```bicep
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    publicNetworkAccess: environment == 'prod' ? 'Disabled' : 'Enabled'
  }
  identity: { type: 'SystemAssigned' }
}
```

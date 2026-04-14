// Networking Module - VNet, Subnets, NSGs, DDoS Protection, Bastion

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('VNet address space')
param vnetAddressSpace string

@description('Subnet configurations')
param subnets array

@description('Enable DDoS protection plan')
param enableDdos bool

@description('Log Analytics Workspace ID for diagnostics')
param logAnalyticsWorkspaceId string

@description('Tags')
param tags object

@description('Monthly budget amount in USD')
param budgetAmount int

@description('Technical contact email for budget alerts')
param technicalContact string

@description('Environment name')
param environment string

// ============================================================================
// DDoS Protection Plan
// ============================================================================

resource ddosPlan 'Microsoft.Network/ddosProtectionPlans@2024-01-01' = if (enableDdos) {
  name: '${prefix}-ddos-plan'
  location: location
  tags: tags
}

// ============================================================================
// Virtual Network
// ============================================================================

resource vnet 'Microsoft.Network/virtualNetworks@2024-01-01' = {
  name: '${prefix}-vnet'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [vnetAddressSpace]
    }
    ddosProtectionPlan: enableDdos ? { id: ddosPlan.id } : null
    enableDdosProtection: enableDdos
    subnets: [
      for subnet in subnets: {
        name: subnet.name
        properties: {
          addressPrefix: subnet.addressPrefix
          networkSecurityGroup: subnet.name != 'AzureBastionSubnet' ? {
            id: resourceId('Microsoft.Network/networkSecurityGroups', '${prefix}-${subnet.name}-nsg')
          } : null
          serviceEndpoints: contains(subnet, 'serviceEndpoints') ? [
            for se in subnet.serviceEndpoints: { service: se }
          ] : []
          privateEndpointNetworkPolicies: contains(subnet, 'privateEndpointPolicies') && subnet.privateEndpointPolicies ? 'Enabled' : 'Disabled'
        }
      }
    ]
  }
  dependsOn: [nsgs]
}

// ============================================================================
// Network Security Groups
// ============================================================================

resource nsgs 'Microsoft.Network/networkSecurityGroups@2024-01-01' = [
  for subnet in subnets: if (subnet.name != 'AzureBastionSubnet' && contains(subnet, 'nsg') && subnet.nsg) {
    name: '${prefix}-${subnet.name}-nsg'
    location: location
    tags: tags
    properties: {
      securityRules: [
        {
          name: 'DenyAllInbound'
          properties: {
            priority: 4096
            direction: 'Inbound'
            access: 'Deny'
            protocol: '*'
            sourceAddressPrefix: '*'
            sourcePortRange: '*'
            destinationAddressPrefix: '*'
            destinationPortRange: '*'
          }
        }
      ]
    }
  }
]

// ============================================================================
// VNet Diagnostic Settings
// ============================================================================

resource vnetDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${prefix}-vnet-diag'
  scope: vnet
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        categoryGroup: 'allLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// ============================================================================
// Cost Governance
// ============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-networking-${environment}'
  properties: {
    timePeriod: {
      startDate: '2026-01-01'
    }
    timeGrain: 'Monthly'
    amount: budgetAmount
    category: 'Cost'
    notifications: {
      forecast80: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 80
        thresholdType: 'Forecasted'
        contactEmails: [technicalContact]
      }
      forecast100: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Forecasted'
        contactEmails: [technicalContact]
      }
      forecast120: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 120
        thresholdType: 'Forecasted'
        contactEmails: [technicalContact]
      }
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================

output vnetId string = vnet.id
output vnetName string = vnet.name
output subnetIds array = [for (subnet, i) in subnets: vnet.properties.subnets[i].id]

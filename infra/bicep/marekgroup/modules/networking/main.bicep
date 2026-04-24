// Networking Module - VNet, Subnets, NSGs, DDoS Protection
// AVM-first: uses Azure Verified Modules from the public Bicep registry

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

param now string = utcNow('yyyy-MM-01')

// ============================================================================
// DDoS Protection Plan
// ============================================================================

resource ddosPlan 'Microsoft.Network/ddosProtectionPlans@2024-01-01' = if (enableDdos) {
  name: '${prefix}-ddos-plan'
  location: location
  tags: tags
}

// ============================================================================
// Network Security Groups (native — simple resources, no AVM needed)
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
// Virtual Network (AVM)
// ============================================================================

module vnet 'br/public:avm/res/network/virtual-network:0.5.2' = {
  name: '${prefix}-vnet-deployment'
  params: {
    name: '${prefix}-vnet'
    location: location
    tags: tags
    addressPrefixes: [vnetAddressSpace]
    ddosProtectionPlanResourceId: enableDdos ? ddosPlan.id : ''
    subnets: [
      for (subnet, i) in subnets: {
        name: subnet.name
        addressPrefix: subnet.addressPrefix
        networkSecurityGroupResourceId: (subnet.name != 'AzureBastionSubnet' && contains(subnet, 'nsg') && subnet.nsg) ? nsgs[i].id : ''
        serviceEndpoints: subnet.?serviceEndpoints ?? []
        privateEndpointNetworkPolicies: contains(subnet, 'privateEndpointPolicies') && subnet.privateEndpointPolicies ? 'Enabled' : 'Disabled'
      }
    ]
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspaceId
        logCategoriesAndGroups: [
          { categoryGroup: 'allLogs' }
        ]
        metricCategories: [
          { category: 'AllMetrics' }
        ]
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
      startDate: now
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

output vnetId string = vnet.outputs.resourceId
output vnetName string = vnet.outputs.name
output subnetIds array = [for (subnet, i) in subnets: vnet.outputs.subnetResourceIds[i]]

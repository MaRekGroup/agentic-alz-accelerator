// Azure Landing Zone Accelerator - Main Deployment
// Orchestrates all landing zone modules based on profile configuration

targetScope = 'subscription'

// ============================================================================
// Parameters
// ============================================================================

@description('Azure region for the deployment')
param location string = 'southcentralus'

@description('Management group name for the landing zone')
param managementGroupName string

@description('Landing zone profile name')
@allowed(['online', 'corp', 'sandbox', 'sap'])
param profileName string

@description('Virtual network address space')
param vnetAddressSpace string = '10.1.0.0/16'

@description('Subnet configurations')
param subnets array = []

@description('Enable DDoS protection')
param enableDdos bool = false

@description('Enable Defender for Cloud')
param enableDefender bool = true

@description('Defender plan names to enable')
param defenderPlans array = ['VirtualMachines', 'SqlServers', 'Storage', 'KeyVaults']

@description('Log Analytics workspace retention in days')
param logRetentionDays int = 90

@description('Policy initiative names to assign')
param policyInitiatives array = ['Azure Security Benchmark']

@description('Tags applied to all resources')
param tags object = {
  Environment: 'production'
  Owner: 'platform-team'
  CostCenter: 'platform'
  Project: profileName
  ManagedBy: 'agentic-alz-accelerator'
}

@description('Monthly budget amount in USD')
param budgetAmount int

@description('Technical contact email for budget alerts')
param technicalContact string

@description('Project name')
param projectName string

@description('Environment name')
param environment string

// CHANGED: Dynamic budget start date — Azure rejects dates prior to current month
param now string = utcNow('yyyy-MM-01')

// ============================================================================
// Variables
// ============================================================================

var prefix = 'mrg-${managementGroupName}'
var rgNames = {
  networking: '${prefix}-networking-rg'
  security: '${prefix}-security-rg'
  logging: '${prefix}-logging-rg'
}

// ============================================================================
// Resource Groups
// ============================================================================

resource networkingRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgNames.networking
  location: location
  tags: tags
}

resource securityRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgNames.security
  location: location
  tags: tags
}

resource loggingRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgNames.logging
  location: location
  tags: tags
}

// Identity module is subscription-scoped and creates its own RG

// ============================================================================
// Module Deployments
// ============================================================================

module logging 'modules/logging/main.bicep' = {
  name: '${prefix}-logging'
  scope: loggingRg
  params: {
    location: location
    prefix: prefix
    retentionDays: logRetentionDays
    tags: tags
    // CHANGED: Added missing required params for cost governance (BCP035)
    environment: environment
    budgetAmount: budgetAmount
    technicalContact: technicalContact
  }
}

module networking 'modules/networking/main.bicep' = {
  name: '${prefix}-networking'
  scope: networkingRg
  params: {
    location: location
    prefix: prefix
    vnetAddressSpace: vnetAddressSpace
    subnets: subnets
    enableDdos: enableDdos
    logAnalyticsWorkspaceId: logging.outputs.workspaceId
    tags: tags
    // CHANGED: Added missing required params for cost governance (BCP035)
    environment: environment
    budgetAmount: budgetAmount
    technicalContact: technicalContact
  }
}

module security 'modules/security/main.bicep' = {
  name: '${prefix}-security'
  scope: securityRg
  params: {
    location: location
    prefix: prefix
    enableDefender: enableDefender
    defenderPlans: defenderPlans
    logAnalyticsWorkspaceId: logging.outputs.workspaceId
    tags: tags
    // CHANGED: Added missing required params for cost governance (BCP035)
    environment: environment
    budgetAmount: budgetAmount
    technicalContact: technicalContact
  }
}

module identity 'modules/identity/main.bicep' = {
  name: '${prefix}-identity'
  params: {
    location: location
    prefix: prefix
    tags: tags
    environment: environment
    budgetAmount: budgetAmount
    technicalContact: technicalContact
  }
}

module policies 'modules/policies/main.bicep' = {
  name: '${prefix}-policies'
  params: {
    policyInitiatives: policyInitiatives
    managementGroupName: managementGroupName
  }
}

// ============================================================================
// Cost Governance
// ============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-platform-${environment}'
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

output networkingResourceGroup string = networkingRg.name
output vnetId string = networking.outputs.vnetId
output logAnalyticsWorkspaceId string = logging.outputs.workspaceId
output keyVaultId string = security.outputs.keyVaultId

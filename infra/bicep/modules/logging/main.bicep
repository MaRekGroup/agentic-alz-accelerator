// Logging Module - Log Analytics Workspace, Automation Account
// AVM-first: uses Azure Verified Modules from the public Bicep registry

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('Log retention in days')
param retentionDays int

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
// Log Analytics Workspace (AVM)
// ============================================================================

module workspace 'br/public:avm/res/operational-insights/workspace:0.9.1' = {
  name: '${prefix}-law-deployment'
  params: {
    name: '${prefix}-law'
    location: location
    tags: tags
    skuName: 'PerGB2018'
    dataRetention: retentionDays
    useResourcePermissions: true
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Automation Account (AVM)
// ============================================================================

module automationAccount 'br/public:avm/res/automation/automation-account:0.11.0' = {
  name: '${prefix}-automation-deployment'
  params: {
    name: '${prefix}-automation'
    location: location
    tags: tags
    skuName: 'Basic'
    linkedWorkspaceResourceId: workspace.outputs.resourceId
  }
}

// ============================================================================
// Cost Governance
// ============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-logging-${environment}'
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

output workspaceId string = workspace.outputs.resourceId
output workspaceName string = workspace.outputs.name
output workspaceCustomerId string = workspace.outputs.logAnalyticsWorkspaceId

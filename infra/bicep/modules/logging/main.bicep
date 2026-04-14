// Logging Module - Log Analytics Workspace, Diagnostic Settings

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

// ============================================================================
// Log Analytics Workspace
// ============================================================================

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-law'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionDays
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Automation Account (for Log Analytics solutions)
// ============================================================================

resource automationAccount 'Microsoft.Automation/automationAccounts@2023-11-01' = {
  name: '${prefix}-automation'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'Basic'
    }
  }
}

// ============================================================================
// Link Automation Account to Log Analytics
// ============================================================================

resource linkedService 'Microsoft.OperationalInsights/workspaces/linkedServices@2020-08-01' = {
  parent: workspace
  name: 'Automation'
  properties: {
    resourceId: automationAccount.id
  }
}

// ============================================================================
// Activity Log Diagnostic Settings (subscription level - deployed separately)
// ============================================================================

// Note: Activity Log diagnostics require subscription-scope deployment.
// Use the subscription-level module for this.

// ============================================================================
// Cost Governance
// ============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-logging-${environment}'
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

output workspaceId string = workspace.id
output workspaceName string = workspace.name
output workspaceCustomerId string = workspace.properties.customerId

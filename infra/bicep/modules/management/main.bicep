// CAF Design Area: Management
// Log Analytics, Azure Monitor, Backup, Update Management

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('Log retention in days')
param retentionDays int

@description('Enable Azure Sentinel')
param enableSentinel bool = false

@description('Tags')
param tags object

@description('Monthly budget amount in USD')
param budgetAmount int

@description('Technical contact email for budget alerts')
param technicalContact string

@description('Environment name')
param environment string

// CHANGED: utcNow() can only be used as a parameter default value in Bicep
@description('Current UTC timestamp — used to derive budget start date')
param now string = utcNow()

// =============================================================================
// Log Analytics Workspace (Centralized)
// =============================================================================

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-law'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: retentionDays
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// =============================================================================
// Automation Account
// =============================================================================

resource automationAccount 'Microsoft.Automation/automationAccounts@2023-11-01' = {
  name: '${prefix}-automation'
  location: location
  tags: tags
  properties: {
    sku: { name: 'Basic' }
  }
}

resource linkedService 'Microsoft.OperationalInsights/workspaces/linkedServices@2020-08-01' = {
  parent: workspace
  name: 'Automation'
  properties: {
    resourceId: automationAccount.id
  }
}

// =============================================================================
// Azure Monitor Action Group
// =============================================================================

resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: '${prefix}-platform-alerts'
  location: 'global'
  tags: tags
  properties: {
    groupShortName: 'PlatAlerts'
    enabled: true
    emailReceivers: []  // Configured via parameters
  }
}

// =============================================================================
// Activity Log Diagnostic Settings
// =============================================================================

// TODO: Activity log diagnostics is subscription-scoped — move to subscription-level deployment
// Commented out: BadRequest when deployed at RG scope
// resource activityLogDiag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
//   name: '${prefix}-activity-log-diag'
//   properties: {
//     workspaceId: workspace.id
//     logs: [
//       { categoryGroup: 'allLogs', enabled: true }
//     ]
//   }
// }

// =============================================================================
// Microsoft Sentinel (optional) — commented out for initial LAW-only deployment
// =============================================================================

// resource sentinel 'Microsoft.OperationsManagement/solutions@2015-11-01-preview' = if (enableSentinel) {
//   name: 'SecurityInsights(${workspace.name})'
//   location: location
//   tags: tags
//   plan: {
//     name: 'SecurityInsights(${workspace.name})'
//     publisher: 'Microsoft'
//     product: 'OMSGallery/SecurityInsights'
//     promotionCode: ''
//   }
//   properties: {
//     workspaceResourceId: workspace.id
//   }
// }

// =============================================================================
// Cost Governance
// =============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-management-${environment}'
  properties: {
    timePeriod: {
      // CHANGED: Derive current month start from utcNow() param — Azure rejects past start dates
      startDate: '${substring(now, 0, 7)}-01'
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

// =============================================================================
// Outputs
// =============================================================================

output workspaceId string = workspace.id
output workspaceName string = workspace.name
output workspaceCustomerId string = workspace.properties.customerId
output automationAccountId string = automationAccount.id
output actionGroupId string = actionGroup.id

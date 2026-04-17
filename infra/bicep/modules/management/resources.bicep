// Management resources — deployed at resource group scope
// Called from main.bicep (subscription-scoped)

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('Log retention in days')
param retentionDays int

@description('Tags')
param tags object

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
    emailReceivers: []
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

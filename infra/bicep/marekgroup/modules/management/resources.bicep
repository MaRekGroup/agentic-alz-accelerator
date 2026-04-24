// Management resources — deployed at resource group scope
// AVM-first: uses Azure Verified Modules from the public Bicep registry
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
// Log Analytics Workspace (AVM — Centralized)
// =============================================================================

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

// =============================================================================
// Automation Account (AVM)
// =============================================================================

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

output workspaceId string = workspace.outputs.resourceId
output workspaceName string = workspace.outputs.name
output workspaceCustomerId string = workspace.outputs.logAnalyticsWorkspaceId
output automationAccountId string = automationAccount.outputs.resourceId
output actionGroupId string = actionGroup.id

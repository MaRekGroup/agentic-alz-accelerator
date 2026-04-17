// Sentinel Sub-module
// Deploys Microsoft Sentinel on a Log Analytics workspace

@description('Log Analytics workspace resource ID')
param workspaceId string

@description('Enable Threat Intelligence integration')
param enableThreatIntelligence bool

@description('Resource tags')
param tags object

// ─── Microsoft Sentinel Solution ──────────────────────────────────────────────

// Extract workspace name from resource ID for the solution naming
var workspaceName = last(split(workspaceId, '/'))

resource sentinelSolution 'Microsoft.OperationsManagement/solutions@2015-11-01-preview' = {
  name: 'SecurityInsights(${workspaceName})'
  location: resourceGroup().location
  tags: tags
  plan: {
    name: 'SecurityInsights(${workspaceName})'
    publisher: 'Microsoft'
    product: 'OMSGallery/SecurityInsights'
    promotionCode: ''
  }
  properties: {
    workspaceResourceId: workspaceId
  }
}

// ─── Sentinel Onboarding ──────────────────────────────────────────────────────

// Reference the existing workspace to scope Sentinel resources
resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: workspaceName
}

resource sentinelOnboarding 'Microsoft.SecurityInsights/onboardingStates@2024-03-01' = {
  name: 'default'
  scope: workspace
  dependsOn: [sentinelSolution]
  properties: {}
}

// ─── Sentinel Data Connectors ─────────────────────────────────────────────────

// AAD connector requires Directory.Read.All — skipped unless explicitly enabled
// To enable: set enableAadConnector = true and grant the SPN Azure AD read permissions

// ─── Threat Intelligence Data Connector ───────────────────────────────────────

resource tiConnector 'Microsoft.SecurityInsights/dataConnectors@2024-03-01' = if (enableThreatIntelligence) {
  name: 'ThreatIntelligence'
  scope: workspace
  dependsOn: [sentinelOnboarding]
  kind: 'ThreatIntelligence'
  properties: {
    tenantId: subscription().tenantId
    dataTypes: {
      indicators: { state: 'Enabled' }
    }
  }
}

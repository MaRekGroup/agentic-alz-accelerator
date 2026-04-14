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

// ─── Sentinel Data Connectors ─────────────────────────────────────────────────

resource aadConnector 'Microsoft.SecurityInsights/dataConnectors@2024-03-01' = {
  name: 'AzureActiveDirectory'
  scope: sentinelSolution
  kind: 'AzureActiveDirectory'
  properties: {
    tenantId: subscription().tenantId
    dataTypes: {
      alerts: { state: 'Enabled' }
    }
  }
}

// ─── Threat Intelligence Data Connector ───────────────────────────────────────

resource tiConnector 'Microsoft.SecurityInsights/dataConnectors@2024-03-01' = if (enableThreatIntelligence) {
  name: 'ThreatIntelligence'
  scope: sentinelSolution
  kind: 'MicrosoftThreatIntelligence'
  properties: {
    tenantId: subscription().tenantId
    dataTypes: {
      microsoftEmergingThreatFeed: { lookbackPeriod: '1970-01-01T00:00:00Z', state: 'Enabled' }
    }
  }
}

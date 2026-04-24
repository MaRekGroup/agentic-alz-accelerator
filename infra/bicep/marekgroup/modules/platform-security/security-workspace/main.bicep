// Security Workspace Sub-module
// Deploys a dedicated Log Analytics workspace for security operations

@description('Azure region')
param location string

@description('Workspace name')
param workspaceName string

@description('Log retention in days')
param retentionDays int

@description('Resource tags')
param tags object

// ─── Security Log Analytics Workspace ─────────────────────────────────────────

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
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

// ─── Outputs ──────────────────────────────────────────────────────────────────

output workspaceId string = workspace.id
output workspaceName string = workspace.name
output workspaceCustomerId string = workspace.properties.customerId

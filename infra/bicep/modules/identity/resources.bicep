// Identity resources — deployed at resource group scope
// Called from main.bicep (subscription-scoped)

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('Tags')
param tags object

// ============================================================================
// User-Assigned Managed Identity (for landing zone workloads)
// ============================================================================

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${prefix}-identity'
  location: location
  tags: tags
}

// ============================================================================
// Managed Identity for ALZ Agent operations
// ============================================================================

resource agentIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${prefix}-agent-identity'
  location: location
  tags: union(tags, {
    purpose: 'mrg-agent-operations'
  })
}

// ============================================================================
// Outputs
// ============================================================================

output managedIdentityId string = managedIdentity.id
output managedIdentityPrincipalId string = managedIdentity.properties.principalId
output managedIdentityClientId string = managedIdentity.properties.clientId
output agentIdentityId string = agentIdentity.id
output agentIdentityPrincipalId string = agentIdentity.properties.principalId

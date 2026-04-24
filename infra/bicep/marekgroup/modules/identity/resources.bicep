// Identity resources — deployed at resource group scope
// AVM-first: uses Azure Verified Modules from the public Bicep registry
// Called from main.bicep (subscription-scoped)

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('Tags')
param tags object

// ============================================================================
// User-Assigned Managed Identity (AVM) — for landing zone workloads
// ============================================================================

module managedIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${prefix}-identity-deployment'
  params: {
    name: '${prefix}-identity'
    location: location
    tags: tags
  }
}

// ============================================================================
// Managed Identity (AVM) — for ALZ Agent operations
// ============================================================================

module agentIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${prefix}-agent-identity-deployment'
  params: {
    name: '${prefix}-agent-identity'
    location: location
    tags: union(tags, {
      purpose: 'mrg-agent-operations'
    })
  }
}

// ============================================================================
// Outputs
// ============================================================================

output managedIdentityId string = managedIdentity.outputs.resourceId
output managedIdentityPrincipalId string = managedIdentity.outputs.principalId
output managedIdentityClientId string = managedIdentity.outputs.clientId
output agentIdentityId string = agentIdentity.outputs.resourceId
output agentIdentityPrincipalId string = agentIdentity.outputs.principalId

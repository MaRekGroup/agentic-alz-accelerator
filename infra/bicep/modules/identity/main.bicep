// Identity Module - Managed Identities and RBAC Assignments

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

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
    purpose: 'alz-agent-operations'
  })
}

// ============================================================================
// Role Assignments
// ============================================================================

// Reader role for the agent at subscription scope
resource agentReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, agentIdentity.id, 'Reader')
  properties: {
    principalId: agentIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7') // Reader
    principalType: 'ServicePrincipal'
  }
}

// Policy Contributor for policy management
resource agentPolicyRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, agentIdentity.id, 'ResourcePolicyContributor')
  properties: {
    principalId: agentIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '36243c78-bf99-498c-9df9-86d9f8d28608') // Resource Policy Contributor
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Cost Governance
// ============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-identity-${environment}'
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

output managedIdentityId string = managedIdentity.id
output managedIdentityPrincipalId string = managedIdentity.properties.principalId
output managedIdentityClientId string = managedIdentity.properties.clientId
output agentIdentityId string = agentIdentity.id
output agentIdentityPrincipalId string = agentIdentity.properties.principalId

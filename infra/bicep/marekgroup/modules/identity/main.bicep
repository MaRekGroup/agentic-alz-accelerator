// Identity Module - Managed Identities and RBAC Assignments
// Subscription-scoped: creates its own RG using the prefix convention

targetScope = 'subscription'

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

@description('Deploy spoke VNet for identity workloads')
param deploySpokeVnet bool = true

@description('Spoke VNet address space')
param spokeVnetAddressSpace string = '10.1.0.0/24'

@description('Hub VNet resource ID for peering (from connectivity subscription)')
param hubVnetId string = ''

@description('Log Analytics Workspace ID for diagnostics')
param logAnalyticsWorkspaceId string = ''

param now string = utcNow('yyyy-MM-01')

// ─── Variables ──────────────────────────────────────────────────────────────

var regionShortcode = {
  eastus: 'eus'
  eastus2: 'eus2'
  westus: 'wus'
  westus2: 'wus2'
  westus3: 'wus3'
  centralus: 'cus'
  southcentralus: 'scus'
  northeurope: 'neu'
  westeurope: 'weu'
  uksouth: 'uks'
  southeastasia: 'sea'
  australiaeast: 'aue'
  japaneast: 'jpe'
}[location] ?? location

var rgName = '${prefix}-identity-${regionShortcode}-rg'

// ─── Resource Group ─────────────────────────────────────────────────────────

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgName
  location: location
  tags: tags
}

// ─── Identity Resources (RG-scoped module) ──────────────────────────────────

module identityResources 'resources.bicep' = {
  name: 'identity-resources-deployment'
  scope: rg
  params: {
    location: location
    prefix: prefix
    tags: tags
  }
}

// ─── Spoke VNet (RG-scoped module) ──────────────────────────────────────────

module spokeVnet 'spoke-vnet.bicep' = if (deploySpokeVnet && hubVnetId != '') {
  name: 'identity-spoke-vnet-deployment'
  scope: rg
  params: {
    location: location
    prefix: prefix
    spokeVnetAddressSpace: spokeVnetAddressSpace
    hubVnetId: hubVnetId
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
    tags: tags
  }
}

// ============================================================================
// Role Assignments (subscription-scoped)
// ============================================================================

// Reader role for the agent at subscription scope
resource agentReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, '${prefix}-agent-identity', 'Reader')
  properties: {
    principalId: identityResources.outputs.agentIdentityPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7') // Reader
    principalType: 'ServicePrincipal'
  }
}

// Policy Contributor for policy management
resource agentPolicyRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, '${prefix}-agent-identity', 'ResourcePolicyContributor')
  properties: {
    principalId: identityResources.outputs.agentIdentityPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '36243c78-bf99-498c-9df9-86d9f8d28608') // Resource Policy Contributor
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Cost Governance (subscription-scoped)
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

output resourceGroupName string = rg.name
output managedIdentityId string = identityResources.outputs.managedIdentityId
output managedIdentityPrincipalId string = identityResources.outputs.managedIdentityPrincipalId
output managedIdentityClientId string = identityResources.outputs.managedIdentityClientId
output agentIdentityId string = identityResources.outputs.agentIdentityId
output agentIdentityPrincipalId string = identityResources.outputs.agentIdentityPrincipalId
output spokeVnetId string = spokeVnet.?outputs.?spokeVnetId ?? ''
output domainControllersSubnetId string = spokeVnet.?outputs.?domainControllersSubnetId ?? ''
output identityServicesSubnetId string = spokeVnet.?outputs.?identityServicesSubnetId ?? ''

// Security Module - Key Vault, Defender for Cloud
// AVM-first: uses Azure Verified Modules from the public Bicep registry

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('Enable Defender for Cloud')
#disable-next-line no-unused-params
param enableDefender bool

@description('Defender plan names')
#disable-next-line no-unused-params
param defenderPlans array

@description('Log Analytics Workspace ID')
param logAnalyticsWorkspaceId string

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
// Key Vault (AVM)
// ============================================================================

module keyVault 'br/public:avm/res/key-vault/vault:0.11.0' = {
  name: '${prefix}-kv-deployment'
  params: {
    name: '${prefix}-kv'
    location: location
    tags: tags
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspaceId
        logCategoriesAndGroups: [
          { categoryGroup: 'allLogs' }
        ]
        metricCategories: [
          { category: 'AllMetrics' }
        ]
      }
    ]
  }
}

// ============================================================================
// Defender for Cloud
// ============================================================================

// TODO: Defender resources are subscription-scoped — move to a subscription-level deployment

// ============================================================================
// Cost Governance
// ============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-security-${environment}'
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

output keyVaultId string = keyVault.outputs.resourceId
output keyVaultName string = keyVault.outputs.name
output keyVaultUri string = keyVault.outputs.uri

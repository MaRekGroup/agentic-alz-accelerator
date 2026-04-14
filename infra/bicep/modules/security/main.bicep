// Security Module - Key Vault, Defender for Cloud, Sentinel

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('Enable Defender for Cloud')
param enableDefender bool

@description('Defender plan names')
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

// ============================================================================
// Key Vault
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${prefix}-kv'
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

// ============================================================================
// Defender for Cloud
// ============================================================================

resource defenderPricing 'Microsoft.Security/pricings@2024-01-01' = [
  for plan in defenderPlans: if (enableDefender) {
    name: plan
    properties: {
      pricingTier: 'Standard'
    }
  }
]

// ============================================================================
// Security Center Auto Provisioning
// ============================================================================

resource autoProvisioning 'Microsoft.Security/autoProvisioningSettings@2017-08-01-preview' = if (enableDefender) {
  name: 'default'
  properties: {
    autoProvision: 'On'
  }
}

// ============================================================================
// Security Center Workspace Settings
// ============================================================================

resource workspaceSettings 'Microsoft.Security/workspaceSettings@2017-08-01-preview' = if (enableDefender) {
  name: 'default'
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    scope: subscription().id
  }
}

// ============================================================================
// Key Vault Diagnostic Settings
// ============================================================================

resource kvDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${prefix}-kv-diag'
  scope: keyVault
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        categoryGroup: 'allLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// ============================================================================
// Cost Governance
// ============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-security-${environment}'
  properties: {
    timePeriod: {
      startDate: '2026-01-01'
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

output keyVaultId string = keyVault.id
output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri

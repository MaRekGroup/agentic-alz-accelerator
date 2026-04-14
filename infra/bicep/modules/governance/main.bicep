// CAF Design Area: Governance
// Azure Policy, Cost Management, compliance enforcement

targetScope = 'subscription'

@description('Policy initiative names to assign')
param policyInitiatives array

@description('Management group name')
param managementGroupName string

@description('Monthly budget amount in USD')
param budgetAmount int

@description('Technical contact email for budget alerts')
param technicalContact string

@description('Project name for budget naming')
param projectName string

@description('Environment name')
param environment string

// =============================================================================
// Built-in Policy Initiative Assignments
// =============================================================================

var initiativeIds = {
  'Azure Security Benchmark': '/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8'
  'CIS Microsoft Azure Foundations Benchmark': '/providers/Microsoft.Authorization/policySetDefinitions/612b5213-9160-4969-8578-1518bd2a000c'
  'ISO 27001:2013': '/providers/Microsoft.Authorization/policySetDefinitions/89c6cddc-1c73-4ac1-b19c-54d1a15a42f2'
  'NIST SP 800-53 Rev. 5': '/providers/Microsoft.Authorization/policySetDefinitions/179d1daa-458f-4e47-8086-2a68d0d6c38f'
}

resource initiativeAssignments 'Microsoft.Authorization/policyAssignments@2024-04-01' = [
  for initiative in policyInitiatives: if (contains(initiativeIds, initiative)) {
    name: 'alz-${toLower(replace(initiative, ' ', '-'))}'
    location: deployment().location
    identity: {
      type: 'SystemAssigned'
    }
    properties: {
      displayName: '${initiative} - ALZ ${managementGroupName}'
      policyDefinitionId: initiativeIds[initiative]
      enforcementMode: 'Default'
    }
  }
]

// =============================================================================
// Custom Policy: Deny Public IP on NIC
// =============================================================================

resource denyPublicIpPolicy 'Microsoft.Authorization/policyDefinitions@2024-05-01' = {
  name: 'alz-deny-public-ip-on-nic'
  properties: {
    displayName: 'Deny Public IP addresses on NICs'
    policyType: 'Custom'
    mode: 'All'
    policyRule: {
      if: {
        allOf: [
          { field: 'type', equals: 'Microsoft.Network/networkInterfaces' }
          {
            count: {
              field: 'Microsoft.Network/networkInterfaces/ipconfigurations[*]'
              where: {
                field: 'Microsoft.Network/networkInterfaces/ipconfigurations[*].publicIpAddress.id'
                notEquals: ''
              }
            }
            greaterOrEquals: 1
          }
        ]
      }
      then: { effect: 'Deny' }
    }
  }
}

// =============================================================================
// Custom Policy: Require TLS 1.2 (Security Baseline Rule #1)
// =============================================================================

resource requireTlsPolicy 'Microsoft.Authorization/policyDefinitions@2024-05-01' = {
  name: 'alz-require-tls-1-2'
  properties: {
    displayName: 'Require minimum TLS version 1.2'
    policyType: 'Custom'
    mode: 'All'
    policyRule: {
      if: {
        allOf: [
          {
            field: 'type'
            in: ['Microsoft.Storage/storageAccounts', 'Microsoft.Web/sites', 'Microsoft.Sql/servers']
          }
          {
            anyOf: [
              { field: 'Microsoft.Storage/storageAccounts/minimumTlsVersion', notEquals: 'TLS1_2' }
              { field: 'Microsoft.Web/sites/siteConfig.minTlsVersion', notEquals: '1.2' }
            ]
          }
        ]
      }
      then: { effect: 'Deny' }
    }
  }
}

// =============================================================================
// Custom Policy: Enforce HTTPS (Security Baseline Rule #2)
// =============================================================================

resource enforceHttpsPolicy 'Microsoft.Authorization/policyDefinitions@2024-05-01' = {
  name: 'alz-enforce-https'
  properties: {
    displayName: 'Enforce HTTPS for web applications'
    policyType: 'Custom'
    mode: 'All'
    policyRule: {
      if: {
        allOf: [
          { field: 'type', equals: 'Microsoft.Web/sites' }
          { field: 'Microsoft.Web/sites/httpsOnly', notEquals: true }
        ]
      }
      then: { effect: 'Deny' }
    }
  }
}

// =============================================================================
// Custom Policy: Deny Public Blob Access (Security Baseline Rule #3)
// =============================================================================

resource denyPublicBlobPolicy 'Microsoft.Authorization/policyDefinitions@2024-05-01' = {
  name: 'alz-deny-public-blob-access'
  properties: {
    displayName: 'Deny public blob access on storage accounts'
    policyType: 'Custom'
    mode: 'All'
    policyRule: {
      if: {
        allOf: [
          { field: 'type', equals: 'Microsoft.Storage/storageAccounts' }
          { field: 'Microsoft.Storage/storageAccounts/allowBlobPublicAccess', notEquals: false }
        ]
      }
      then: { effect: 'Deny' }
    }
  }
}

// =============================================================================
// Custom Policy: Require Tags
// =============================================================================

resource requireTagsPolicy 'Microsoft.Authorization/policyDefinitions@2024-05-01' = {
  name: 'alz-require-mandatory-tags'
  properties: {
    displayName: 'Require mandatory tags on resource groups'
    policyType: 'Custom'
    mode: 'All'
    parameters: {
      tagName: {
        type: 'String'
        metadata: { displayName: 'Tag name' }
      }
    }
    policyRule: {
      if: {
        allOf: [
          { field: 'type', equals: 'Microsoft.Resources/subscriptions/resourceGroups' }
          { field: '[concat(\'tags[\', parameters(\'tagName\'), \']\')]', exists: false }
        ]
      }
      then: { effect: 'Deny' }
    }
  }
}

// =============================================================================
// Cost Governance: Budget with Forecast Alerts (APEX Pattern)
// =============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-${projectName}-${environment}'
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

// =============================================================================
// Outputs
// =============================================================================

output budgetId string = budget.id
output policyAssignmentCount int = length(policyInitiatives)

// Policies Module - Azure Policy Assignments and Custom Definitions

targetScope = 'subscription'

@description('Policy initiative names to assign')
param policyInitiatives array

@description('Management group name')
param managementGroupName string

// ============================================================================
// Built-in Policy Initiative IDs
// ============================================================================

var initiativeIds = {
  'Azure Security Benchmark': '/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8'
  'CIS Microsoft Azure Foundations Benchmark': '/providers/Microsoft.Authorization/policySetDefinitions/612b5213-9160-4969-8578-1518bd2a000c'
  'ISO 27001:2013': '/providers/Microsoft.Authorization/policySetDefinitions/89c6cddc-1c73-4ac1-b19c-54d1a15a42f2'
  'NIST SP 800-53 Rev. 5': '/providers/Microsoft.Authorization/policySetDefinitions/179d1daa-458f-4e47-8086-2a68d0d6c38f'
}

// ============================================================================
// Policy Initiative Assignments
// ============================================================================

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
      parameters: {}
    }
  }
]

// ============================================================================
// Custom Policy: Deny Public IP on NIC
// ============================================================================

resource denyPublicIpPolicy 'Microsoft.Authorization/policyDefinitions@2024-05-01' = {
  name: 'alz-deny-public-ip-on-nic'
  properties: {
    displayName: 'Deny Public IP addresses on NICs'
    description: 'Prevents association of public IP addresses with network interfaces'
    policyType: 'Custom'
    mode: 'All'
    parameters: {}
    policyRule: {
      if: {
        allOf: [
          {
            field: 'type'
            equals: 'Microsoft.Network/networkInterfaces'
          }
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
      then: {
        effect: 'Deny'
      }
    }
  }
}

// ============================================================================
// Custom Policy: Require TLS 1.2
// ============================================================================

resource requireTlsPolicy 'Microsoft.Authorization/policyDefinitions@2024-05-01' = {
  name: 'alz-require-tls-1-2'
  properties: {
    displayName: 'Require minimum TLS version 1.2'
    description: 'Ensures all supported resources use TLS 1.2 or higher'
    policyType: 'Custom'
    mode: 'All'
    parameters: {}
    policyRule: {
      if: {
        allOf: [
          {
            field: 'type'
            in: [
              'Microsoft.Storage/storageAccounts'
              'Microsoft.Web/sites'
              'Microsoft.Sql/servers'
            ]
          }
          {
            anyOf: [
              {
                field: 'Microsoft.Storage/storageAccounts/minimumTlsVersion'
                notEquals: 'TLS1_2'
              }
              {
                field: 'Microsoft.Web/sites/siteConfig.minTlsVersion'
                notEquals: '1.2'
              }
            ]
          }
        ]
      }
      then: {
        effect: 'Deny'
      }
    }
  }
}

// ============================================================================
// Custom Policy: Enforce HTTPS
// ============================================================================

resource enforceHttpsPolicy 'Microsoft.Authorization/policyDefinitions@2024-05-01' = {
  name: 'alz-enforce-https'
  properties: {
    displayName: 'Enforce HTTPS for web applications'
    description: 'Ensures web applications are only accessible via HTTPS'
    policyType: 'Custom'
    mode: 'All'
    parameters: {}
    policyRule: {
      if: {
        allOf: [
          {
            field: 'type'
            equals: 'Microsoft.Web/sites'
          }
          {
            field: 'Microsoft.Web/sites/httpsOnly'
            notEquals: true
          }
        ]
      }
      then: {
        effect: 'Deny'
      }
    }
  }
}

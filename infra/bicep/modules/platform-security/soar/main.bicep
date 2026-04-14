// SOAR Playbooks Sub-module
// Deploys Logic App workflows for automated incident response

@description('Azure region')
param location string

@description('Resource naming prefix')
param prefix string

@description('Sentinel workspace resource ID for playbook triggers')
param sentinelWorkspaceId string

@description('Resource tags')
param tags object

// ─── Managed Identity for SOAR Operations ─────────────────────────────────────

resource soarIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${prefix}-soar-mi'
  location: location
  tags: tags
}

// ─── Playbook: Block Suspicious IP ────────────────────────────────────────────

resource blockIpPlaybook 'Microsoft.Logic/workflows@2019-05-01' = {
  name: '${prefix}-soar-block-ip'
  location: location
  tags: union(tags, { soar_playbook: 'Block-SuspiciousIP' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${soarIdentity.id}': {}
    }
  }
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      triggers: {
        'Microsoft_Sentinel_incident': {
          type: 'ApiConnectionWebhook'
          inputs: {}
        }
      }
      actions: {}
    }
  }
}

// ─── Playbook: Isolate Compromised VM ─────────────────────────────────────────

resource isolateVmPlaybook 'Microsoft.Logic/workflows@2019-05-01' = {
  name: '${prefix}-soar-isolate-vm'
  location: location
  tags: union(tags, { soar_playbook: 'Isolate-CompromisedVM' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${soarIdentity.id}': {}
    }
  }
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      triggers: {
        'Microsoft_Sentinel_incident': {
          type: 'ApiConnectionWebhook'
          inputs: {}
        }
      }
      actions: {}
    }
  }
}

// ─── Playbook: Revoke Entra ID Session ────────────────────────────────────────

resource revokeSessionPlaybook 'Microsoft.Logic/workflows@2019-05-01' = {
  name: '${prefix}-soar-revoke-session'
  location: location
  tags: union(tags, { soar_playbook: 'Revoke-EntraIDSession' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${soarIdentity.id}': {}
    }
  }
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      triggers: {
        'Microsoft_Sentinel_incident': {
          type: 'ApiConnectionWebhook'
          inputs: {}
        }
      }
      actions: {}
    }
  }
}

// ─── Playbook: Enrich Incident with Threat Intelligence ───────────────────────

resource enrichTiPlaybook 'Microsoft.Logic/workflows@2019-05-01' = {
  name: '${prefix}-soar-enrich-ti'
  location: location
  tags: union(tags, { soar_playbook: 'Enrich-IncidentWithThreatIntel' })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${soarIdentity.id}': {}
    }
  }
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      triggers: {
        'Microsoft_Sentinel_incident': {
          type: 'ApiConnectionWebhook'
          inputs: {}
        }
      }
      actions: {}
    }
  }
}

// ─── Outputs ──────────────────────────────────────────────────────────────────

output soarIdentityId string = soarIdentity.id
output soarIdentityPrincipalId string = soarIdentity.properties.principalId
output playbookIds object = {
  blockIp: blockIpPlaybook.id
  isolateVm: isolateVmPlaybook.id
  revokeSession: revokeSessionPlaybook.id
  enrichTi: enrichTiPlaybook.id
}

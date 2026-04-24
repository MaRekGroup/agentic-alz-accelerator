// CAF Design Area: Billing & Tenant
// Management group hierarchy and subscription organization

targetScope = 'managementGroup'

@description('Top-level management group prefix')
param prefix string

@description('Existing parent management group ID (usually Tenant Root Group)')
param parentManagementGroupId string = ''

@description('Tags applied to management group metadata')
param tags object = {}

// =============================================================================
// Management Group Hierarchy (Enterprise-Scale)
// =============================================================================

// Level 1: Intermediate root
resource intermediateRoot 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}'
  properties: {
    displayName: '${prefix} - Enterprise Root'
    details: parentManagementGroupId != '' ? {
      parent: {
        id: '/providers/Microsoft.Management/managementGroups/${parentManagementGroupId}'
      }
    } : null
  }
}

// Level 2: Platform
resource platformMg 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}-platform'
  properties: {
    displayName: 'Platform'
    details: {
      parent: {
        id: intermediateRoot.id
      }
    }
  }
}

// Level 2: Landing Zones
resource landingZonesMg 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}-landingzones'
  properties: {
    displayName: 'Landing Zones'
    details: {
      parent: {
        id: intermediateRoot.id
      }
    }
  }
}

// Level 2: Sandbox
resource sandboxMg 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}-sandbox'
  properties: {
    displayName: 'Sandbox'
    details: {
      parent: {
        id: intermediateRoot.id
      }
    }
  }
}

// Level 2: Decommissioned
resource decommissionedMg 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}-decommissioned'
  properties: {
    displayName: 'Decommissioned'
    details: {
      parent: {
        id: intermediateRoot.id
      }
    }
  }
}

// Level 3: Platform children
resource identityMg 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}-platform-identity'
  properties: {
    displayName: 'Identity'
    details: {
      parent: {
        id: platformMg.id
      }
    }
  }
}

resource managementMg 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}-platform-management'
  properties: {
    displayName: 'Management'
    details: {
      parent: {
        id: platformMg.id
      }
    }
  }
}

resource connectivityMg 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}-platform-connectivity'
  properties: {
    displayName: 'Connectivity'
    details: {
      parent: {
        id: platformMg.id
      }
    }
  }
}

// Level 3: Landing Zone children
resource corpMg 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}-landingzones-corp'
  properties: {
    displayName: 'Corp'
    details: {
      parent: {
        id: landingZonesMg.id
      }
    }
  }
}

resource onlineMg 'Microsoft.Management/managementGroups@2023-04-01' = {
  name: '${prefix}-landingzones-online'
  properties: {
    displayName: 'Online'
    details: {
      parent: {
        id: landingZonesMg.id
      }
    }
  }
}

// =============================================================================
// Outputs
// =============================================================================

output intermediateRootId string = intermediateRoot.id
output platformMgId string = platformMg.id
output landingZonesMgId string = landingZonesMg.id
output corpMgId string = corpMg.id
output onlineMgId string = onlineMg.id
output sandboxMgId string = sandboxMg.id
output identityMgId string = identityMg.id
output managementMgId string = managementMg.id
output connectivityMgId string = connectivityMg.id

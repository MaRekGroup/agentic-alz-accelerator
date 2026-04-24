// Virtual WAN Topology Sub-module
// Deploys Azure Virtual WAN, Virtual Hub, and secured hub (with Firewall)

@description('Azure region')
param location string

@description('Resource naming prefix')
param prefix string

@description('Virtual WAN type')
@allowed(['Basic', 'Standard'])
param vwanType string

@description('Deploy Azure Firewall in secured hub')
param deployAzureFirewall bool

@description('Azure Firewall SKU tier')
@allowed(['Standard', 'Premium'])
param firewallSkuTier string

@description('Log Analytics Workspace ID')
param logAnalyticsWorkspaceId string

@description('Resource tags')
param tags object

// ─── Virtual WAN ──────────────────────────────────────────────────────────────

resource virtualWan 'Microsoft.Network/virtualWans@2024-01-01' = {
  name: '${prefix}-vwan'
  location: location
  tags: tags
  properties: {
    type: vwanType
    allowBranchToBranchTraffic: true
    disableVpnEncryption: false
  }
}

// ─── Virtual Hub ──────────────────────────────────────────────────────────────

resource virtualHub 'Microsoft.Network/virtualHubs@2024-01-01' = {
  name: '${prefix}-vhub-${location}'
  location: location
  tags: tags
  properties: {
    virtualWan: {
      id: virtualWan.id
    }
    addressPrefix: '10.0.0.0/23'
    sku: 'Standard'
  }
}

// ─── Firewall Policy (for secured hub) ────────────────────────────────────────

resource firewallPolicy 'Microsoft.Network/firewallPolicies@2024-01-01' = if (deployAzureFirewall) {
  name: '${prefix}-vwan-fw-policy'
  location: location
  tags: tags
  properties: {
    sku: {
      tier: firewallSkuTier
    }
    threatIntelMode: 'Deny'
    dnsSettings: {
      enableProxy: true
    }
  }
}

// ─── Azure Firewall (Secured Virtual Hub) ─────────────────────────────────────

resource azureFirewall 'Microsoft.Network/azureFirewalls@2024-01-01' = if (deployAzureFirewall) {
  name: '${prefix}-vwan-fw'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'AZFW_Hub'
      tier: firewallSkuTier
    }
    virtualHub: {
      id: virtualHub.id
    }
    firewallPolicy: {
      id: firewallPolicy.id
    }
    hubIPAddresses: {
      publicIPs: {
        count: 1
      }
    }
  }
}

// ─── Diagnostics ──────────────────────────────────────────────────────────────

resource vwanDiag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${prefix}-vwan-diag'
  scope: virtualWan
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      { categoryGroup: 'allLogs', enabled: true }
    ]
    metrics: [
      { category: 'AllMetrics', enabled: true }
    ]
  }
}

// ─── Outputs ──────────────────────────────────────────────────────────────────

output vwanId string = virtualWan.id
output vhubId string = virtualHub.id
output firewallId string = deployAzureFirewall ? azureFirewall.id : ''

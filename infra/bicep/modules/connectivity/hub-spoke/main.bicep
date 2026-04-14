// Hub-Spoke Topology Sub-module
// Deploys Hub VNet, Azure Firewall, Bastion

@description('Azure region')
param location string

@description('Resource naming prefix')
param prefix string

@description('Hub VNet address space')
param hubVnetAddressSpace string

@description('Deploy Azure Firewall')
param deployAzureFirewall bool

@description('Azure Firewall SKU tier')
@allowed(['Standard', 'Premium'])
param firewallSkuTier string

@description('Deploy Azure Bastion')
param enableBastion bool

@description('Bastion SKU')
@allowed(['Basic', 'Standard'])
param bastionSku string

@description('DDoS Protection Plan resource ID')
param ddosProtectionPlanId string

@description('Log Analytics Workspace ID for diagnostics')
param logAnalyticsWorkspaceId string

@description('Resource tags')
param tags object

// ─── Variables ────────────────────────────────────────────────────────────────

var hubSubnets = [
  {
    name: 'AzureFirewallSubnet'
    addressPrefix: cidrSubnet(hubVnetAddressSpace, 26, 0) // /26 for firewall
  }
  {
    name: 'AzureFirewallManagementSubnet'
    addressPrefix: cidrSubnet(hubVnetAddressSpace, 26, 1)
  }
  {
    name: 'AzureBastionSubnet'
    addressPrefix: cidrSubnet(hubVnetAddressSpace, 26, 2)
  }
  {
    name: 'GatewaySubnet'
    addressPrefix: cidrSubnet(hubVnetAddressSpace, 27, 6)
  }
  {
    name: 'DnsResolverInbound'
    addressPrefix: cidrSubnet(hubVnetAddressSpace, 28, 14)
  }
  {
    name: 'DnsResolverOutbound'
    addressPrefix: cidrSubnet(hubVnetAddressSpace, 28, 15)
  }
]

// ─── Hub Virtual Network ──────────────────────────────────────────────────────

resource hubVnet 'Microsoft.Network/virtualNetworks@2024-01-01' = {
  name: '${prefix}-hub-vnet'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [hubVnetAddressSpace]
    }
    ddosProtectionPlan: ddosProtectionPlanId != '' ? { id: ddosProtectionPlanId } : null
    enableDdosProtection: ddosProtectionPlanId != ''
    subnets: [
      for subnet in hubSubnets: {
        name: subnet.name
        properties: {
          addressPrefix: subnet.addressPrefix
        }
      }
    ]
  }
}

// ─── Azure Firewall ───────────────────────────────────────────────────────────

resource firewallPip 'Microsoft.Network/publicIPAddresses@2024-01-01' = if (deployAzureFirewall) {
  name: '${prefix}-fw-pip'
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Regional'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
    publicIPAddressVersion: 'IPv4'
  }
  zones: ['1', '2', '3']
}

resource firewallPolicy 'Microsoft.Network/firewallPolicies@2024-01-01' = if (deployAzureFirewall) {
  name: '${prefix}-fw-policy'
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
    intrusionDetection: firewallSkuTier == 'Premium' ? {
      mode: 'Deny'
    } : null
  }
}

resource firewall 'Microsoft.Network/azureFirewalls@2024-01-01' = if (deployAzureFirewall) {
  name: '${prefix}-fw'
  location: location
  tags: tags
  zones: ['1', '2', '3']
  properties: {
    sku: {
      name: 'AZFW_VNet'
      tier: firewallSkuTier
    }
    firewallPolicy: {
      id: firewallPolicy.id
    }
    ipConfigurations: [
      {
        name: 'fw-ipconfig'
        properties: {
          subnet: {
            id: hubVnet.properties.subnets[0].id // AzureFirewallSubnet
          }
          publicIPAddress: {
            id: firewallPip.id
          }
        }
      }
    ]
  }
}

// ─── Firewall Diagnostics ─────────────────────────────────────────────────────

resource firewallDiag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (deployAzureFirewall) {
  name: '${prefix}-fw-diag'
  scope: firewall
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

// ─── Azure Bastion ────────────────────────────────────────────────────────────

resource bastionPip 'Microsoft.Network/publicIPAddresses@2024-01-01' = if (enableBastion) {
  name: '${prefix}-bastion-pip'
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Regional'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource bastion 'Microsoft.Network/bastionHosts@2024-01-01' = if (enableBastion) {
  name: '${prefix}-bastion'
  location: location
  tags: tags
  sku: {
    name: bastionSku
  }
  properties: {
    ipConfigurations: [
      {
        name: 'bastion-ipconfig'
        properties: {
          subnet: {
            id: hubVnet.properties.subnets[2].id // AzureBastionSubnet
          }
          publicIPAddress: {
            id: bastionPip.id
          }
        }
      }
    ]
  }
}

// ─── Hub VNet Diagnostics ─────────────────────────────────────────────────────

resource hubVnetDiag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${prefix}-hub-vnet-diag'
  scope: hubVnet
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

output hubVnetId string = hubVnet.id
output hubVnetName string = hubVnet.name
output firewallPrivateIp string = deployAzureFirewall ? firewall.properties.ipConfigurations[0].properties.privateIPAddress : ''
output firewallPolicyId string = deployAzureFirewall ? firewallPolicy.id : ''
output gatewaySubnetId string = hubVnet.properties.subnets[3].id
output dnsInboundSubnetId string = hubVnet.properties.subnets[4].id
output dnsOutboundSubnetId string = hubVnet.properties.subnets[5].id
output bastionId string = enableBastion ? bastion.id : ''

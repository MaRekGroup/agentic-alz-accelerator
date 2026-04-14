// Private DNS Zones Sub-module
// Deploys Private DNS zones and links them to the hub VNet

@description('Resource naming prefix')
param prefix string

@description('Private DNS zone names to deploy')
param privateDnsZones array

@description('Hub VNet resource ID for DNS zone linking')
param hubVnetId string

@description('Resource tags')
param tags object

// ─── Private DNS Zones ────────────────────────────────────────────────────────

resource dnsZones 'Microsoft.Network/privateDnsZones@2024-06-01' = [
  for zone in privateDnsZones: {
    name: zone
    location: 'global'
    tags: tags
  }
]

// ─── VNet Links ───────────────────────────────────────────────────────────────

resource vnetLinks 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = [
  for (zone, i) in privateDnsZones: if (hubVnetId != '') {
    parent: dnsZones[i]
    name: '${prefix}-hub-link'
    location: 'global'
    tags: tags
    properties: {
      virtualNetwork: {
        id: hubVnetId
      }
      registrationEnabled: false
    }
  }
]

// ─── Outputs ──────────────────────────────────────────────────────────────────

output zoneIds array = [for (zone, i) in privateDnsZones: dnsZones[i].id]
output zoneNames array = [for (zone, i) in privateDnsZones: dnsZones[i].name]

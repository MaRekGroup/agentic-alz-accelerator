// Gateways Sub-module
// Deploys ExpressRoute and/or VPN Gateways

@description('Azure region')
param location string

@description('Resource naming prefix')
param prefix string

@description('Gateway subnet resource ID')
param gatewaySubnetId string

@description('Deploy ExpressRoute Gateway')
param deployExpressRouteGateway bool

@description('ExpressRoute Gateway SKU')
@allowed(['ErGw1AZ', 'ErGw2AZ', 'ErGw3AZ'])
param expressRouteGatewaySku string

@description('Deploy VPN Gateway')
param deployVpnGateway bool

@description('VPN Gateway SKU')
@allowed(['VpnGw1AZ', 'VpnGw2AZ', 'VpnGw3AZ'])
param vpnGatewaySku string

@description('Log Analytics Workspace ID for diagnostics')
param logAnalyticsWorkspaceId string

@description('Resource tags')
param tags object

// ─── ExpressRoute Gateway ─────────────────────────────────────────────────────

resource erGwPip 'Microsoft.Network/publicIPAddresses@2024-01-01' = if (deployExpressRouteGateway) {
  name: '${prefix}-ergw-pip'
  location: location
  tags: tags
  sku: { name: 'Standard', tier: 'Regional' }
  properties: { publicIPAllocationMethod: 'Static' }
  zones: ['1', '2', '3']
}

resource expressRouteGateway 'Microsoft.Network/virtualNetworkGateways@2024-01-01' = if (deployExpressRouteGateway) {
  name: '${prefix}-ergw'
  location: location
  tags: tags
  properties: {
    gatewayType: 'ExpressRoute'
    sku: {
      name: expressRouteGatewaySku
      tier: expressRouteGatewaySku
    }
    ipConfigurations: [
      {
        name: 'ergw-ipconfig'
        properties: {
          subnet: { id: gatewaySubnetId }
          publicIPAddress: { id: erGwPip.id }
        }
      }
    ]
  }
}

resource erGwDiag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (deployExpressRouteGateway) {
  name: '${prefix}-ergw-diag'
  scope: expressRouteGateway
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

// ─── VPN Gateway ──────────────────────────────────────────────────────────────

resource vpnGwPip 'Microsoft.Network/publicIPAddresses@2024-01-01' = if (deployVpnGateway) {
  name: '${prefix}-vpngw-pip'
  location: location
  tags: tags
  sku: { name: 'Standard', tier: 'Regional' }
  properties: { publicIPAllocationMethod: 'Static' }
  zones: ['1', '2', '3']
}

resource vpnGateway 'Microsoft.Network/virtualNetworkGateways@2024-01-01' = if (deployVpnGateway) {
  name: '${prefix}-vpngw'
  location: location
  tags: tags
  properties: {
    gatewayType: 'Vpn'
    vpnType: 'RouteBased'
    sku: {
      name: vpnGatewaySku
      tier: vpnGatewaySku
    }
    ipConfigurations: [
      {
        name: 'vpngw-ipconfig'
        properties: {
          subnet: { id: gatewaySubnetId }
          publicIPAddress: { id: vpnGwPip.id }
        }
      }
    ]
    vpnGatewayGeneration: 'Generation2'
  }
}

resource vpnGwDiag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (deployVpnGateway) {
  name: '${prefix}-vpngw-diag'
  scope: vpnGateway
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

output expressRouteGatewayId string = deployExpressRouteGateway ? expressRouteGateway.id : ''
output vpnGatewayId string = deployVpnGateway ? vpnGateway.id : ''

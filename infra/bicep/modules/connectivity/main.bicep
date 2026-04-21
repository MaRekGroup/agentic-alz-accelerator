// ─────────────────────────────────────────────────────────────────────────────
// Platform Landing Zone: Connectivity Module
// CAF Design Area: Network Topology & Connectivity
//
// Deploys either a Hub-Spoke or Azure Virtual WAN topology.
// Select via hubTopology parameter: 'hub-spoke' | 'vwan'
// ─────────────────────────────────────────────────────────────────────────────

targetScope = 'subscription'

// ─── Parameters ───────────────────────────────────────────────────────────────

@description('Azure region for deployment')
param location string = deployment().location

@description('Naming prefix (≤10 chars)')
@maxLength(10)
param prefix string

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string

param now string = utcNow('yyyy-MM-01')

@description('Hub network topology')
@allowed(['hub-spoke', 'vwan'])
param hubTopology string = 'hub-spoke'

@description('Hub VNet address space (hub-spoke only)')
param hubVnetAddressSpace string = '10.0.0.0/16'

@description('Deploy Azure Firewall')
param deployAzureFirewall bool = true

@description('Azure Firewall SKU tier')
@allowed(['Standard', 'Premium'])
param firewallSkuTier string = 'Premium'

@description('Deploy ExpressRoute Gateway')
param deployExpressRouteGateway bool = false

@description('ExpressRoute Gateway SKU')
@allowed(['ErGw1AZ', 'ErGw2AZ', 'ErGw3AZ'])
param expressRouteGatewaySku string = 'ErGw1AZ'

@description('Deploy VPN Gateway')
param deployVpnGateway bool = false

@description('VPN Gateway SKU')
@allowed(['VpnGw1AZ', 'VpnGw2AZ', 'VpnGw3AZ'])
param vpnGatewaySku string = 'VpnGw1AZ'

@description('Enable DDoS Protection Plan')
param enableDdosProtection bool = true

@description('Deploy DNS Resolver')
param deployDnsResolver bool = true

@description('Enable Azure Bastion')
param enableBastion bool = true

@description('Bastion SKU')
@allowed(['Basic', 'Standard'])
param bastionSku string = 'Standard'

@description('Private DNS zones to deploy (array of zone names)')
param privateDnsZones array = [
  'privatelink.database.windows.net'
  'privatelink.blob.core.windows.net'
  'privatelink.file.core.windows.net'
  'privatelink.vaultcore.azure.net'
  'privatelink.azurewebsites.net'
  'privatelink.azurecr.io'
  'privatelink.openai.azure.com'
  'privatelink.servicebus.windows.net'
  'privatelink.cognitiveservices.azure.com'
]

@description('Log Analytics workspace resource ID (from management subscription)')
param logAnalyticsWorkspaceId string

@description('Monthly budget in USD')
param budgetAmountUsd int

@description('Budget alert email addresses')
param budgetAlertEmails array = []

@description('Value for the ManagedBy tag')
param managedBy string = 'agentic-alz-accelerator'

@description('Resource tags')
param tags object = {
  Environment: environment
  Owner: 'platform-team'
  CostCenter: 'platform'
  Project: 'platform-connectivity'
  ManagedBy: managedBy
}

// ─── Variables ────────────────────────────────────────────────────────────────

var regionShortcode = {
  eastus: 'eus'
  eastus2: 'eus2'
  westus: 'wus'
  westus2: 'wus2'
  westus3: 'wus3'
  centralus: 'cus'
  southcentralus: 'scus'
  northeurope: 'neu'
  westeurope: 'weu'
  uksouth: 'uks'
  southeastasia: 'sea'
  australiaeast: 'aue'
  japaneast: 'jpe'
}[location] ?? location

var rgHub      = '${prefix}-conn-hub-${regionShortcode}-rg'
var rgGateways = '${prefix}-conn-gateways-${regionShortcode}-rg'
var rgDns      = '${prefix}-conn-dns-${regionShortcode}-rg'
var rgDdos     = '${prefix}-conn-ddos-rg'

// ─── Resource Groups ──────────────────────────────────────────────────────────

resource rgHubRes 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgHub
  location: location
  tags: tags
}

resource rgGatewaysRes 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgGateways
  location: location
  tags: tags
}

resource rgDnsRes 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgDns
  location: location
  tags: tags
}

resource rgDdosRes 'Microsoft.Resources/resourceGroups@2024-03-01' = if (enableDdosProtection) {
  name: rgDdos
  location: location
  tags: tags
}

// ─── Cost Governance ─────────────────────────────────────────────────────────

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-connectivity-${environment}'
  properties: {
    timePeriod: {
      startDate: now
    }
    timeGrain: 'Monthly'
    amount: budgetAmountUsd
    category: 'Cost'
    notifications: {
      forecast80: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 80
        thresholdType: 'Forecasted'
        contactEmails: budgetAlertEmails
      }
      forecast100: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Forecasted'
        contactEmails: budgetAlertEmails
      }
      forecast120: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 120
        thresholdType: 'Forecasted'
        contactEmails: budgetAlertEmails
      }
    }
  }
}

// ─── Hub-Spoke Topology ───────────────────────────────────────────────────────

module hubSpoke 'hub-spoke/main.bicep' = if (hubTopology == 'hub-spoke') {
  name: 'hub-spoke-deployment'
  scope: rgHubRes
  params: {
    location: location
    prefix: prefix
    hubVnetAddressSpace: hubVnetAddressSpace
    deployAzureFirewall: deployAzureFirewall
    firewallSkuTier: firewallSkuTier
    enableBastion: enableBastion
    bastionSku: bastionSku
    ddosProtectionPlanId: enableDdosProtection ? ddosProtectionPlan.outputs.resourceId : ''
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
    tags: tags
  }
}

module gatewaysHubSpoke 'gateways/main.bicep' = if (hubTopology == 'hub-spoke') {
  name: 'gateways-deployment'
  scope: rgGatewaysRes
  params: {
    location: location
    prefix: prefix
    gatewaySubnetId: hubTopology == 'hub-spoke' ? hubSpoke.outputs.gatewaySubnetId : ''
    deployExpressRouteGateway: deployExpressRouteGateway
    expressRouteGatewaySku: expressRouteGatewaySku
    deployVpnGateway: deployVpnGateway
    vpnGatewaySku: vpnGatewaySku
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
    tags: tags
  }
}

// ─── Azure Virtual WAN Topology ───────────────────────────────────────────────

module vwan 'vwan/main.bicep' = if (hubTopology == 'vwan') {
  name: 'vwan-deployment'
  scope: rgHubRes
  params: {
    location: location
    prefix: prefix
    vwanType: 'Standard'
    deployAzureFirewall: deployAzureFirewall
    firewallSkuTier: firewallSkuTier
    logAnalyticsWorkspaceId: logAnalyticsWorkspaceId
    tags: tags
  }
}

// ─── DDoS Protection Plan ─────────────────────────────────────────────────────

module ddosProtectionPlan 'br/public:avm/res/network/ddos-protection-plan:0.1.0' = if (enableDdosProtection) {
  name: 'ddos-protection-plan'
  scope: rgDdosRes
  params: {
    name: '${prefix}-ddos-plan'
    location: location
    tags: tags
  }
}

// ─── Private DNS Zones ────────────────────────────────────────────────────────

module privateDns 'private-dns/main.bicep' = {
  name: 'private-dns-deployment'
  scope: rgDnsRes
  params: {
    prefix: prefix
    privateDnsZones: privateDnsZones
    hubVnetId: hubTopology == 'hub-spoke' ? hubSpoke.outputs.hubVnetId : ''
    tags: tags
  }
}

// ─── DNS Resolver ─────────────────────────────────────────────────────────────

module dnsResolver 'br/public:avm/res/network/dns-resolver:0.3.0' = if (hubTopology == 'hub-spoke' && deployDnsResolver) {
  name: 'dns-resolver'
  scope: rgHubRes
  params: {
    name: '${prefix}-dns-resolver'
    location: location
    virtualNetworkResourceId: hubTopology == 'hub-spoke' ? hubSpoke.outputs.hubVnetId : ''
    inboundEndpoints: [
      {
        name: 'inbound'
        subnetResourceId: hubTopology == 'hub-spoke' ? hubSpoke.outputs.dnsInboundSubnetId : ''
      }
    ]
    outboundEndpoints: [
      {
        name: 'outbound'
        subnetResourceId: hubTopology == 'hub-spoke' ? hubSpoke.outputs.dnsOutboundSubnetId : ''
      }
    ]
    tags: tags
  }
}

// ─── Outputs ──────────────────────────────────────────────────────────────────

output hubVnetId string = hubTopology == 'hub-spoke' ? hubSpoke.outputs.hubVnetId : vwan.outputs.vwanId
output hubTopologyDeployed string = hubTopology
output ddosProtectionPlanId string = enableDdosProtection ? ddosProtectionPlan.outputs.resourceId : ''
output privateDnsZoneIds array = privateDns.outputs.zoneIds
output azureFirewallPrivateIp string = (hubTopology == 'hub-spoke' && deployAzureFirewall) ? hubSpoke.outputs.firewallPrivateIp : ''
output expressRouteGatewayId string = (hubTopology == 'hub-spoke' && deployExpressRouteGateway) ? gatewaysHubSpoke.outputs.expressRouteGatewayId : ''

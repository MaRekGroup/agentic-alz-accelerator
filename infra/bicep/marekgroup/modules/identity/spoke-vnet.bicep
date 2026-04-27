// Identity Spoke VNet — deployed at resource group scope
// AVM-first: uses Azure Verified Modules from the public Bicep registry
// Called from main.bicep (subscription-scoped)

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('Spoke VNet address space')
param spokeVnetAddressSpace string

@description('Hub VNet resource ID for peering')
param hubVnetId string

@description('Log Analytics Workspace ID for diagnostics (empty = skip)')
param logAnalyticsWorkspaceId string = ''

@description('Resource tags')
param tags object

@description('Bastion subnet CIDR for RDP access (restrict to Bastion only)')
param bastionSubnetCidr string = '10.0.0.128/26'

// ─── Subnet Definitions ─────────────────────────────────────────────────────

var subnets = [
  {
    name: 'DomainControllers'
    addressPrefix: cidrSubnet(spokeVnetAddressSpace, 27, 0) // /27 = 32 IPs
  }
  {
    name: 'IdentityServices'
    addressPrefix: cidrSubnet(spokeVnetAddressSpace, 27, 1) // /27 = 32 IPs
  }
]

// ─── Network Security Groups ────────────────────────────────────────────────

resource nsgDomainControllers 'Microsoft.Network/networkSecurityGroups@2024-01-01' = {
  name: '${prefix}-identity-dc-nsg'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowAD-TCP'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'VirtualNetwork'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRanges: [
            '53'    // DNS
            '88'    // Kerberos
            '135'   // RPC
            '389'   // LDAP
            '445'   // SMB
            '464'   // Kerberos change/set password
            '636'   // LDAPS
            '3268'  // Global Catalog
            '3269'  // Global Catalog SSL
            '5722'  // DFS-R
            '9389'  // AD Web Services
            '49152-65535' // RPC dynamic ports
          ]
        }
      }
      {
        name: 'AllowAD-UDP'
        properties: {
          priority: 110
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Udp'
          sourceAddressPrefix: 'VirtualNetwork'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRanges: [
            '53'    // DNS
            '88'    // Kerberos
            '123'   // NTP
            '389'   // LDAP
            '464'   // Kerberos change/set password
          ]
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
      // ─── Outbound rules ───
      {
        name: 'AllowADReplication-Outbound'
        properties: {
          priority: 100
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: 'VirtualNetwork'
          destinationPortRanges: [
            '53'
            '88'
            '135'
            '389'
            '445'
            '464'
            '636'
            '3268'
            '3269'
            '49152-65535'
          ]
        }
      }
      {
        name: 'AllowDNS-Outbound'
        properties: {
          priority: 110
          direction: 'Outbound'
          access: 'Allow'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: 'VirtualNetwork'
          destinationPortRanges: [
            '53'
          ]
        }
      }
      {
        name: 'AllowAzureAD-Outbound'
        properties: {
          priority: 120
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: 'AzureActiveDirectory'
          destinationPortRanges: [
            '443'
            '80'
          ]
        }
      }
      {
        name: 'AllowAzureMonitor-Outbound'
        properties: {
          priority: 130
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: 'AzureMonitor'
          destinationPortRange: '443'
        }
      }
      {
        name: 'AllowKMS-Outbound'
        properties: {
          priority: 140
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '23.102.135.246'
          destinationPortRange: '1688'
        }
      }
      {
        name: 'DenyAllOutbound'
        properties: {
          priority: 4096
          direction: 'Outbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource nsgIdentityServices 'Microsoft.Network/networkSecurityGroups@2024-01-01' = {
  name: '${prefix}-identity-svc-nsg'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowHTTPS-VNet'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'VirtualNetwork'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      {
        name: 'AllowRDP-Bastion'
        properties: {
          priority: 110
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: bastionSubnetCidr
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '3389'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

// ─── Spoke Virtual Network (AVM) ───────────────────────────────────────────

module spokeVnet 'br/public:avm/res/network/virtual-network:0.5.2' = {
  name: '${prefix}-identity-spoke-vnet-deployment'
  params: {
    name: '${prefix}-identity-spoke-vnet'
    location: location
    tags: tags
    addressPrefixes: [spokeVnetAddressSpace]
    subnets: [
      {
        name: subnets[0].name
        addressPrefix: subnets[0].addressPrefix
        networkSecurityGroupResourceId: nsgDomainControllers.id
      }
      {
        name: subnets[1].name
        addressPrefix: subnets[1].addressPrefix
        networkSecurityGroupResourceId: nsgIdentityServices.id
      }
    ]
    peerings: [
      {
        allowForwardedTraffic: true
        allowGatewayTransit: false
        allowVirtualNetworkAccess: true
        remotePeeringAllowForwardedTraffic: true
        remotePeeringAllowVirtualNetworkAccess: true
        remotePeeringEnabled: true
        remotePeeringName: '${prefix}-hub-to-identity-spoke'
        remoteVirtualNetworkResourceId: hubVnetId
        useRemoteGateways: false
      }
    ]
    diagnosticSettings: logAnalyticsWorkspaceId != '' ? [
      {
        workspaceResourceId: logAnalyticsWorkspaceId
        logCategoriesAndGroups: [
          { categoryGroup: 'allLogs' }
        ]
        metricCategories: [
          { category: 'AllMetrics' }
        ]
      }
    ] : []
  }
}

// ─── Outputs ────────────────────────────────────────────────────────────────

output spokeVnetId string = spokeVnet.outputs.resourceId
output spokeVnetName string = spokeVnet.outputs.name
output domainControllersSubnetId string = spokeVnet.outputs.subnetResourceIds[0]
output identityServicesSubnetId string = spokeVnet.outputs.subnetResourceIds[1]

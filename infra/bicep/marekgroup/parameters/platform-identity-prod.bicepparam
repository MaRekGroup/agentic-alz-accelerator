using '../modules/identity/main.bicep'

param location = 'southcentralus'
param prefix = 'mrg'
param environment = 'prod'
param budgetAmount = 200
param technicalContact = 'ytesfaye@MngEnvMCAP084543.onmicrosoft.com'

// Spoke VNet — peered to hub in connectivity subscription
param deploySpokeVnet = true
param spokeVnetAddressSpace = '10.1.0.0/24'
// hubVnetId is injected at deploy time via --parameters override:
//   --parameters hubVnetId='/subscriptions/{conn-sub-id}/resourceGroups/mrg-conn-hub-scus-rg/providers/Microsoft.Network/virtualNetworks/mrg-hub-vnet'

param tags = {
  Environment: 'prod'
  Owner: 'platform-team'
  CostCenter: 'platform'
  Project: 'platform-identity'
  ManagedBy: 'agentic-alz-accelerator'
}

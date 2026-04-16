using '../modules/connectivity/main.bicep'

param location = 'southcentralus'
param prefix = 'mrg'
param environment = 'prod'
param hubTopology = 'hub-spoke'
param hubVnetAddressSpace = '10.0.0.0/16'
param deployAzureFirewall = true
param firewallSkuTier = 'Premium'
param deployExpressRouteGateway = false
param deployVpnGateway = false
param enableDdosProtection = true
param enableBastion = true
param bastionSku = 'Standard'
param logAnalyticsWorkspaceId = ''
param budgetAmountUsd = 2000
param budgetAlertEmails = [
  'ytesfaye@MngEnvMCAP084543.onmicrosoft.com'
]
param tags = {
  environment: 'prod'
  managedBy: 'agentic-alz-accelerator'
  platform: 'connectivity'
}

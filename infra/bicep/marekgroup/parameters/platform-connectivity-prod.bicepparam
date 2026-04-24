using '../modules/connectivity/main.bicep'

param location = 'southcentralus'
param prefix = 'mrg'
param environment = 'prod'
param hubTopology = 'hub-spoke'
param hubVnetAddressSpace = '10.0.0.0/16'
param deployAzureFirewall = false
param firewallSkuTier = 'Premium'
param deployExpressRouteGateway = false
param deployVpnGateway = false
param enableDdosProtection = false
param deployDnsResolver = false
param enableBastion = true
param bastionSku = 'Standard'
param logAnalyticsWorkspaceId = ''
param budgetAmountUsd = 2000
param budgetAlertEmails = [
  'ytesfaye@MngEnvMCAP084543.onmicrosoft.com'
]
param tags = {
  Environment: 'prod'
  Owner: 'platform-team'
  CostCenter: 'platform'
  Project: 'platform-connectivity'
  ManagedBy: 'agentic-alz-accelerator'
}

using '../modules/platform-security/main.bicep'

param location = 'southcentralus'
param prefix = 'mrg'
param environment = 'prod'
param sentinelWorkspaceMode = 'dedicated'
param managementLogAnalyticsWorkspaceId = ''
param retentionDays = 90
param enableSentinel = true
param enableSoar = true
param enableThreatIntelligence = false
param securityContactEmail = 'ytesfaye@MngEnvMCAP084543.onmicrosoft.com'
param budgetAmountUsd = 1000
param budgetAlertEmails = [
  'ytesfaye@MngEnvMCAP084543.onmicrosoft.com'
]
param tags = {
  Environment: 'prod'
  Owner: 'platform-team'
  CostCenter: 'security'
  Project: 'platform-security'
  ManagedBy: 'agentic-alz-accelerator'
}

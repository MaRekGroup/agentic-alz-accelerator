using '../modules/management/main.bicep'

param location = 'southcentralus'
param prefix = 'mrg'
param retentionDays = 90
param enableSentinel = false
param environment = 'prod'
param budgetAmount = 500
param technicalContact = 'ytesfaye@MngEnvMCAP084543.onmicrosoft.com'
param tags = {
  Environment: 'prod'
  Owner: 'platform-team'
  CostCenter: 'platform'
  Project: 'platform-management'
  ManagedBy: 'agentic-alz-accelerator'
}

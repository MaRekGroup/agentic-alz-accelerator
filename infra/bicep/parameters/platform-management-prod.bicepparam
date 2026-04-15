using '../modules/management/main.bicep'

param location = 'southcentralus'
param prefix = 'mrg'
param retentionDays = 90
param enableSentinel = false
param environment = 'prod'
param budgetAmount = 500
param technicalContact = 'ytesfaye@MngEnvMCAP084543.onmicrosoft.com'
param tags = {
  environment: 'prod'
  managedBy: 'agentic-alz-accelerator'
  platform: 'management'
}

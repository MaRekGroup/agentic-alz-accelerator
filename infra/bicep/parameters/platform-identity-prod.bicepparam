using '../modules/identity/main.bicep'

param location = 'southcentralus'
param prefix = 'mrg'
param environment = 'prod'
param budgetAmount = 200
param technicalContact = 'ytesfaye@MngEnvMCAP084543.onmicrosoft.com'
param tags = {
  Environment: 'prod'
  Owner: 'platform-team'
  CostCenter: 'platform'
  Project: 'platform-identity'
  ManagedBy: 'agentic-alz-accelerator'
}

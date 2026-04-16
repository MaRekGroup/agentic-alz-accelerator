using '../modules/identity/main.bicep'

param location = 'southcentralus'
param prefix = 'mrg'
param environment = 'prod'
param budgetAmount = 200
param technicalContact = 'ytesfaye@MngEnvMCAP084543.onmicrosoft.com'
param tags = {
  environment: 'prod'
  managedBy: 'agentic-alz-accelerator'
  platform: 'identity'
}

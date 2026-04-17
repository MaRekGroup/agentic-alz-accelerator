// CAF Design Area: Management
// Log Analytics, Azure Monitor, Backup, Update Management
// Subscription-scoped: creates its own RG using the prefix convention

targetScope = 'subscription'

@description('Azure region')
param location string

@description('Resource name prefix')
param prefix string

@description('Log retention in days')
param retentionDays int

@description('Enable Azure Sentinel')
param enableSentinel bool = false

@description('Tags')
param tags object

@description('Monthly budget amount in USD')
param budgetAmount int

@description('Technical contact email for budget alerts')
param technicalContact string

@description('Environment name')
param environment string

@description('Current UTC timestamp — used to derive budget start date')
param now string = utcNow('yyyy-MM-01')

// ─── Variables ──────────────────────────────────────────────────────────────

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

var rgName = '${prefix}-management-${regionShortcode}-rg'

// ─── Resource Group ─────────────────────────────────────────────────────────

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgName
  location: location
  tags: tags
}

// ─── Management Resources (RG-scoped module) ───────────────────────────────

module managementResources 'resources.bicep' = {
  name: 'management-resources-deployment'
  scope: rg
  params: {
    location: location
    prefix: prefix
    retentionDays: retentionDays
    tags: tags
  }
}

// ─── Cost Governance (subscription-scoped) ──────────────────────────────────

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-management-${environment}'
  properties: {
    timePeriod: {
      startDate: now
    }
    timeGrain: 'Monthly'
    amount: budgetAmount
    category: 'Cost'
    notifications: {
      forecast80: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 80
        thresholdType: 'Forecasted'
        contactEmails: [technicalContact]
      }
      forecast100: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Forecasted'
        contactEmails: [technicalContact]
      }
      forecast120: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 120
        thresholdType: 'Forecasted'
        contactEmails: [technicalContact]
      }
    }
  }
}

// ─── Outputs ────────────────────────────────────────────────────────────────

output resourceGroupName string = rg.name
output workspaceId string = managementResources.outputs.workspaceId
output workspaceName string = managementResources.outputs.workspaceName
output workspaceCustomerId string = managementResources.outputs.workspaceCustomerId
output automationAccountId string = managementResources.outputs.automationAccountId
output actionGroupId string = managementResources.outputs.actionGroupId

// ─────────────────────────────────────────────────────────────────────────────
// Platform Landing Zone: Security Module
// CAF Design Area: Security
//
// Deploys the dedicated Security subscription resources:
//  - Security-dedicated Log Analytics workspace + Microsoft Sentinel
//  - Microsoft Defender for Cloud configuration (all plans)
//  - SOAR playbooks (Logic Apps) for automated incident response
//  - Security Key Vault (private endpoint, purge protection)
//  - Security Automation Account (baseline checks, posture reports)
//  - Cost governance (mandatory budget)
// ─────────────────────────────────────────────────────────────────────────────

targetScope = 'subscription'

// ─── Parameters ─────────────────────────────────────────────────────────────

@description('Azure region for deployment')
param location string = deployment().location

@description('Naming prefix (≤10 chars)')
@maxLength(10)
param prefix string

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string

param now string = utcNow('yyyy-MM-01')

@description('Sentinel workspace mode: dedicated (new workspace) or linked (reuse management workspace)')
@allowed(['dedicated', 'linked'])
param sentinelWorkspaceMode string = 'dedicated'

@description('Log Analytics workspace ID from management subscription (required when sentinelWorkspaceMode=linked)')
param managementLogAnalyticsWorkspaceId string = ''

@description('Log retention in days for the security workspace')
param retentionDays int = 730

@description('Enable Microsoft Sentinel')
param enableSentinel bool = true

@description('Enable SOAR playbooks (Logic Apps)')
param enableSoar bool = true

@description('Enable Threat Intelligence integration')
param enableThreatIntelligence bool = true

@description('Defender for Cloud plans to enable')
param defenderPlans array = [
  'VirtualMachines'
  'SqlServers'
  'AppServices'
  'StorageAccounts'
  'KeyVaults'
  'Dns'
  'Arm'
  'Containers'
  'OpenSourceRelationalDatabases'
  'SqlServerVirtualMachines'
  'CosmosDbs'
  'Api'
]

@description('Security contact email for Defender for Cloud alerts')
param securityContactEmail string

@description('Monthly budget in USD')
param budgetAmountUsd int

@description('Budget alert email addresses')
param budgetAlertEmails array = []

@description('Resource tags')
param tags object = {
  environment: environment
  managed_by: 'agentic-alz-accelerator'
  cost_center: 'security'
}

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

var rgSoc          = '${prefix}-sec-soc-${regionShortcode}-rg'
var rgPosture      = '${prefix}-sec-posture-${regionShortcode}-rg'
var rgAutomation   = '${prefix}-sec-automation-${regionShortcode}-rg'
var rgGovernance   = '${prefix}-sec-governance-${regionShortcode}-rg'

var workspaceName  = '${prefix}-sec-sentinel-law'
var kvName         = '${prefix}-sec-kv'
var autoName       = '${prefix}-sec-automation'

// ─── Resource Groups ────────────────────────────────────────────────────────

resource rgSocRes 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgSoc
  location: location
  tags: tags
}

resource rgPostureRes 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgPosture
  location: location
  tags: tags
}

resource rgAutomationRes 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgAutomation
  location: location
  tags: tags
}

resource rgGovernanceRes 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgGovernance
  location: location
  tags: tags
}

// ─── Cost Governance (mandatory) ────────────────────────────────────────────

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-platform-security-${environment}'
  properties: {
    timePeriod: {
      startDate: now
    }
    timeGrain: 'Monthly'
    amount: budgetAmountUsd
    category: 'Cost'
    notifications: {
      forecast80: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 80
        thresholdType: 'Forecasted'
        contactEmails: budgetAlertEmails
      }
      forecast100: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Forecasted'
        contactEmails: budgetAlertEmails
      }
      forecast120: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 120
        thresholdType: 'Forecasted'
        contactEmails: budgetAlertEmails
      }
    }
  }
}

// ─── Security-Dedicated Log Analytics Workspace ────────────────────────────

module securityWorkspace 'security-workspace/main.bicep' = if (sentinelWorkspaceMode == 'dedicated') {
  name: 'security-workspace-deployment'
  scope: rgSocRes
  params: {
    location: location
    workspaceName: workspaceName
    retentionDays: retentionDays
    tags: tags
  }
}

// ─── Microsoft Sentinel ────────────────────────────────────────────────────

module sentinel 'sentinel/main.bicep' = if (enableSentinel) {
  name: 'sentinel-deployment'
  scope: rgSocRes
  dependsOn: [securityWorkspace]
  params: {
    workspaceId: sentinelWorkspaceMode == 'dedicated'
      ? securityWorkspace.outputs.workspaceId
      : managementLogAnalyticsWorkspaceId
    enableThreatIntelligence: enableThreatIntelligence
    tags: tags
  }
}

// ─── Microsoft Defender for Cloud ──────────────────────────────────────────

module defenderConfig 'defender/main.bicep' = {
  name: 'defender-deployment'
  params: {
    defenderPlans: defenderPlans
    securityContactEmail: securityContactEmail
    logAnalyticsWorkspaceId: sentinelWorkspaceMode == 'dedicated'
      ? securityWorkspace.outputs.workspaceId
      : managementLogAnalyticsWorkspaceId
  }
}

// ─── SOAR Playbooks (Logic Apps) ───────────────────────────────────────────

module soarPlaybooks 'soar/main.bicep' = if (enableSoar) {
  name: 'soar-deployment'
  scope: rgAutomationRes
  params: {
    location: location
    prefix: prefix
    sentinelWorkspaceId: sentinelWorkspaceMode == 'dedicated'
      ? securityWorkspace.outputs.workspaceId
      : managementLogAnalyticsWorkspaceId
    tags: tags
  }
}

// ─── Key Vault (security secrets, private endpoint enforced) ────────────────

module keyVault 'br/public:avm/res/key-vault/vault:0.6.0' = {
  name: 'security-key-vault'
  scope: rgAutomationRes
  params: {
    name: kvName
    location: location
    enablePurgeProtection: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enableRbacAuthorization: true
    publicNetworkAccess: 'Disabled'   // Security baseline: no public access
    tags: tags
  }
}

// ─── Security Automation Account ───────────────────────────────────────────

module automationAccount 'br/public:avm/res/automation/automation-account:0.9.0' = {
  name: 'security-automation'
  scope: rgAutomationRes
  params: {
    name: autoName
    location: location
    skuName: 'Basic'
    managedIdentities: {
      systemAssigned: true   // Security baseline: Managed Identity
    }
    diagnosticSettings: [
      {
        workspaceResourceId: sentinelWorkspaceMode == 'dedicated'
          ? securityWorkspace.outputs.workspaceId
          : managementLogAnalyticsWorkspaceId
      }
    ]
    tags: tags
  }
}

// ─── Outputs ───────────────────────────────────────────────────────────────

output securityWorkspaceId string = sentinelWorkspaceMode == 'dedicated'
  ? securityWorkspace.outputs.workspaceId
  : managementLogAnalyticsWorkspaceId
output sentinelWorkspaceMode string = sentinelWorkspaceMode
output keyVaultName string = kvName
output automationAccountName string = autoName
output resourceGroupSoc string = rgSoc
output resourceGroupPosture string = rgPosture
output resourceGroupAutomation string = rgAutomation
output resourceGroupGovernance string = rgGovernance

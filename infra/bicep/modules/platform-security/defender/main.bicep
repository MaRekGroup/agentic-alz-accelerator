// Defender for Cloud Sub-module
// Configures Microsoft Defender for Cloud plans and security contacts

targetScope = 'subscription'

@description('Defender plan names to enable')
param defenderPlans array

@description('Security contact email')
param securityContactEmail string

@description('Log Analytics workspace ID for Defender data')
param logAnalyticsWorkspaceId string

// ─── Defender for Cloud Pricing Tiers ─────────────────────────────────────────

@batchSize(1)
resource defenderPricing 'Microsoft.Security/pricings@2024-01-01' = [
  for plan in defenderPlans: {
    name: plan
    properties: {
      pricingTier: 'Standard'
    }
  }
]

// ─── Security Contact ─────────────────────────────────────────────────────────

resource securityContact 'Microsoft.Security/securityContacts@2020-01-01-preview' = {
  name: 'default'
  properties: {
    emails: securityContactEmail
    alertNotifications: {
      state: 'On'
      minimalSeverity: 'Medium'
    }
    notificationsByRole: {
      state: 'On'
      roles: ['Owner', 'ServiceAdmin']
    }
resource workspaceSettings 'Microsoft.Security/workspaceSettings@2017-08-01-preview' = {
  name: 'default'
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    scope: subscription().id
  }
}

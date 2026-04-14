// Defender for Cloud Sub-module
// Configures Microsoft Defender for Cloud plans and security contacts

@description('Defender plan names to enable')
param defenderPlans array

@description('Security contact email')
param securityContactEmail string

@description('Log Analytics workspace ID for Defender data')
param logAnalyticsWorkspaceId string

@description('Resource tags')
param tags object

// ─── Defender for Cloud Pricing Tiers ─────────────────────────────────────────

resource defenderPricing 'Microsoft.Security/pricings@2024-01-01' = [
  for plan in defenderPlans: {
    name: plan
    properties: {
      pricingTier: 'Standard'
    }
  }
]

// ─── Security Contact ─────────────────────────────────────────────────────────

resource securityContact 'Microsoft.Security/securityContacts@2023-12-01-preview' = {
  name: 'default'
  properties: {
    emails: securityContactEmail
    notificationsByRole: {
      state: 'On'
      roles: ['Owner', 'ServiceAdmin']
    }
    isEnabled: true
  }
}

// ─── Auto Provisioning ────────────────────────────────────────────────────────

resource autoProvisioning 'Microsoft.Security/autoProvisioningSettings@2017-08-01-preview' = {
  name: 'default'
  properties: {
    autoProvision: 'On'
  }
}

// ─── Workspace Settings ───────────────────────────────────────────────────────

resource workspaceSettings 'Microsoft.Security/workspaceSettings@2017-08-01-preview' = {
  name: 'default'
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    scope: subscription().id
  }
}

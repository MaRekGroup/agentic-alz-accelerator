# ─────────────────────────────────────────────────────────────────────────────
# Platform Landing Zone: Security Module (Terraform)
# CAF Design Area: Security
#
# Deploys the dedicated Security subscription resources:
#  - Security-dedicated Log Analytics workspace + Microsoft Sentinel
#  - Microsoft Defender for Cloud (all plans)
#  - SOAR playbooks (Logic Apps)
#  - Security Key Vault (private endpoint, purge protection)
#  - Security Automation Account
#  - Mandatory budget
# ─────────────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.9.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" }
  }
}

# ─── Variables ──────────────────────────────────────────────────────────────

variable "subscription_id"              { type = string }
variable "location"                     { type = string, default = "southcentralus" }
variable "prefix"                       { type = string }
variable "environment"                  { type = string }
variable "sentinel_workspace_mode"      { type = string, default = "dedicated", description = "dedicated or linked" }
variable "management_law_id"            { type = string, default = "", description = "Management LAW ID (required if sentinel_workspace_mode=linked)" }
variable "retention_days"               { type = number, default = 730 }
variable "enable_sentinel"              { type = bool, default = true }
variable "enable_soar"                  { type = bool, default = true }
variable "enable_threat_intelligence"   { type = bool, default = true }
variable "security_contact_email"       { type = string }
variable "budget_amount_usd"            { type = number }
variable "budget_alert_emails"          { type = list(string), default = [] }
variable "tags"                         { type = map(string), default = {} }
variable "managed_by"                    { type = string, default = "agentic-alz-accelerator" }

variable "defender_plans" {
  type    = list(string)
  default = [
    "VirtualMachines", "SqlServers", "AppServices", "Storage",
    "KeyVaults", "Dns", "Arm", "Containers",
    "OpenSourceRelationalDatabases", "SqlServerVirtualMachines",
    "CosmosDbs", "Api"
  ]
}

# ─── Locals ─────────────────────────────────────────────────────────────────

locals {
  region_shortcodes = {
    eastus2    = "eus2"
    westus2    = "wus2"
    westeurope = "weu"
    uksouth    = "uks"
    centralus  = "cus"
    southcentralus = "scus"
  }
  region_code = lookup(local.region_shortcodes, var.location, var.location)

  rg_soc        = "${var.prefix}-sec-soc-${local.region_code}-rg"
  rg_posture    = "${var.prefix}-sec-posture-${local.region_code}-rg"
  rg_automation = "${var.prefix}-sec-automation-${local.region_code}-rg"
  rg_governance = "${var.prefix}-sec-governance-${local.region_code}-rg"

  common_tags = merge({
    Environment = var.environment
    Owner       = "platform-team"
    CostCenter  = "security"
    Project     = "platform-security"
    ManagedBy   = var.managed_by
  }, var.tags)
}

# ─── Resource Groups ───────────────────────────────────────────────────────

resource "azurerm_resource_group" "soc" {
  name = local.rg_soc; location = var.location; tags = local.common_tags
}
resource "azurerm_resource_group" "posture" {
  name = local.rg_posture; location = var.location; tags = local.common_tags
}
resource "azurerm_resource_group" "automation" {
  name = local.rg_automation; location = var.location; tags = local.common_tags
}
resource "azurerm_resource_group" "governance" {
  name = local.rg_governance; location = var.location; tags = local.common_tags
}

# ─── Budget (mandatory — "no budget, no merge") ───────────────────────────

resource "azurerm_consumption_budget_subscription" "security" {
  name            = "${var.prefix}-sec-monthly-budget"
  subscription_id = "/subscriptions/${var.subscription_id}"
  amount          = var.budget_amount_usd
  time_grain      = "Monthly"
  time_period { start_date = formatdate("YYYY-MM-01'T'00:00:00Z", timestamp()) }
  dynamic "notification" {
    for_each = [80, 100, 120]
    content {
      enabled        = true
      threshold      = notification.value
      threshold_type = "Forecasted"
      operator       = "GreaterThan"
      contact_emails = var.budget_alert_emails
    }
  }
}

# ─── Security-Dedicated Log Analytics Workspace ───────────────────────────

resource "azurerm_log_analytics_workspace" "security" {
  count               = var.sentinel_workspace_mode == "dedicated" ? 1 : 0
  name                = "${var.prefix}-sec-sentinel-law"
  location            = var.location
  resource_group_name = azurerm_resource_group.soc.name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_days
  tags                = local.common_tags
}

locals {
  sentinel_workspace_id = (
    var.sentinel_workspace_mode == "dedicated"
    ? azurerm_log_analytics_workspace.security[0].id
    : var.management_law_id
  )
}

# ─── Log Analytics Solutions ───────────────────────────────────────────────

resource "azurerm_log_analytics_solution" "security_insights" {
  count                 = var.enable_sentinel && var.sentinel_workspace_mode == "dedicated" ? 1 : 0
  solution_name         = "SecurityInsights"
  location              = var.location
  resource_group_name   = azurerm_resource_group.soc.name
  workspace_resource_id = azurerm_log_analytics_workspace.security[0].id
  workspace_name        = azurerm_log_analytics_workspace.security[0].name
  plan {
    publisher = "Microsoft"
    product   = "OMSGallery/SecurityInsights"
  }
  tags = local.common_tags
}

resource "azurerm_log_analytics_solution" "security_center" {
  count                 = var.sentinel_workspace_mode == "dedicated" ? 1 : 0
  solution_name         = "Security"
  location              = var.location
  resource_group_name   = azurerm_resource_group.soc.name
  workspace_resource_id = azurerm_log_analytics_workspace.security[0].id
  workspace_name        = azurerm_log_analytics_workspace.security[0].name
  plan {
    publisher = "Microsoft"
    product   = "OMSGallery/Security"
  }
  tags = local.common_tags
}

# ─── Microsoft Sentinel Onboarding ────────────────────────────────────────

resource "azurerm_sentinel_log_analytics_workspace_onboarding" "sentinel" {
  count                      = var.enable_sentinel ? 1 : 0
  workspace_id               = local.sentinel_workspace_id
  customer_managed_key_enabled = false
}

# ─── Sentinel Data Connectors ─────────────────────────────────────────────

resource "azurerm_sentinel_data_connector_azure_active_directory" "aad" {
  count                      = var.enable_sentinel ? 1 : 0
  name                       = "AzureActiveDirectory"
  log_analytics_workspace_id = local.sentinel_workspace_id
  depends_on                 = [azurerm_sentinel_log_analytics_workspace_onboarding.sentinel]
}

resource "azurerm_sentinel_data_connector_azure_security_center" "asc" {
  count                      = var.enable_sentinel ? 1 : 0
  name                       = "AzureSecurityCenter"
  log_analytics_workspace_id = local.sentinel_workspace_id
  depends_on                 = [azurerm_sentinel_log_analytics_workspace_onboarding.sentinel]
}

resource "azurerm_sentinel_data_connector_microsoft_cloud_app_security" "mcas" {
  count                      = var.enable_sentinel ? 1 : 0
  name                       = "MicrosoftCloudAppSecurity"
  log_analytics_workspace_id = local.sentinel_workspace_id
  depends_on                 = [azurerm_sentinel_log_analytics_workspace_onboarding.sentinel]
}

resource "azurerm_sentinel_data_connector_threat_intelligence" "ti" {
  count                      = var.enable_sentinel && var.enable_threat_intelligence ? 1 : 0
  name                       = "ThreatIntelligence"
  log_analytics_workspace_id = local.sentinel_workspace_id
  depends_on                 = [azurerm_sentinel_log_analytics_workspace_onboarding.sentinel]
}

# ─── Microsoft Defender for Cloud ─────────────────────────────────────────

resource "azurerm_security_center_subscription_pricing" "plans" {
  for_each      = toset(var.defender_plans)
  tier          = "Standard"
  resource_type = each.value
}

resource "azurerm_security_center_contact" "security" {
  email               = var.security_contact_email
  alert_notifications = true
  alerts_to_admins    = true
}

resource "azurerm_security_center_auto_provisioning" "auto" {
  auto_provision = "On"
}

# ─── Security Key Vault ──────────────────────────────────────────────────

resource "azurerm_key_vault" "security" {
  name                       = "${var.prefix}-sec-kv"
  location                   = var.location
  resource_group_name        = azurerm_resource_group.automation.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = true
  soft_delete_retention_days = 90
  enable_rbac_authorization  = true
  public_network_access_enabled = false  # Security baseline: no public access
  tags                       = local.common_tags
}

data "azurerm_client_config" "current" {}

# ─── Security Automation Account ─────────────────────────────────────────

resource "azurerm_automation_account" "security" {
  name                = "${var.prefix}-sec-automation"
  location            = var.location
  resource_group_name = azurerm_resource_group.automation.name
  sku_name            = "Basic"
  identity { type = "SystemAssigned" }  # Security baseline: Managed Identity
  tags                = local.common_tags
}

resource "azurerm_log_analytics_linked_service" "security_automation" {
  count               = var.sentinel_workspace_mode == "dedicated" ? 1 : 0
  resource_group_name = azurerm_resource_group.soc.name
  workspace_id        = azurerm_log_analytics_workspace.security[0].id
  read_access_id      = azurerm_automation_account.security.id
}

# ─── SOAR Playbooks (Logic Apps) ─────────────────────────────────────────

resource "azurerm_user_assigned_identity" "soar" {
  count               = var.enable_soar ? 1 : 0
  name                = "${var.prefix}-sec-soar-mi"
  location            = var.location
  resource_group_name = azurerm_resource_group.automation.name
  tags                = local.common_tags
}

resource "azurerm_logic_app_workflow" "block_suspicious_ip" {
  count               = var.enable_soar ? 1 : 0
  name                = "${var.prefix}-soar-block-ip"
  location            = var.location
  resource_group_name = azurerm_resource_group.automation.name
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.soar[0].id]
  }
  tags = merge(local.common_tags, { soar_playbook = "Block-SuspiciousIP" })
}

resource "azurerm_logic_app_workflow" "isolate_compromised_vm" {
  count               = var.enable_soar ? 1 : 0
  name                = "${var.prefix}-soar-isolate-vm"
  location            = var.location
  resource_group_name = azurerm_resource_group.automation.name
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.soar[0].id]
  }
  tags = merge(local.common_tags, { soar_playbook = "Isolate-CompromisedVM" })
}

resource "azurerm_logic_app_workflow" "revoke_session" {
  count               = var.enable_soar ? 1 : 0
  name                = "${var.prefix}-soar-revoke-session"
  location            = var.location
  resource_group_name = azurerm_resource_group.automation.name
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.soar[0].id]
  }
  tags = merge(local.common_tags, { soar_playbook = "Revoke-EntraIDSession" })
}

resource "azurerm_logic_app_workflow" "enrich_threat_intel" {
  count               = var.enable_soar ? 1 : 0
  name                = "${var.prefix}-soar-enrich-ti"
  location            = var.location
  resource_group_name = azurerm_resource_group.automation.name
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.soar[0].id]
  }
  tags = merge(local.common_tags, { soar_playbook = "Enrich-IncidentWithThreatIntel" })
}

# ─── Diagnostic Settings (security workspace) ────────────────────────────

resource "azurerm_monitor_diagnostic_setting" "key_vault" {
  name                       = "diag-sec-kv"
  target_resource_id         = azurerm_key_vault.security.id
  log_analytics_workspace_id = local.sentinel_workspace_id
  enabled_log { category = "AuditEvent" }
  enabled_log { category = "AzurePolicyEvaluationDetails" }
  metric { category = "AllMetrics" }
}

resource "azurerm_monitor_diagnostic_setting" "automation" {
  name                       = "diag-sec-automation"
  target_resource_id         = azurerm_automation_account.security.id
  log_analytics_workspace_id = local.sentinel_workspace_id
  enabled_log { category = "JobLogs" }
  enabled_log { category = "JobStreams" }
  enabled_log { category = "DscNodeStatus" }
  metric { category = "AllMetrics" }
}

# ─── Outputs ─────────────────────────────────────────────────────────────

output "security_workspace_id" {
  value = local.sentinel_workspace_id
}
output "security_workspace_name" {
  value = var.sentinel_workspace_mode == "dedicated" ? azurerm_log_analytics_workspace.security[0].name : ""
}
output "key_vault_id" {
  value = azurerm_key_vault.security.id
}
output "automation_account_id" {
  value = azurerm_automation_account.security.id
}
output "soar_identity_id" {
  value = var.enable_soar ? azurerm_user_assigned_identity.soar[0].id : ""
}
output "soar_playbook_ids" {
  value = var.enable_soar ? {
    block_ip       = azurerm_logic_app_workflow.block_suspicious_ip[0].id
    isolate_vm     = azurerm_logic_app_workflow.isolate_compromised_vm[0].id
    revoke_session = azurerm_logic_app_workflow.revoke_session[0].id
    enrich_ti      = azurerm_logic_app_workflow.enrich_threat_intel[0].id
  } : {}
}

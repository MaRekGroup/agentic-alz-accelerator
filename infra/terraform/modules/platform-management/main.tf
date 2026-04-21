# ─────────────────────────────────────────────────────────────────────────────
# Platform Landing Zone: Management Module (Terraform)
# CAF Design Area: Management
# ─────────────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.9.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" }
  }
}

variable "subscription_id"   { type = string }
variable "location"           { type = string, default = "southcentralus" }
variable "prefix"             { type = string }
variable "environment"        { type = string }
variable "retention_days"     { type = number, default = 365 }
variable "enable_sentinel"    { type = bool, default = true }
variable "enable_automation"  { type = bool, default = true }
variable "enable_backup"      { type = bool, default = true }
variable "budget_amount_usd"  { type = number }
variable "budget_alert_emails" { type = list(string), default = [] }
variable "tags"               { type = map(string), default = {} }

locals {
  region_shortcodes = { eastus2 = "eus2", westus2 = "wus2", westeurope = "weu", uksouth = "uks", southcentralus = "scus" }
  region_code = lookup(local.region_shortcodes, var.location, var.location)
  rg_monitoring = "${var.prefix}-mgmt-monitoring-${local.region_code}-rg"
  rg_security   = "${var.prefix}-mgmt-security-${local.region_code}-rg"
  rg_governance = "${var.prefix}-mgmt-governance-${local.region_code}-rg"
  common_tags = merge({ Environment = var.environment, Owner = "platform-team", CostCenter = "platform", Project = "platform-management", ManagedBy = "agentic-alz-accelerator" }, var.tags)
}

resource "azurerm_resource_group" "monitoring" {
  name = local.rg_monitoring; location = var.location; tags = local.common_tags
}
resource "azurerm_resource_group" "security" {
  name = local.rg_security; location = var.location; tags = local.common_tags
}
resource "azurerm_resource_group" "governance" {
  name = local.rg_governance; location = var.location; tags = local.common_tags
}

# ── Budget (mandatory) ────────────────────────────────────────────────────────
resource "azurerm_consumption_budget_subscription" "management" {
  name            = "${var.prefix}-mgmt-monthly-budget"
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

# ── Log Analytics Workspace ───────────────────────────────────────────────────
resource "azurerm_log_analytics_workspace" "central" {
  name                = "${var.prefix}-law"
  location            = var.location
  resource_group_name = azurerm_resource_group.monitoring.name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_days
  tags                = local.common_tags
}

# ── Microsoft Sentinel ────────────────────────────────────────────────────────
resource "azurerm_sentinel_log_analytics_workspace_onboarding" "sentinel" {
  count                      = var.enable_sentinel ? 1 : 0
  workspace_id               = azurerm_log_analytics_workspace.central.id
  customer_managed_key_enabled = false
}

# ── Automation Account ────────────────────────────────────────────────────────
resource "azurerm_automation_account" "this" {
  count               = var.enable_automation ? 1 : 0
  name                = "${var.prefix}-automation"
  location            = var.location
  resource_group_name = azurerm_resource_group.monitoring.name
  sku_name            = "Basic"
  identity { type = "SystemAssigned" }   # Security baseline: Managed Identity
  tags                = local.common_tags
}

resource "azurerm_log_analytics_linked_service" "automation" {
  count               = var.enable_automation ? 1 : 0
  resource_group_name = azurerm_resource_group.monitoring.name
  workspace_id        = azurerm_log_analytics_workspace.central.id
  read_access_id      = azurerm_automation_account.this[0].id
}

# ── Action Group ──────────────────────────────────────────────────────────────
resource "azurerm_monitor_action_group" "platform" {
  name                = "${var.prefix}-platform-alerts"
  resource_group_name = azurerm_resource_group.monitoring.name
  short_name          = "PlatAlerts"
  tags                = local.common_tags
}

# ── Recovery Services Vault ───────────────────────────────────────────────────
resource "azurerm_recovery_services_vault" "this" {
  count               = var.enable_backup ? 1 : 0
  name                = "${var.prefix}-rsv"
  location            = var.location
  resource_group_name = azurerm_resource_group.monitoring.name
  sku                 = "Standard"
  soft_delete_enabled = true
  tags                = local.common_tags
  identity { type = "SystemAssigned" }
}

# ── Outputs ───────────────────────────────────────────────────────────────────
output "log_analytics_workspace_id"          { value = azurerm_log_analytics_workspace.central.id }
output "log_analytics_workspace_customer_id" { value = azurerm_log_analytics_workspace.central.workspace_id }
output "automation_account_id"               { value = var.enable_automation ? azurerm_automation_account.this[0].id : "" }
output "action_group_id"                     { value = azurerm_monitor_action_group.platform.id }
output "recovery_services_vault_id"          { value = var.enable_backup ? azurerm_recovery_services_vault.this[0].id : "" }

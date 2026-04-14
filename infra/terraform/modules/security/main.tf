# Security Module - Key Vault, Defender for Cloud

variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "prefix" { type = string }
variable "enable_defender" { type = bool }
variable "log_analytics_workspace_id" { type = string }
variable "tags" { type = map(string) }
variable "budget_amount_usd" { type = number }
variable "budget_alert_emails" { type = list(string), default = [] }

data "azurerm_client_config" "current" {}

# =============================================================================
# Key Vault
# =============================================================================

resource "azurerm_key_vault" "this" {
  name                       = "${var.prefix}-kv"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  enable_rbac_authorization  = true
  soft_delete_retention_days = 90
  purge_protection_enabled   = true
  tags                       = var.tags

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }
}

# =============================================================================
# Defender for Cloud
# =============================================================================

resource "azurerm_security_center_subscription_pricing" "vms" {
  count         = var.enable_defender ? 1 : 0
  tier          = "Standard"
  resource_type = "VirtualMachines"
}

resource "azurerm_security_center_subscription_pricing" "sql" {
  count         = var.enable_defender ? 1 : 0
  tier          = "Standard"
  resource_type = "SqlServers"
}

resource "azurerm_security_center_subscription_pricing" "storage" {
  count         = var.enable_defender ? 1 : 0
  tier          = "Standard"
  resource_type = "StorageAccounts"
}

resource "azurerm_security_center_subscription_pricing" "kv" {
  count         = var.enable_defender ? 1 : 0
  tier          = "Standard"
  resource_type = "KeyVaults"
}

resource "azurerm_security_center_workspace" "this" {
  count        = var.enable_defender ? 1 : 0
  scope        = "/subscriptions/${data.azurerm_client_config.current.subscription_id}"
  workspace_id = var.log_analytics_workspace_id
}

# =============================================================================
# Key Vault Diagnostics
# =============================================================================

resource "azurerm_monitor_diagnostic_setting" "kv" {
  name                       = "${var.prefix}-kv-diag"
  target_resource_id         = azurerm_key_vault.this.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category_group = "allLogs"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

# =============================================================================
# Cost Governance
# =============================================================================

resource "azurerm_consumption_budget_subscription" "budget" {
  name            = "${var.prefix}-security-monthly-budget"
  subscription_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}"
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

# =============================================================================
# Outputs
# =============================================================================

output "key_vault_id" {
  value = azurerm_key_vault.this.id
}

output "key_vault_name" {
  value = azurerm_key_vault.this.name
}

output "key_vault_uri" {
  value = azurerm_key_vault.this.vault_uri
}

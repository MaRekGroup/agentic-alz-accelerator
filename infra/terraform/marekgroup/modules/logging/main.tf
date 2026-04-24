# Logging Module - Log Analytics Workspace

variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "prefix" { type = string }
variable "retention_days" { type = number }
variable "tags" { type = map(string) }
variable "subscription_id" { type = string }
variable "budget_amount_usd" { type = number }
variable "budget_alert_emails" { type = list(string), default = [] }

resource "azurerm_log_analytics_workspace" "this" {
  name                = "${var.prefix}-law"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_days
  tags                = var.tags
}

resource "azurerm_automation_account" "this" {
  name                = "${var.prefix}-automation"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = "Basic"
  tags                = var.tags
}

resource "azurerm_log_analytics_linked_service" "automation" {
  resource_group_name = var.resource_group_name
  workspace_id        = azurerm_log_analytics_workspace.this.id
  read_access_id      = azurerm_automation_account.this.id
}

# =============================================================================
# Cost Governance
# =============================================================================

resource "azurerm_consumption_budget_subscription" "budget" {
  name            = "${var.prefix}-logging-monthly-budget"
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

output "workspace_id" {
  value = azurerm_log_analytics_workspace.this.id
}

output "workspace_name" {
  value = azurerm_log_analytics_workspace.this.name
}

output "workspace_customer_id" {
  value = azurerm_log_analytics_workspace.this.workspace_id
}

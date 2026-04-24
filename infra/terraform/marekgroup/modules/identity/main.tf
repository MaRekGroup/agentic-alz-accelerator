# Identity Module - Managed Identities and RBAC

variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "prefix" { type = string }
variable "tags" { type = map(string) }
variable "budget_amount_usd" { type = number }
variable "budget_alert_emails" { type = list(string), default = [] }

data "azurerm_subscription" "current" {}

# =============================================================================
# Managed Identities
# =============================================================================

resource "azurerm_user_assigned_identity" "workload" {
  name                = "${var.prefix}-identity"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_user_assigned_identity" "agent" {
  name                = "${var.prefix}-agent-identity"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags = merge(var.tags, {
    purpose = "mrg-agent-operations"
  })
}

# =============================================================================
# Role Assignments for Agent
# =============================================================================

resource "azurerm_role_assignment" "agent_reader" {
  scope                = data.azurerm_subscription.current.id
  role_definition_name = "Reader"
  principal_id         = azurerm_user_assigned_identity.agent.principal_id
}

resource "azurerm_role_assignment" "agent_policy_contributor" {
  scope                = data.azurerm_subscription.current.id
  role_definition_name = "Resource Policy Contributor"
  principal_id         = azurerm_user_assigned_identity.agent.principal_id
}

# =============================================================================
# Cost Governance
# =============================================================================

resource "azurerm_consumption_budget_subscription" "budget" {
  name            = "${var.prefix}-identity-monthly-budget"
  subscription_id = data.azurerm_subscription.current.id
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

output "managed_identity_id" {
  value = azurerm_user_assigned_identity.workload.id
}

output "managed_identity_principal_id" {
  value = azurerm_user_assigned_identity.workload.principal_id
}

output "managed_identity_client_id" {
  value = azurerm_user_assigned_identity.workload.client_id
}

output "agent_identity_id" {
  value = azurerm_user_assigned_identity.agent.id
}

output "agent_identity_principal_id" {
  value = azurerm_user_assigned_identity.agent.principal_id
}

# Policies Module - Azure Policy Definitions and Assignments

variable "management_group_name" { type = string }
variable "location" { type = string }

data "azurerm_subscription" "current" {}

# =============================================================================
# Built-in Initiative Assignments
# =============================================================================

resource "azurerm_subscription_policy_assignment" "azure_security_benchmark" {
  name                 = "mrg-azure-security-benchmark"
  subscription_id      = data.azurerm_subscription.current.id
  policy_definition_id = "/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8"
  display_name         = "Azure Security Benchmark - ${var.management_group_name}"
  location             = var.location

  identity {
    type = "SystemAssigned"
  }
}

# =============================================================================
# Custom Policy: Deny Public IP on NIC
# =============================================================================

resource "azurerm_policy_definition" "deny_public_ip" {
  name         = "mrg-deny-public-ip-on-nic"
  policy_type  = "Custom"
  mode         = "All"
  display_name = "Deny Public IP addresses on NICs"
  description  = "Prevents association of public IP addresses with network interfaces"

  policy_rule = jsonencode({
    if = {
      allOf = [
        {
          field  = "type"
          equals = "Microsoft.Network/networkInterfaces"
        },
        {
          count = {
            field = "Microsoft.Network/networkInterfaces/ipconfigurations[*]"
            where = {
              field     = "Microsoft.Network/networkInterfaces/ipconfigurations[*].publicIpAddress.id"
              notEquals = ""
            }
          }
          greaterOrEquals = 1
        }
      ]
    }
    then = {
      effect = "Deny"
    }
  })
}

# =============================================================================
# Custom Policy: Require TLS 1.2
# =============================================================================

resource "azurerm_policy_definition" "require_tls" {
  name         = "mrg-require-tls-1-2"
  policy_type  = "Custom"
  mode         = "All"
  display_name = "Require minimum TLS version 1.2"

  policy_rule = jsonencode({
    if = {
      allOf = [
        {
          field = "type"
          in    = ["Microsoft.Storage/storageAccounts", "Microsoft.Web/sites"]
        },
        {
          anyOf = [
            {
              field     = "Microsoft.Storage/storageAccounts/minimumTlsVersion"
              notEquals = "TLS1_2"
            },
            {
              field     = "Microsoft.Web/sites/siteConfig.minTlsVersion"
              notEquals = "1.2"
            }
          ]
        }
      ]
    }
    then = {
      effect = "Deny"
    }
  })
}

# =============================================================================
# Custom Policy: Enforce HTTPS
# =============================================================================

resource "azurerm_policy_definition" "enforce_https" {
  name         = "mrg-enforce-https"
  policy_type  = "Custom"
  mode         = "All"
  display_name = "Enforce HTTPS for web applications"

  policy_rule = jsonencode({
    if = {
      allOf = [
        {
          field  = "type"
          equals = "Microsoft.Web/sites"
        },
        {
          field     = "Microsoft.Web/sites/httpsOnly"
          notEquals = true
        }
      ]
    }
    then = {
      effect = "Deny"
    }
  })
}

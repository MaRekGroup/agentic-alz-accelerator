# Azure Landing Zone Accelerator - Main Terraform Configuration
# Orchestrates all landing zone modules based on profile configuration

terraform {
  required_version = ">= 1.9.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {
    # Configured via -backend-config at init time
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }
  subscription_id = var.subscription_id
}

# =============================================================================
# Variables
# =============================================================================

variable "subscription_id" {
  description = "Target Azure subscription ID"
  type        = string
}

variable "location" {
  description = "Azure region for the deployment"
  type        = string
  default     = "southcentralus"
}

variable "management_group_name" {
  description = "Management group name for the landing zone"
  type        = string
}

variable "profile_name" {
  description = "Landing zone profile name"
  type        = string
  validation {
    condition     = contains(["online", "corp", "sandbox", "sap"], var.profile_name)
    error_message = "Profile must be one of: online, corp, sandbox, sap"
  }
}

variable "vnet_address_space" {
  description = "Virtual network address space"
  type        = string
  default     = "10.1.0.0/16"
}

variable "enable_ddos" {
  description = "Enable DDoS protection"
  type        = bool
  default     = false
}

variable "enable_defender" {
  description = "Enable Defender for Cloud"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Log Analytics workspace retention in days"
  type        = number
  default     = 90
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "budget_amount_usd" {
  description = "Monthly budget amount in USD"
  type        = number
}

variable "budget_alert_emails" {
  description = "Budget alert email addresses"
  type        = list(string)
  default     = []
}

# =============================================================================
# Locals
# =============================================================================

locals {
  prefix = "mrg-${var.management_group_name}"

  default_tags = merge({
    Environment = "production"
    Owner       = "platform-team"
    CostCenter  = "platform"
    Project     = var.profile_name
    ManagedBy   = "agentic-alz-accelerator"
  }, var.tags)

  resource_group_names = {
    networking = "${local.prefix}-networking-rg"
    security   = "${local.prefix}-security-rg"
    logging    = "${local.prefix}-logging-rg"
    identity   = "${local.prefix}-identity-rg"
  }
}

# =============================================================================
# Resource Groups
# =============================================================================

resource "azurerm_resource_group" "networking" {
  name     = local.resource_group_names.networking
  location = var.location
  tags     = local.default_tags
}

resource "azurerm_resource_group" "security" {
  name     = local.resource_group_names.security
  location = var.location
  tags     = local.default_tags
}

resource "azurerm_resource_group" "logging" {
  name     = local.resource_group_names.logging
  location = var.location
  tags     = local.default_tags
}

resource "azurerm_resource_group" "identity" {
  name     = local.resource_group_names.identity
  location = var.location
  tags     = local.default_tags
}

# =============================================================================
# Module Deployments
# =============================================================================

module "logging" {
  source = "./modules/logging"

  resource_group_name = azurerm_resource_group.logging.name
  location            = var.location
  prefix              = local.prefix
  retention_days      = var.log_retention_days
  tags                = local.default_tags
}

module "networking" {
  source = "./modules/networking"

  resource_group_name        = azurerm_resource_group.networking.name
  location                   = var.location
  prefix                     = local.prefix
  vnet_address_space         = var.vnet_address_space
  enable_ddos                = var.enable_ddos
  log_analytics_workspace_id = module.logging.workspace_id
  tags                       = local.default_tags
}

module "security" {
  source = "./modules/security"

  resource_group_name        = azurerm_resource_group.security.name
  location                   = var.location
  prefix                     = local.prefix
  enable_defender            = var.enable_defender
  log_analytics_workspace_id = module.logging.workspace_id
  tags                       = local.default_tags
}

module "identity" {
  source = "./modules/identity"

  resource_group_name = azurerm_resource_group.identity.name
  location            = var.location
  prefix              = local.prefix
  tags                = local.default_tags
}

module "policies" {
  source = "./modules/policies"

  management_group_name = var.management_group_name
  location              = var.location
}

# =============================================================================
# Cost Governance
# =============================================================================

resource "azurerm_consumption_budget_subscription" "budget" {
  name            = "${local.prefix}-monthly-budget"
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

# =============================================================================
# Outputs
# =============================================================================

output "networking_resource_group" {
  value = azurerm_resource_group.networking.name
}

output "vnet_id" {
  value = module.networking.vnet_id
}

output "log_analytics_workspace_id" {
  value = module.logging.workspace_id
}

output "key_vault_id" {
  value = module.security.key_vault_id
}

output "managed_identity_id" {
  value = module.identity.managed_identity_id
}

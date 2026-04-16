---
name: terraform-patterns
description: "Reusable Terraform patterns and AVM-TF module examples for Azure Landing Zone deployments. USE FOR: Terraform code generation, module composition, hub-spoke networking. DO NOT USE FOR: Bicep patterns (use azure-bicep-patterns)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: iac-terraform
---

# Terraform Patterns Skill

Reusable Terraform patterns for the ALZ Accelerator.

## Hub-Spoke Network Pattern

```hcl
module "hub_vnet" {
  source  = "Azure/avm-res-network-virtualnetwork/azurerm"
  version = "~> 0.4"

  name                = "vnet-hub-${var.environment}-${var.location_short}"
  resource_group_name = azurerm_resource_group.hub.name
  location            = var.location
  address_space       = [var.hub_address_prefix]

  subnets = {
    AzureFirewallSubnet = { address_prefix = var.firewall_subnet_prefix }
    AzureBastionSubnet  = { address_prefix = var.bastion_subnet_prefix }
    GatewaySubnet       = { address_prefix = var.gateway_subnet_prefix }
  }

  tags = var.tags
}

# VNet Peering (hub → spoke)
resource "azurerm_virtual_network_peering" "hub_to_spoke" {
  name                      = "peer-hub-to-${var.spoke_name}"
  resource_group_name       = azurerm_resource_group.hub.name
  virtual_network_name      = module.hub_vnet.name
  remote_virtual_network_id = module.spoke_vnet.resource_id

  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = true
}
```

## Private Endpoint Pattern

```hcl
module "private_endpoint" {
  source  = "Azure/avm-res-network-privateendpoint/azurerm"
  version = "~> 0.5"

  name                = "pe-${var.resource_name}"
  resource_group_name = var.resource_group_name
  location            = var.location
  subnet_resource_id  = var.subnet_id

  private_service_connection_resource_id = var.target_resource_id
  private_service_connection_name        = "plsc-${var.resource_name}"
  private_service_connection_group_ids   = [var.group_id]

  private_dns_zone_resource_ids = [var.dns_zone_id]

  tags = var.tags
}
```

## Budget Pattern

```hcl
resource "azurerm_consumption_budget_subscription" "this" {
  name            = "budget-${var.environment}"
  subscription_id = data.azurerm_subscription.current.id
  amount          = var.budget_amount
  time_grain      = "Monthly"

  time_period {
    start_date = var.budget_start_date
  }

  notification {
    threshold      = 80
    threshold_type = "Forecasted"
    operator       = "GreaterThanOrEqualTo"
    contact_emails = var.alert_emails
  }

  notification {
    threshold      = 100
    threshold_type = "Forecasted"
    operator       = "GreaterThanOrEqualTo"
    contact_emails = var.alert_emails
    contact_groups = [azurerm_monitor_action_group.budget.id]
  }

  notification {
    threshold      = 120
    threshold_type = "Forecasted"
    operator       = "GreaterThanOrEqualTo"
    contact_emails = var.alert_emails
    contact_groups = [azurerm_monitor_action_group.budget.id]
  }
}
```

## Security Baseline Enforcement

```hcl
resource "azurerm_storage_account" "this" {
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = var.environment == "prod" ? false : true

  identity {
    type = "SystemAssigned"
  }
}
```

## State Management

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "stterraformstate"
    container_name       = "tfstate"
    key                  = "alz.terraform.tfstate"
  }
}
```

# ─────────────────────────────────────────────────────────────────────────────
# Platform Landing Zone: Connectivity Module (Terraform)
# CAF Design Area: Network Topology & Connectivity
#
# Supports:  hub-spoke (Azure Firewall)  |  vwan (Azure Virtual WAN)
# Select via: var.hub_topology = "hub-spoke" or "vwan"
# ─────────────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.9.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" }
  }
}

# ─── Variables ────────────────────────────────────────────────────────────────

variable "subscription_id"              { type = string }
variable "location"                     { type = string, default = "eastus2" }
variable "prefix"                       { type = string, description = "Naming prefix (≤10 chars)" }
variable "environment"                  { type = string, validation { condition = contains(["dev","staging","prod"], var.environment) } }

variable "hub_topology"                 { type = string, default = "hub-spoke", description = "hub-spoke or vwan" }
variable "hub_vnet_address_space"       { type = string, default = "10.0.0.0/16" }

variable "deploy_azure_firewall"        { type = bool, default = true }
variable "firewall_sku_tier"            { type = string, default = "Premium" }

variable "deploy_expressroute_gateway"  { type = bool, default = false }
variable "expressroute_gateway_sku"     { type = string, default = "ErGw1AZ" }

variable "deploy_vpn_gateway"           { type = bool, default = false }
variable "vpn_gateway_sku"              { type = string, default = "VpnGw1AZ" }

variable "enable_ddos_protection"       { type = bool, default = true }
variable "enable_bastion"               { type = bool, default = true }
variable "bastion_sku"                  { type = string, default = "Standard" }

variable "private_dns_zones" {
  type = list(string)
  default = [
    "privatelink.database.windows.net",
    "privatelink.blob.core.windows.net",
    "privatelink.file.core.windows.net",
    "privatelink.vaultcore.azure.net",
    "privatelink.azurewebsites.net",
    "privatelink.azurecr.io",
    "privatelink.openai.azure.com",
    "privatelink.servicebus.windows.net",
    "privatelink.cognitiveservices.azure.com",
  ]
}

variable "log_analytics_workspace_id"  { type = string, description = "From management subscription" }
variable "budget_amount_usd"            { type = number }
variable "budget_alert_emails"          { type = list(string), default = [] }

variable "tags" {
  type    = map(string)
  default = {}
}

# ─── Locals ───────────────────────────────────────────────────────────────────

locals {
  region_shortcodes = {
    eastus        = "eus"
    eastus2       = "eus2"
    westus        = "wus"
    westus2       = "wus2"
    westus3       = "wus3"
    centralus     = "cus"
    northeurope   = "neu"
    westeurope    = "weu"
    uksouth       = "uks"
    southeastasia = "sea"
    australiaeast = "aue"
    japaneast     = "jpe"
  }
  region_code = lookup(local.region_shortcodes, var.location, var.location)

  rg_hub      = "${var.prefix}-conn-hub-${local.region_code}-rg"
  rg_gateways = "${var.prefix}-conn-gateways-${local.region_code}-rg"
  rg_dns      = "${var.prefix}-conn-dns-${local.region_code}-rg"
  rg_ddos     = "${var.prefix}-conn-ddos-rg"

  common_tags = merge({
    environment = var.environment
    managed_by  = "agentic-alz-accelerator"
    cost_center = "platform"
  }, var.tags)

  # Hub-Spoke subnet layout
  hub_subnets = {
    AzureFirewallSubnet           = "10.0.0.0/26"
    AzureFirewallManagementSubnet = "10.0.0.64/26"
    GatewaySubnet                 = "10.0.1.0/27"
    AzureBastionSubnet            = "10.0.2.0/26"
    dns-resolver-inbound          = "10.0.3.0/28"
    dns-resolver-outbound         = "10.0.3.16/28"
  }
}

# ─── Resource Groups ──────────────────────────────────────────────────────────

resource "azurerm_resource_group" "hub" {
  name     = local.rg_hub
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_resource_group" "gateways" {
  name     = local.rg_gateways
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_resource_group" "dns" {
  name     = local.rg_dns
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_resource_group" "ddos" {
  count    = var.enable_ddos_protection ? 1 : 0
  name     = local.rg_ddos
  location = var.location
  tags     = local.common_tags
}

# ─── Cost Governance — Budget Alerts (mandatory) ──────────────────────────────

resource "azurerm_consumption_budget_subscription" "connectivity" {
  name            = "${var.prefix}-conn-monthly-budget"
  subscription_id = "/subscriptions/${var.subscription_id}"
  amount          = var.budget_amount_usd
  time_grain      = "Monthly"

  time_period {
    start_date = formatdate("YYYY-MM-01'T'00:00:00Z", timestamp())
  }

  dynamic "notification" {
    for_each = [
      { threshold = 80, name = "forecast-80-pct" },
      { threshold = 100, name = "forecast-100-pct" },
      { threshold = 120, name = "forecast-120-pct" },
    ]
    content {
      enabled        = true
      threshold      = notification.value.threshold
      threshold_type = "Forecasted"
      operator       = "GreaterThan"
      contact_emails = var.budget_alert_emails
    }
  }
}

# ─── DDoS Protection Plan ─────────────────────────────────────────────────────

resource "azurerm_network_ddos_protection_plan" "this" {
  count               = var.enable_ddos_protection ? 1 : 0
  name                = "${var.prefix}-ddos-plan"
  location            = var.location
  resource_group_name = azurerm_resource_group.ddos[0].name
  tags                = local.common_tags
}

# ─── Hub-Spoke: Hub VNet ──────────────────────────────────────────────────────

resource "azurerm_virtual_network" "hub" {
  count               = var.hub_topology == "hub-spoke" ? 1 : 0
  name                = "${var.prefix}-hub-vnet"
  location            = var.location
  resource_group_name = azurerm_resource_group.hub.name
  address_space       = [var.hub_vnet_address_space]
  tags                = local.common_tags

  dynamic "ddos_protection_plan" {
    for_each = var.enable_ddos_protection ? [1] : []
    content {
      id     = azurerm_network_ddos_protection_plan.this[0].id
      enable = true
    }
  }
}

resource "azurerm_subnet" "hub_subnets" {
  for_each             = var.hub_topology == "hub-spoke" ? local.hub_subnets : {}
  name                 = each.key
  resource_group_name  = azurerm_resource_group.hub.name
  virtual_network_name = azurerm_virtual_network.hub[0].name
  address_prefixes     = [each.value]

  delegation {
    name = "dns-delegation"
    service_delegation {
      name = startswith(each.key, "dns-resolver") ? "Microsoft.Network/dnsResolvers" : "Microsoft.Network/virtualNetworks"
    }
  }
}

# ─── Hub-Spoke: Azure Firewall ────────────────────────────────────────────────

resource "azurerm_firewall_policy" "this" {
  count               = var.deploy_azure_firewall ? 1 : 0
  name                = "${var.prefix}-firewall-policy"
  location            = var.location
  resource_group_name = azurerm_resource_group.hub.name
  sku                 = var.firewall_sku_tier
  tags                = local.common_tags

  dns { proxy_enabled = true }

  dynamic "intrusion_detection" {
    for_each = var.firewall_sku_tier == "Premium" ? [1] : []
    content { mode = "Deny" }
  }
}

resource "azurerm_firewall" "this" {
  count               = (var.hub_topology == "hub-spoke" && var.deploy_azure_firewall) ? 1 : 0
  name                = "${var.prefix}-azure-firewall"
  location            = var.location
  resource_group_name = azurerm_resource_group.hub.name
  sku_name            = "AZFW_VNet"
  sku_tier            = var.firewall_sku_tier
  firewall_policy_id  = azurerm_firewall_policy.this[0].id
  zones               = ["1", "2", "3"]
  tags                = local.common_tags

  ip_configuration {
    name      = "fw-ip-config"
    subnet_id = azurerm_subnet.hub_subnets["AzureFirewallSubnet"].id
    public_ip_address_id = azurerm_public_ip.firewall[0].id
  }

  management_ip_configuration {
    name      = "fw-mgmt-ip-config"
    subnet_id = azurerm_subnet.hub_subnets["AzureFirewallManagementSubnet"].id
    public_ip_address_id = azurerm_public_ip.firewall_mgmt[0].id
  }

  depends_on = [azurerm_subnet.hub_subnets]
}

resource "azurerm_public_ip" "firewall" {
  count               = (var.hub_topology == "hub-spoke" && var.deploy_azure_firewall) ? 1 : 0
  name                = "${var.prefix}-fw-pip"
  location            = var.location
  resource_group_name = azurerm_resource_group.hub.name
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = ["1", "2", "3"]
  tags                = local.common_tags
}

resource "azurerm_public_ip" "firewall_mgmt" {
  count               = (var.hub_topology == "hub-spoke" && var.deploy_azure_firewall) ? 1 : 0
  name                = "${var.prefix}-fw-mgmt-pip"
  location            = var.location
  resource_group_name = azurerm_resource_group.hub.name
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = ["1", "2", "3"]
  tags                = local.common_tags
}

# ─── Hub-Spoke: Azure Bastion ─────────────────────────────────────────────────

resource "azurerm_bastion_host" "this" {
  count               = (var.hub_topology == "hub-spoke" && var.enable_bastion) ? 1 : 0
  name                = "${var.prefix}-bastion"
  location            = var.location
  resource_group_name = azurerm_resource_group.hub.name
  sku                 = var.bastion_sku
  scale_units         = var.bastion_sku == "Standard" ? 2 : 2
  tags                = local.common_tags

  ip_configuration {
    name      = "bastion-ip-config"
    subnet_id = azurerm_subnet.hub_subnets["AzureBastionSubnet"].id
    public_ip_address_id = azurerm_public_ip.bastion[0].id
  }
}

resource "azurerm_public_ip" "bastion" {
  count               = (var.hub_topology == "hub-spoke" && var.enable_bastion) ? 1 : 0
  name                = "${var.prefix}-bastion-pip"
  location            = var.location
  resource_group_name = azurerm_resource_group.hub.name
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = ["1", "2", "3"]
  tags                = local.common_tags
}

# ─── Private DNS Zones ────────────────────────────────────────────────────────

resource "azurerm_private_dns_zone" "zones" {
  for_each            = toset(var.private_dns_zones)
  name                = each.value
  resource_group_name = azurerm_resource_group.dns.name
  tags                = local.common_tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "hub_links" {
  for_each              = toset(var.private_dns_zones)
  name                  = "${var.prefix}-hub-link"
  resource_group_name   = azurerm_resource_group.dns.name
  private_dns_zone_name = azurerm_private_dns_zone.zones[each.value].name
  virtual_network_id    = var.hub_topology == "hub-spoke" ? azurerm_virtual_network.hub[0].id : ""
  registration_enabled  = false
  tags                  = local.common_tags
}

# ─── Azure Virtual WAN ────────────────────────────────────────────────────────

resource "azurerm_virtual_wan" "this" {
  count               = var.hub_topology == "vwan" ? 1 : 0
  name                = "${var.prefix}-vwan"
  resource_group_name = azurerm_resource_group.hub.name
  location            = var.location
  type                = "Standard"
  tags                = local.common_tags
}

resource "azurerm_virtual_hub" "primary" {
  count               = var.hub_topology == "vwan" ? 1 : 0
  name                = "${var.prefix}-vhub-${local.region_code}"
  resource_group_name = azurerm_resource_group.hub.name
  location            = var.location
  virtual_wan_id      = azurerm_virtual_wan.this[0].id
  address_prefix      = "10.200.0.0/23"
  tags                = local.common_tags
}

# ─── Diagnostic Settings ──────────────────────────────────────────────────────

resource "azurerm_monitor_diagnostic_setting" "firewall" {
  count                      = var.deploy_azure_firewall ? 1 : 0
  name                       = "${var.prefix}-fw-diag"
  target_resource_id         = azurerm_firewall.this[0].id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log { category = "AzureFirewallApplicationRule" }
  enabled_log { category = "AzureFirewallNetworkRule" }
  enabled_log { category = "AzureFirewallDnsProxy" }
  metric { category = "AllMetrics" }
}

# ─── Outputs ──────────────────────────────────────────────────────────────────

output "hub_vnet_id"               { value = var.hub_topology == "hub-spoke" ? azurerm_virtual_network.hub[0].id : "" }
output "hub_topology"              { value = var.hub_topology }
output "ddos_protection_plan_id"   { value = var.enable_ddos_protection ? azurerm_network_ddos_protection_plan.this[0].id : "" }
output "azure_firewall_private_ip" { value = var.deploy_azure_firewall ? azurerm_firewall.this[0].ip_configuration[0].private_ip_address : "" }
output "private_dns_zone_ids"      { value = [for z in azurerm_private_dns_zone.zones : z.id] }
output "vwan_id"                   { value = var.hub_topology == "vwan" ? azurerm_virtual_wan.this[0].id : "" }

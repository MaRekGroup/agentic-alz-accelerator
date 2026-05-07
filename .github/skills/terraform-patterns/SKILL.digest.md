<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Terraform Patterns Skill (Digest)

Reusable Terraform patterns for ALZ Accelerator deployments. All patterns use AVM modules where available.

## Pattern Index

| Pattern | AVM Module | Key Resources |
|---------|-----------|---------------|
| Hub-Spoke Network | `Azure/avm-res-network-virtualnetwork/azurerm ~> 0.4` | Hub VNet, subnets (Firewall, Bastion, Gateway), VNet peering |
| Private Endpoint | `Azure/avm-res-network-privateendpoint/azurerm ~> 0.5` | Private endpoint, DNS zone link, service connection |
| Budget | Native `azurerm_consumption_budget_subscription` | Budget with 80/100/120% forecast notifications |
| Security Baseline | Native `azurerm_storage_account` (example) | TLS 1.2, HTTPS-only, no public blob, managed identity, env-conditional public access |
| State Management | `backend "azurerm"` | Remote state in Azure Storage (`rg-terraform-state` / `stterraformstate`) |

## Hub-Spoke Key Details

- Hub subnets: `AzureFirewallSubnet`, `AzureBastionSubnet`, `GatewaySubnet`
- Peering flags: `allow_virtual_network_access`, `allow_forwarded_traffic`, `allow_gateway_transit`

## Security Baseline Enforcement

Storage account pattern enforces: `min_tls_version = "TLS1_2"`, `https_traffic_only_enabled = true`, `allow_nested_items_to_be_public = false`, `public_network_access_enabled` conditional on environment, `identity { type = "SystemAssigned" }`.

## Budget Pattern

Three notification blocks at 80%, 100%, 120% forecast thresholds with `contact_emails` and `contact_groups` (action group for 100%+).

> _See SKILL.md for full HCL code examples._

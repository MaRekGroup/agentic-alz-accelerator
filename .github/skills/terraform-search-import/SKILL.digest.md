<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Terraform Search & Import Skill (Digest)

Discover existing Azure resources and generate Terraform configuration for bulk import — critical for brownfield Landing Zone onboarding.

## When to Use

- Brownfield scenarios requiring IaC management of existing resources
- Post-assessment (Step 0) migration to CAF-aligned Terraform
- Importing platform resources deployed outside the accelerator

## Decision Tree

**Primary workflow = Manual Discovery** via `az` CLI (always works with azurerm ~> 4.0).
**Secondary = Terraform Search** (experimental, TF >= 1.14).

## Manual Discovery Workflow

1. **Discover** — `az resource list --subscription` / `--resource-group` / `--tag`
2. **Create import blocks** — Paired `import {}` + `resource {}` blocks in `imports.tf`
3. **Plan and apply** — `terraform plan` (import actions only), then `terraform apply`

## Landing Zone Resource Type Mapping

| Platform LZ | Azure Type | Terraform Resource | Import Pattern |
|---|---|---|---|
| Management | `Microsoft.OperationalInsights/workspaces` | `azurerm_log_analytics_workspace` | `module.management.*.central` |
| Management | `Microsoft.Automation/automationAccounts` | `azurerm_automation_account` | `module.management.*.main` |
| Connectivity | `Microsoft.Network/virtualNetworks` | `azurerm_virtual_network` | `module.connectivity.*.hub` |
| Connectivity | `Microsoft.Network/bastionHosts` | `azurerm_bastion_host` | `module.connectivity.*.main` |
| Connectivity | `Microsoft.Network/azureFirewalls` | `azurerm_firewall` | `module.connectivity.*.hub` |
| Identity | `Microsoft.ManagedIdentity/userAssignedIdentities` | `azurerm_user_assigned_identity` | `module.identity.*` |
| Security | `Microsoft.KeyVault/vaults` | `azurerm_key_vault` | `module.security.*.platform` |

Import ID format: `/subscriptions/{sub}/resourceGroups/{rg}/providers/{type}/{name}`

## Post-Import: Adopt AVM Modules

Refactor imported `azurerm_*` resources to AVM modules using `moved {}` blocks.

## Security Baseline Enforcement Post-Import

Validate all 6 non-negotiable rules after import. Non-compliant resources require immediate remediation.

## Constraints

- **Never** run `terraform import` or `terraform apply` locally — use GitHub Actions
- **Always** preview with `terraform plan` before applying
- Import blocks go in `imports.tf` (separate from resource definitions)
- Remove `import {}` blocks after successful import
- Tag imported resources with `ManagedBy = "terraform"`

> _See SKILL.md for full HCL examples, assessment integration details, and search workflow._

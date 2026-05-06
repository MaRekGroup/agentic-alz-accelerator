---
name: terraform-search-import
description: "Discover existing Azure resources and bulk import them into Terraform management for brownfield Landing Zones. USE FOR: import Azure resources, bring unmanaged infra under Terraform, brownfield migration, generate import blocks. DO NOT USE FOR: Bicep code (use azure-bicep-patterns), new resource creation, architecture decisions."
compatibility: azurerm ~> 4.0 + Azure CLI. Search workflow requires Terraform >= 1.14 (experimental).
---

# Terraform Search & Import for Enterprise Landing Zones

Discover existing Azure resources and generate Terraform configuration for bulk
import — critical for brownfield Landing Zone onboarding.

## When to Use

- Brownfield scenarios where existing resources must come under IaC management
- Post-assessment (Step 0) when migrating to CAF-aligned Terraform
- Importing platform resources already deployed outside the accelerator

## Decision Tree

```text
┌─ Identify target Azure resources (from 00-assessment-report.json)
│
├─ PRIMARY: Manual Discovery via az CLI (always works)
│  └─ az resource list → create import blocks → terraform plan → apply
│
└─ SECONDARY: Terraform Search (EXPERIMENTAL, TF >= 1.14)
   ├─ Check: terraform version >= 1.14?
   │  └─ NO → use Manual workflow
   └─ YES → use Search workflow (.tfquery.hcl)
```

**Primary workflow = Manual Discovery** via `az` CLI. Always works with azurerm ~> 4.0.

---

## Manual Discovery Workflow (Primary)

### Step 1: Discover Resources

Use assessment artifacts as the starting point:

```bash
# From assessment report — list resources in a platform LZ subscription
az resource list --subscription "ME-MngEnvMCAP084543-ytesfaye-3" --output table

# Filter by resource group (platform LZ pattern)
az resource list --resource-group rg-{prefix}-connectivity-{region} --output json

# By tag (CAF-required tags)
az resource list --tag ManagedBy=terraform --output json
```

### Step 2: Create Import Blocks

For each resource, create paired `import` + `resource` blocks:

```hcl
# Platform connectivity — hub VNet
import {
  to = module.connectivity.azurerm_virtual_network.hub
  id = "/subscriptions/{sub-id}/resourceGroups/rg-mrg-connectivity-scus/providers/Microsoft.Network/virtualNetworks/vnet-mrg-hub-scus"
}

# Platform management — Log Analytics Workspace
import {
  to = module.management.azurerm_log_analytics_workspace.central
  id = "/subscriptions/{sub-id}/resourceGroups/rg-mrg-management-scus/providers/Microsoft.OperationalInsights/workspaces/law-mrg-scus"
}
```

### Step 3: Plan and Apply

```bash
cd infra/terraform/{customer}/
terraform plan    # Review — should show import actions only, no creates/destroys
terraform apply   # Execute imports
```

---

## Landing Zone Resource Type Mapping

| Platform LZ | Azure Type | Terraform Resource | Import Pattern |
|---|---|---|---|
| Management | `Microsoft.OperationalInsights/workspaces` | `azurerm_log_analytics_workspace` | `module.management.azurerm_log_analytics_workspace.central` |
| Management | `Microsoft.Automation/automationAccounts` | `azurerm_automation_account` | `module.management.azurerm_automation_account.main` |
| Connectivity | `Microsoft.Network/virtualNetworks` | `azurerm_virtual_network` | `module.connectivity.azurerm_virtual_network.hub` |
| Connectivity | `Microsoft.Network/bastionHosts` | `azurerm_bastion_host` | `module.connectivity.azurerm_bastion_host.main` |
| Connectivity | `Microsoft.Network/azureFirewalls` | `azurerm_firewall` | `module.connectivity.azurerm_firewall.hub` |
| Identity | `Microsoft.ManagedIdentity/userAssignedIdentities` | `azurerm_user_assigned_identity` | `module.identity.azurerm_user_assigned_identity.*` |
| Security | `Microsoft.KeyVault/vaults` | `azurerm_key_vault` | `module.security.azurerm_key_vault.platform` |
| Security | `Microsoft.OperationsManagement/solutions` | `azurerm_sentinel_log_analytics_workspace_onboarding` | `module.security.azurerm_sentinel_*` |

Import ID format: `/subscriptions/{sub}/resourceGroups/{rg}/providers/{type}/{name}`

---

## Post-Import: Adopt AVM Modules

After importing raw `azurerm_*` resources, refactor to AVM modules using `moved {}` blocks:

```hcl
# Refactor imported VNet to AVM module
moved {
  from = azurerm_virtual_network.hub
  to   = module.hub_vnet.azurerm_virtual_network.this
}

module "hub_vnet" {
  source  = "Azure/avm-res-network-virtualnetwork/azurerm"
  version = "~> 0.7"
  # ...
}
```

---

## Integration with Assessment (Step 0)

When running brownfield onboarding:

1. **Assessment** produces `00-assessment-report.json` with resource inventory
2. **Requirements** (Step 1) captures `decisions.iac_tool = "terraform"`
3. **This skill** generates import blocks from the assessment inventory
4. **IaC Planner** (Step 4) maps imported resources to AVM modules
5. **Forge** (Step 5) generates the final refactored Terraform with `moved {}` blocks

---

## Security Baseline Enforcement Post-Import

After import, validate all resources meet the 6 non-negotiable security rules:

| # | Rule | Check Command |
|---|------|---|
| 1 | TLS 1.2 minimum | `terraform plan` shows no `min_tls_version` changes needed |
| 2 | HTTPS-only | Verify `https_traffic_only_enabled = true` in state |
| 3 | No public blob access | Verify `allow_nested_items_to_be_public = false` |
| 4 | Managed Identity | Verify `identity { type = "SystemAssigned" }` exists |
| 5 | Azure AD-only SQL | Verify `azuread_authentication_only = true` |
| 6 | Public network disabled (prod) | Verify `public_network_access_enabled = false` |

Non-compliant resources require immediate remediation plan in the implementation step.

---

## Constraints

- **Never** run `terraform import` or `terraform apply` locally — use GitHub Actions
- **Always** preview with `terraform plan` before applying
- Import blocks go in `imports.tf` (separate from resource definitions)
- After successful import, remove `import {}` blocks and commit clean state
- Tag imported resources with `ManagedBy = "terraform"` post-import

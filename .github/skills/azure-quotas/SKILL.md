---
name: azure-quotas
description: "Check and manage Azure quotas and usage across providers for Enterprise Landing Zone deployment planning. USE FOR: quota checks, service limits, capacity validation, region selection, quota increase requests. DO NOT USE FOR: cost optimization (use azure-cost-optimization), pricing lookups (use azure-pricing MCP)."
compatibility: Requires Azure CLI with quota extension. Works via GitHub Actions or local az CLI.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: deployment
---

# Azure Quotas — Service Limits & Capacity Management

Check and validate Azure quotas before Enterprise Landing Zone deployments.
Prevents deployment failures from quota exhaustion across platform and
application landing zone subscriptions.

## When to Use This Skill

- **Before platform LZ deployment** — validate capacity in target subscriptions
- **Region selection** — compare quota availability across regions
- **Quota exceeded errors** — diagnose and resolve deployment failures
- **Capacity planning** — ensure subscriptions can handle planned resources
- **New app landing zone** — verify target subscription has sufficient quota

## Quick Reference

| Property | Details |
|----------|---------|
| **Primary Tool** | Azure CLI (`az quota`) — USE THIS FIRST |
| **Extension** | `az extension add --name quota` (install first) |
| **Key Commands** | `az quota list`, `az quota show`, `az quota usage list` |
| **Required Permission** | Reader (view) or Quota Request Operator (manage) |

> **ALWAYS USE CLI FIRST.** REST API and Portal show unreliable/cached data.
> "No Limit" in REST API does NOT mean unlimited capacity.

## ALZ Platform LZ Quota Checks

Before deploying platform landing zones, validate these quotas:

### Management LZ

| Resource | Quota Name | Minimum Required |
|----------|-----------|------------------|
| Log Analytics Workspace | `Microsoft.OperationalInsights` | 1 |
| Automation Account | `Microsoft.Automation` | 1 |
| Storage Account | `Microsoft.Storage/storageAccounts` | 1 |

### Connectivity LZ

| Resource | Quota Name | Minimum Required |
|----------|-----------|------------------|
| Virtual Networks | `Microsoft.Network/virtualNetworks` | 2+ (hub + spokes) |
| Public IPs | `Microsoft.Network/publicIPAddresses` | 2+ (Bastion + Firewall) |
| Bastion Hosts | `Microsoft.Network/bastionHosts` | 1 |
| Azure Firewall | `Microsoft.Network/azureFirewalls` | 0-1 (optional) |
| VNet Peerings | `Microsoft.Network/virtualNetworks/virtualNetworkPeerings` | N (spoke count) |
| Private DNS Zones | `Microsoft.Network/privateDnsZones` | 10+ |

### Identity LZ

| Resource | Quota Name | Minimum Required |
|----------|-----------|------------------|
| Virtual Networks | `Microsoft.Network/virtualNetworks` | 1 (spoke) |
| Managed Identities | `Microsoft.ManagedIdentity` | 5+ |

### Security LZ

| Resource | Quota Name | Minimum Required |
|----------|-----------|------------------|
| Key Vaults | `Microsoft.KeyVault/vaults` | 1+ |
| Log Analytics Solutions | `Microsoft.OperationsManagement` | 1 (Sentinel) |

## Quota Check Workflow

```bash
# 1. Install quota extension
az extension add --name quota

# 2. Set subscription context
az account set --subscription "$PLATFORM_CONN_SUBSCRIPTION_ID"

# 3. Discover quota resource names
az quota list \
  --scope "/subscriptions/{sub-id}/providers/Microsoft.Network/locations/southcentralus" \
  --output table

# 4. Check specific quota usage
az quota usage show \
  --resource-name "VirtualNetworks" \
  --scope "/subscriptions/{sub-id}/providers/Microsoft.Network/locations/southcentralus" \
  --output json

# 5. Validate capacity
# Available = Limit - (Current Usage + Planned Resources)
```

## Multi-Subscription Check (ALZ Estate)

For Enterprise Landing Zones, check quotas across ALL platform subscriptions:

```bash
#!/bin/bash
# Check quotas across all platform subscriptions
for sub in PLATFORM_MGMT_SUBSCRIPTION_ID PLATFORM_CONN_SUBSCRIPTION_ID \
           PLATFORM_IDTY_SUBSCRIPTION_ID PLATFORM_SEC_SUBSCRIPTION_ID; do
  sub_id=$(gh secret list | grep "$sub" | awk '{print $1}')
  echo "=== Checking $sub ==="
  az account set --subscription "$sub_id"
  az quota usage list \
    --scope "/subscriptions/$sub_id/providers/Microsoft.Compute/locations/southcentralus" \
    --output table 2>/dev/null | head -20
done
```

## Quota Increase Request

```bash
# Request quota increase (free — only pay for what you use)
az quota create \
  --resource-name "StandardDSv3Family" \
  --scope "/subscriptions/{sub-id}/providers/Microsoft.Compute/locations/southcentralus" \
  --limit-object value=100 limit-object-type=LimitValue \
  --resource-type "dedicated"
```

## Integration with Workflow

| Step | Agent | How Quotas Are Used |
|------|-------|---------------------|
| Step 2 (Architecture) | Oracle | Region selection considers quota availability |
| Step 4 (Plan) | Strategist | Validate capacity for planned resources |
| Step 5 (Validation) | azure-validate | Check quotas as part of preflight |
| Step 6 (Deploy) | Envoy | Diagnose quota-related deployment failures |

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `QuotaExceeded` | Usage + request > limit | Request quota increase or reduce request |
| `BadRequest` | Provider doesn't support quota API | Check docs for service-specific limits |
| `ExtensionNotFound` | Quota extension not installed | `az extension add --name quota` |
| `InvalidScope` | Wrong scope format | Use `/subscriptions/{id}/providers/{provider}/locations/{region}` |

## Best Practices

1. **Check before deploy** — always validate quotas before triggering workflows
2. **Buffer 20%** — request quota 20% above immediate needs for growth
3. **Per-subscription** — each LZ subscription has independent quotas
4. **Region matters** — quotas differ by region; southcentralus is our default
5. **Document sources** — track whether limit came from quota API or Azure docs

## Guardrails

**DO:** Use `az quota` CLI first · Check all platform subscriptions · Request
increases proactively · Validate before deployment workflows.

**DON'T:** Trust REST API "No Limit" values · Assume ARM type = quota name ·
Skip quota checks for "small" deployments · Hard-code subscription IDs.

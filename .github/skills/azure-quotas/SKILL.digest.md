<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Quotas Skill (Digest)

Check and validate Azure quotas before Enterprise Landing Zone deployments.

## Quick Reference

| Property | Details |
|----------|---------|
| **Primary Tool** | Azure CLI (`az quota`) — USE THIS FIRST |
| **Extension** | `az extension add --name quota` |
| **Key Commands** | `az quota list`, `az quota show`, `az quota usage list` |
| **Required Permission** | Reader (view) or Quota Request Operator (manage) |

## ALZ Platform LZ Quota Checks

| LZ | Key Resources | Minimum Required |
|----|---------------|------------------|
| Management | LAW, Automation Account, Storage | 1 each |
| Connectivity | VNets (2+), Public IPs (2+), Bastion (1), Firewall (0-1), Peerings (N), DNS Zones (10+) | varies |
| Identity | VNet (1), Managed Identities (5+) | varies |
| Security | Key Vaults (1+), Sentinel (1) | varies |

## Workflow Integration

| Step | Agent | Usage |
|------|-------|-------|
| Step 2 | Oracle | Region selection considers quota availability |
| Step 4 | Strategist | Validate capacity for planned resources |
| Step 5 | azure-validate | Preflight quota checks |
| Step 6 | Envoy | Diagnose quota-related failures |

## Troubleshooting

| Error | Fix |
|-------|-----|
| `QuotaExceeded` | Request increase or reduce request |
| `BadRequest` | Check docs for service-specific limits |
| `ExtensionNotFound` | `az extension add --name quota` |
| `InvalidScope` | Use `/subscriptions/{id}/providers/{provider}/locations/{region}` |

## Best Practices

1. Always check before deploy
2. Buffer 20% above immediate needs
3. Each LZ subscription has independent quotas
4. Quotas differ by region
5. Document whether limit came from API or docs

> _See SKILL.md for full CLI examples and multi-subscription check scripts._

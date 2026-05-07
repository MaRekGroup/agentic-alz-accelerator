<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Bicep Patterns Skill (Digest)

Reusable Bicep patterns for ALZ Accelerator deployments using AVM modules.

## Pattern Reference

| Pattern | AVM Module / Resource | Key Properties |
|---------|----------------------|----------------|
| Hub-Spoke Network | `br/public:avm/res/network/virtual-network:0.4.0` | AzureFirewallSubnet, AzureBastionSubnet, GatewaySubnet |
| Private Endpoint | `br/public:avm/res/network/private-endpoint:0.7.0` | privateLinkServiceConnections, privateDnsZoneGroups |
| Diagnostic Settings | `Microsoft.Insights/diagnosticSettings@2021-05-01-preview` | allLogs + AllMetrics → Log Analytics |
| Budget | `Microsoft.Consumption/budgets@2023-11-01` | 80%/100%/120% forecast thresholds, parameterized amounts |
| Security Baseline (Storage) | `Microsoft.Storage/storageAccounts@2023-05-01` | TLS1_2, HTTPS-only, no public blob, SystemAssigned identity, public network disabled for prod |

> _See SKILL.md for full Bicep code blocks for each pattern._

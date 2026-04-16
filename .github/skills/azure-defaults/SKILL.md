---
name: azure-defaults
description: "Azure infrastructure defaults: regions, tags, naming (CAF), AVM-first policy, security baseline, unique suffix patterns. USE FOR: any agent generating or planning Azure resources. DO NOT USE FOR: artifact template structures (use azure-artifacts), pricing lookups (read references/pricing-guidance.md on demand)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: azure-infrastructure
---

# Azure Defaults Skill

Standard Azure conventions and defaults for the Agentic ALZ Accelerator.

## Naming Conventions (CAF)

| Resource | Pattern | Example |
|----------|---------|---------|
| Resource Group | `rg-{workload}-{env}-{region}` | `rg-alz-prod-scus` |
| Virtual Network | `vnet-{workload}-{env}-{region}` | `vnet-hub-prod-scus` |
| Subnet | `snet-{purpose}-{env}` | `snet-gateway-prod` |
| Storage Account | `st{workload}{env}{region}{suffix}` | `stalzprodscus001` |
| Key Vault | `kv-{workload}-{env}-{suffix}` | `kv-alz-prod-001` |
| Log Analytics | `log-{workload}-{env}-{region}` | `log-alz-prod-scus` |
| NSG | `nsg-{subnet}-{env}` | `nsg-gateway-prod` |
| Route Table | `rt-{subnet}-{env}` | `rt-gateway-prod` |
| Azure Firewall | `afw-{workload}-{env}-{region}` | `afw-hub-prod-scus` |
| Bastion | `bas-{workload}-{env}-{region}` | `bas-hub-prod-scus` |
| Public IP | `pip-{resource}-{env}-{region}` | `pip-afw-prod-scus` |
| Management Group | `mg-{purpose}` | `mg-platform`, `mg-landingzones` |

## Required Tags

All resource groups must have:

| Tag | Description | Example |
|-----|-------------|---------|
| `Environment` | Deployment environment | `prod`, `dev`, `staging` |
| `Owner` | Team or person responsible | `platform-team` |
| `CostCenter` | Billing cost center | `CC-12345` |
| `Project` | Project name | `alz-accelerator` |
| `ManagedBy` | IaC framework | `bicep`, `terraform` |

## Default Region

`southcentralus` (configurable via `AZURE_DEPLOYMENT_REGION` env var)

## AVM Module Registry

- Bicep: `br/public:avm/res/{provider}/{type}:{version}`
- Terraform: `Azure/avm-res-{provider}-{type}/azurerm`

Always check for AVM module availability before writing native resources.

## WAF Pillar Alignment

Every resource should be assessed against:

1. **Security** — TLS 1.2+, managed identity, private endpoints
2. **Reliability** — Zone redundancy, backups, monitoring
3. **Cost Optimization** — Right-sizing, reserved instances, budgets
4. **Performance** — Scaling, caching, CDN
5. **Operational Excellence** — IaC, diagnostics, alerts

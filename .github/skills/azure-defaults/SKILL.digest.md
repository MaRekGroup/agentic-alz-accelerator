<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Defaults Skill (Digest)

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
| Azure Firewall | `afw-{workload}-{env}-{region}` | `afw-hub-prod-scus` |
| Bastion | `bas-{workload}-{env}-{region}` | `bas-hub-prod-scus` |
| Public IP | `pip-{resource}-{env}-{region}` | `pip-afw-prod-scus` |
| Management Group | `mg-{purpose}` | `mg-platform` |

## Required Tags

| Tag | Description | Example |
|-----|-------------|---------|
| `Environment` | Deployment environment | `prod`, `dev`, `staging` |
| `Owner` | Team or person responsible | `platform-team` |
| `CostCenter` | Billing cost center | `CC-12345` |
| `Project` | Project name | `alz-accelerator` |
| `ManagedBy` | IaC framework | `bicep`, `terraform` |

## Key Defaults

- **Default Region:** `southcentralus` (configurable via `AZURE_DEPLOYMENT_REGION`)
- **AVM Registry (Bicep):** `br/public:avm/res/{provider}/{type}:{version}`
- **AVM Registry (Terraform):** `Azure/avm-res-{provider}-{type}/azurerm`
- **AVM-first:** Always check for AVM module availability before writing native resources

## WAF Pillar Alignment

Every resource assessed against: Security (TLS 1.2+, MI, PE), Reliability (zone redundancy, backups), Cost Optimization (right-sizing, budgets), Performance (scaling, caching), Operational Excellence (IaC, diagnostics, alerts).

> _See SKILL.md for full details._

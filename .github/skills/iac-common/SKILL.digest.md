<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# IaC Common Skill (Digest)

Shared IaC conventions for both Bicep and Terraform in the ALZ Accelerator.

## Module Organization

> _See SKILL.md for full directory tree._

Both Bicep and Terraform follow the same module layout: `main` orchestration file, `modules/` with subdirectories for management-groups, policy-assignments, connectivity, identity, management, security, and governance. Environment parameters live in `parameters/` (Bicep) or `environments/` (Terraform).

## Parameter Strategy

| Parameter | Dev | Staging | Prod |
|-----------|-----|---------|------|
| `environment` | `dev` | `staging` | `prod` |
| `budgetAmount` | $1,500 | $2,500 | $5,000 |
| `publicNetworkAccess` | `Enabled` | `Enabled` | `Disabled` |
| `firewallSku` | `Basic` | `Standard` | `Premium` |
| `bastionSku` | `Developer` | `Basic` | `Standard` |
| `logRetentionDays` | 30 | 90 | 365 |
| `enableDefender` | false | true | true |

**Sensitive parameters:** Never commit secrets, subscription IDs, or tenant IDs. Use Key Vault references and pipeline variables/OIDC.

## Deployment Order

1. Management Groups → 2. Policy Definitions → 3. Policy Assignments → 4. Platform subscriptions → 5. Hub networking → 6. Spoke networking → 7. Security → 8. Monitoring → 9. Governance → 10. Landing zone subscriptions

## AVM Module Selection

Check AVM registry before writing native resources. Bicep: `azure.github.io/Azure-Verified-Modules/`. Terraform: `registry.terraform.io` (search `avm-res-`). Fall back to native only when no AVM module exists.

## Validation Checklist

- [ ] Security baseline (6 rules) enforced
- [ ] Budget resource with 80/100/120% alerts
- [ ] Diagnostic settings on all resources
- [ ] CAF naming conventions followed
- [ ] Required tags present
- [ ] AVM modules used where available
- [ ] No hardcoded secrets or IDs

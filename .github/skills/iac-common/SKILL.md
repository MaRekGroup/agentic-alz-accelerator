---
name: iac-common
description: "Shared IaC conventions, module organization, deployment ordering, and validation checklists for both Bicep and Terraform. USE FOR: module structure planning, parameter strategy, AVM selection, pre-PR validation. DO NOT USE FOR: language-specific patterns (use azure-bicep-patterns or terraform-patterns)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: iac-common
---

# IaC Common Skill

Shared IaC conventions for both Bicep and Terraform in the ALZ Accelerator.

## Module Organization

```
infra/
  bicep/
    main.bicep                    # Orchestration
    modules/
      management-groups/          # MG hierarchy
      policy-assignments/         # Azure Policy
      connectivity/               # Hub-spoke networking
      identity/                   # RBAC, PIM
      management/                 # Log Analytics, Monitor
      security/                   # Defender, Sentinel
      governance/                 # Budgets, tags, naming
    parameters/
      dev.bicepparam
      staging.bicepparam
      prod.bicepparam
  terraform/
    main.tf                       # Root module
    modules/
      management-groups/
      policy-assignments/
      connectivity/
      identity/
      management/
      security/
      governance/
    environments/
      dev.tfvars
      staging.tfvars
      prod.tfvars
```

## Parameter Strategy

### Environment Differentiation

| Parameter | Dev | Staging | Prod |
|-----------|-----|---------|------|
| `environment` | `dev` | `staging` | `prod` |
| `budgetAmount` | $1,500 | $2,500 | $5,000 |
| `publicNetworkAccess` | `Enabled` | `Enabled` | `Disabled` |
| `firewallSku` | `Basic` | `Standard` | `Premium` |
| `bastionSku` | `Developer` | `Basic` | `Standard` |
| `logRetentionDays` | 30 | 90 | 365 |
| `enableDefender` | false | true | true |

### Sensitive Parameters

- Never commit secrets, subscription IDs, or tenant IDs to parameter files
- Use Key Vault references for secrets
- Use pipeline variables or OIDC for authentication

## Deployment Order

1. Management Groups
2. Policy Definitions
3. Policy Assignments
4. Platform subscriptions (Management, Connectivity, Identity)
5. Hub networking
6. Spoke networking
7. Security (Defender, Sentinel)
8. Monitoring (Log Analytics, alerts)
9. Governance (budgets, tags)
10. Landing zone subscriptions

## AVM Module Selection

Check AVM registry before writing native resources:
- Bicep: https://azure.github.io/Azure-Verified-Modules/
- Terraform: https://registry.terraform.io/namespaces/Azure (search `avm-res-`)

Only fall back to native resources when no AVM module exists.

## Validation Checklist

Before any PR:
- [ ] Security baseline (6 rules) enforced
- [ ] Budget resource with 80/100/120% alerts
- [ ] Diagnostic settings on all resources
- [ ] CAF naming conventions followed
- [ ] Required tags present
- [ ] AVM modules used where available
- [ ] No hardcoded secrets or IDs

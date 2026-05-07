<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Validate Skill (Digest)

Pre-deployment validation for Enterprise Landing Zone IaC templates — security
baseline, cost governance, and deployment readiness checks before Gate 5.

## When to Use

- Before triggering `2-platform-deploy.yml` or `3-app-deploy.yml`
- After Step 5 (Code Gen), before Gate 5 approval
- When troubleshooting deployment failures or verifying IaC changes in a PR

## Prerequisites

1. Implementation plan exists → `agent-output/{customer}/04-implementation-plan.md`
2. IaC templates exist → `infra/{bicep|terraform}/{customer}/`
3. Governance constraints exist → `agent-output/{customer}/04-governance-constraints.json`

If any missing, **STOP** and invoke the upstream agent.

## Validation Steps

| # | Check | Command | Pass Criteria |
|---|-------|---------|---------------|
| 1 | Bicep Lint | `az bicep build --file infra/bicep/{customer}/main.bicep` | Exit 0 |
| 2 | Terraform Validate | `cd infra/terraform/{customer} && terraform init -backend=false && terraform validate` | Exit 0 |
| 3 | Security Baseline | `python scripts/validators/validate_security_baseline.py infra/{iac}/{customer}/` | 0 violations |
| 4 | Cost Governance | `python scripts/validators/validate_cost_governance.py infra/{iac}/{customer}/` | Budget exists |
| 5 | Parameter Completeness | Check all required params have values/defaults | No empty required |
| 6 | AVM Module Versions | Verify pinned versions | No `latest` |
| 7 | Governance Blockers | Check `04-governance-constraints.json` for Deny-effect | 0 unresolved |

## Security Baseline Checks (Non-Negotiable)

| # | Rule | What to Check |
|---|------|---------------|
| 1 | TLS 1.2 minimum | `minimumTlsVersion` / `min_tls_version` ≥ 1.2 |
| 2 | HTTPS-only | `supportsHttpsTrafficOnly` / `https_traffic_only_enabled` = true |
| 3 | No public blob access | `allowBlobPublicAccess` / `allow_nested_items_to_be_public` = false |
| 4 | Managed Identity | `identity.type` = SystemAssigned or UserAssigned |
| 5 | Entra-only SQL auth | `azureADOnlyAuthentication` = true (SQL only) |
| 6 | No public network (prod) | `publicNetworkAccess` = Disabled (prod only) |

## Cost Governance Checks

| Check | Criteria |
|-------|----------|
| Budget resource exists | At least one `Microsoft.Consumption/budgets` |
| Alert thresholds | 80%, 100%, 120% forecast thresholds |
| Parameterized amounts | Budget amount is a parameter, not hardcoded |
| Action groups | Alerts wired to an action group |

## Workflow Integration

```text
Step 5 (Code Gen) → azure-validate → Gate 5 → Step 6 (Deploy)
```

- ALL pass → proceed to Gate 5 for Challenger review
- Any FAIL → fix and re-validate before Gate 5

## Guardrails

**DO:** Run all local checks before GitHub Actions · Report all failures together · Use exit codes for CI.

**DON'T:** Run `az deployment` or `terraform apply` locally · Skip security baseline · Approve Gate 5 with failures · Hardcode subscription IDs.

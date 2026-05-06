---
name: azure-validate
description: "Pre-deployment validation for Enterprise Landing Zones. Run deep checks on IaC (Bicep or Terraform), security baseline compliance, cost governance, and deployment readiness before triggering GitHub Actions. USE FOR: validate Bicep/Terraform, check deployment readiness, run preflight checks, security baseline validation, cost governance validation. DO NOT USE FOR: actual deployment (use deployment agent), post-deployment compliance (use monitoring agent)."
compatibility: Requires Python 3.10+, Azure CLI on PATH (for what-if), Bicep CLI or Terraform CLI.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "1.0"
  category: deployment
---

# Azure Validate — Enterprise Landing Zone Preflight

Pre-deployment validation skill for Enterprise Landing Zone infrastructure.
Runs structured checks on IaC templates, security baseline compliance, cost
governance, and prerequisites before triggering deployment workflows.

## When to Use

- Before triggering `2-platform-deploy.yml` or `3-app-deploy.yml`
- After Step 5 (Code Gen) completes, before Gate 5 approval
- When troubleshooting deployment failures
- When verifying IaC changes in a PR

## When NOT to Use

- For actual deployment execution → use Deployment agent (Envoy)
- For post-deployment compliance scanning → use Monitoring agent (Sentinel)
- For policy discovery → use Governance agent (Warden)

## Prerequisite Check

Before proceeding, verify:

1. **Implementation Plan exists** → `agent-output/{customer}/04-implementation-plan.md`
2. **IaC templates exist** → `infra/{bicep|terraform}/{customer}/`
3. **Governance constraints exist** → `agent-output/{customer}/04-governance-constraints.json`

If any are missing, **STOP** and invoke the appropriate upstream agent.

## Validation Steps

| # | Check | Command | Pass Criteria |
|---|-------|---------|---------------|
| 1 | **Bicep Lint** | `az bicep build --file infra/bicep/{customer}/main.bicep` | Exit 0, no errors |
| 2 | **Terraform Validate** | `cd infra/terraform/{customer} && terraform init -backend=false && terraform validate` | Exit 0, valid |
| 3 | **Security Baseline** | `python scripts/validators/validate_security_baseline.py infra/{iac}/{customer}/` | 0 violations |
| 4 | **Cost Governance** | `python scripts/validators/validate_cost_governance.py infra/{iac}/{customer}/` | Budget resource exists |
| 5 | **Parameter Completeness** | Check all required params have values or defaults | No empty required params |
| 6 | **AVM Module Versions** | Verify AVM modules reference pinned versions | No `latest` or missing versions |
| 7 | **Governance Blockers** | Check `04-governance-constraints.json` for Deny-effect blockers | 0 unresolved blockers |

## Validation by IaC Framework

### Bicep Validation

```bash
# Step 1: Lint
az bicep build --file infra/bicep/{customer}/main.bicep --no-restore

# Step 2: What-If (requires Azure connection — runs in GitHub Actions)
# Triggered via: gh workflow run 2-platform-deploy.yml -f action=plan

# Step 3: Security baseline
python scripts/validators/validate_security_baseline.py infra/bicep/{customer}/

# Step 4: Cost governance
python scripts/validators/validate_cost_governance.py infra/bicep/{customer}/
```

### Terraform Validation

```bash
# Step 1: Init + Validate
cd infra/terraform/{customer}
terraform init -backend=false
terraform validate

# Step 2: Plan (requires Azure connection — runs in GitHub Actions)
# Triggered via: gh workflow run 2-platform-deploy.yml -f framework=terraform -f action=plan

# Step 3: Security baseline
python scripts/validators/validate_security_baseline.py infra/terraform/{customer}/

# Step 4: Cost governance
python scripts/validators/validate_cost_governance.py infra/terraform/{customer}/
```

## Security Baseline Checks (Non-Negotiable)

These 6 rules must pass for every resource in the template:

| # | Rule | What to Check |
|---|------|---------------|
| 1 | TLS 1.2 minimum | `minimumTlsVersion` / `min_tls_version` present and ≥ 1.2 |
| 2 | HTTPS-only | `supportsHttpsTrafficOnly` / `https_traffic_only_enabled` = true |
| 3 | No public blob access | `allowBlobPublicAccess` / `allow_nested_items_to_be_public` = false |
| 4 | Managed Identity | `identity.type` = SystemAssigned or UserAssigned present |
| 5 | Entra-only SQL auth | `azureADOnlyAuthentication` = true (SQL resources only) |
| 6 | No public network (prod) | `publicNetworkAccess` = Disabled (prod environment only) |

## Cost Governance Checks

Every deployment must include:

| Check | Criteria |
|-------|----------|
| Budget resource exists | At least one `Microsoft.Consumption/budgets` resource |
| Alert thresholds | 80%, 100%, 120% forecast thresholds configured |
| Parameterized amounts | Budget amount references a parameter, not hardcoded |
| Action groups | Alert notifications wired to an action group |

## Validation Report Format

After running all checks, produce a summary:

```text
=== ALZ Preflight Validation Report ===
Customer: {customer}
Framework: {bicep|terraform}
Timestamp: {ISO8601}

✅ Bicep lint: PASS
✅ Security baseline: PASS (6/6 rules)
✅ Cost governance: PASS (budget + alerts)
⚠️ Parameter completeness: WARNING (2 optional params empty)
✅ AVM versions: PASS (all pinned)
✅ Governance blockers: PASS (0 Deny-effect blockers)

Overall: READY FOR DEPLOYMENT
```

## Integration with Workflow

```text
Step 5 (Code Gen) → azure-validate → Gate 5 → Step 6 (Deploy)
```

- If ALL checks pass → proceed to Gate 5 for Challenger review
- If any FAIL → fix issues and re-validate before Gate 5
- What-If/Plan runs in GitHub Actions (not locally) → triggered at Gate 5

## Guardrails

**DO:** Run all local checks before triggering GitHub Actions · Report all
failures together (don't stop at first) · Use exit codes for CI integration.

**DON'T:** Run `az deployment` or `terraform apply` locally · Skip security
baseline checks · Approve Gate 5 with unresolved failures · Hardcode subscription
IDs in validation commands.

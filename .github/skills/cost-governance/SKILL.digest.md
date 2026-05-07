<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Cost Governance Skill (Digest)

Enforces Azure Landing Zone cost governance: every deployment must include a
budget resource with forecast alert notifications.

## Core Rule: No Budget, No Merge

## Required Budget Alerts

| Threshold | Type | Action |
|-----------|------|--------|
| 80% | Forecast | Email notification |
| 100% | Forecast | Email + action group |
| 120% | Forecast | Email + action group |

## Validation Rules

| Rule | ID | Severity |
|------|----|----------|
| No budget resource found | COST-001 | Blocker |
| Missing 80% threshold | COST-002-80 | Blocker |
| Missing 100% threshold | COST-002-100 | Blocker |
| Missing 120% threshold | COST-002-120 | Blocker |
| Uses Actual instead of Forecasted | COST-003 | Warning |
| Hardcoded budget amount | COST-004 | Blocker |

## Per-Environment Budgets

| Environment | Typical Range |
|-------------|---------------|
| Dev/Sandbox | $500–$2,000/month |
| Staging | $2,000–$5,000/month |
| Production | $5,000–$50,000+/month |

Budget amounts are parameterized per environment — never hardcoded.

## MCP Pricing Tools

| Tool | Purpose |
|------|---------|
| `azure_cost_estimate` | Estimate cost for a resource configuration |
| `azure_bulk_estimate` | Estimate cost for multiple resources |
| `azure_price_compare` | Compare pricing across SKUs |
| `azure_ri_pricing` | Reserved instance pricing |
| `azure_region_recommend` | Recommend cost-effective regions |

## Validator

```bash
python scripts/validators/validate_cost_governance.py infra/
```

> _See SKILL.md for Bicep and Terraform implementation examples._

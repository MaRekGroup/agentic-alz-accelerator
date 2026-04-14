# Cost Governance Skill

Domain knowledge for enforcing Azure Landing Zone cost governance.

## Core Rule: No Budget, No Merge

Every deployment must include an Azure Budget resource with forecast alert
notifications at 80%, 100%, and 120% thresholds.

## Required Budget Alerts

| Threshold | Type | Action |
|-----------|------|--------|
| 80% | Forecast | Email notification |
| 100% | Forecast | Email + action group |
| 120% | Forecast | Email + action group |

## Bicep Implementation

```bicep
resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-${projectName}-${environment}'
  properties: {
    timePeriod: { startDate: '2026-01-01' }
    timeGrain: 'Monthly'
    amount: budgetAmount        // Must be a parameter, never hardcoded
    category: 'Cost'
    notifications: {
      forecast80:  { enabled: true, operator: 'GreaterThanOrEqualTo', threshold: 80,  thresholdType: 'Forecasted', contactEmails: [technicalContact] }
      forecast100: { enabled: true, operator: 'GreaterThanOrEqualTo', threshold: 100, thresholdType: 'Forecasted', contactEmails: [technicalContact] }
      forecast120: { enabled: true, operator: 'GreaterThanOrEqualTo', threshold: 120, thresholdType: 'Forecasted', contactEmails: [technicalContact] }
    }
  }
}
```

## Terraform Implementation

```hcl
resource "azurerm_consumption_budget_subscription" "budget" {
  name            = "${var.prefix}-monthly-budget"
  subscription_id = "/subscriptions/${var.subscription_id}"
  amount          = var.budget_amount_usd   # Must be a variable, never hardcoded
  time_grain      = "Monthly"
  time_period { start_date = formatdate("YYYY-MM-01'T'00:00:00Z", timestamp()) }
  dynamic "notification" {
    for_each = [80, 100, 120]
    content {
      enabled        = true
      threshold      = notification.value
      threshold_type = "Forecasted"
      operator       = "GreaterThan"
      contact_emails = var.budget_alert_emails
    }
  }
}
```

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

Budget amounts are parameterized per environment — never hardcoded:

| Environment | Typical Range |
|-------------|---------------|
| Dev/Sandbox | $500–$2,000/month |
| Staging | $2,000–$5,000/month |
| Production | $5,000–$50,000+/month |

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

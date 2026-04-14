# Cost Governance Guide

Budget alerts, forecast notifications, and anomaly detection for every deployment.

## Why Cost Governance Is Mandatory

Every IaC deployment must include cost monitoring resources. The rule is simple:
**no budget, no merge.**

Challenger reviews verify cost monitoring exists, and CI validators flag missing budget resources.

## Budget Alert Setup

Every deployment must include an Azure Budget resource with three **forecast-based** alert thresholds:

| Threshold | Type | Action |
|-----------|------|--------|
| 80% | Forecast | Email notification to owner |
| 100% | Forecast | Email notification + action group |
| 120% | Forecast | Email notification + action group |

### Forecast vs Actual Alerts

This project uses **forecast alerts exclusively** because they provide advance warning.
By the time an actual-spend alert triggers, the budget is already blown.

## Per-Environment Budgets

Use parameterized budgets that scale by environment:

| Environment | Typical Budget | Rationale |
|-------------|---------------|-----------|
| dev | Low | Minimal resources, short-lived |
| staging | Medium | Production-like but limited use |
| prod | Full | Production workload capacity |

Set the budget amount via `.bicepparam` or `terraform.tfvars` — never hardcode it.

## Anomaly Detection

In addition to budget alerts, enable Azure Cost Management anomaly alerts:
- Configure via Azure Cost Management in the portal
- Alert on spend patterns that deviate from historical baselines
- Notify the `technicalContact` parameter

## MCP Pricing Integration

The Architect agent (Step 2) uses the Azure Pricing MCP server for real-time cost estimation:

| Tool | Purpose |
|------|---------|
| `azure_cost_estimate` | Estimate costs based on usage patterns |
| `azure_bulk_estimate` | Multi-resource estimate in one call |
| `azure_price_compare` | Compare prices across regions and SKUs |
| `azure_ri_pricing` | Reserved Instance pricing and savings |
| `azure_region_recommend` | Find cheapest regions for a service |

## Running the Validator

```bash
python scripts/validators/validate_cost_governance.py infra/
```

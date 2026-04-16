---
name: azure-diagnostics
description: "KQL query templates, diagnostic settings, and monitoring patterns for Azure Landing Zone operations. USE FOR: log analytics queries, diagnostic configuration, alert rule authoring. DO NOT USE FOR: compliance monitoring (use azure-compliance), cost alerts (use cost-governance)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: azure-operations
---

# Azure Diagnostics Skill

KQL query templates and diagnostic patterns for Azure Landing Zone monitoring.

## Common KQL Queries

### Policy Compliance Summary

```kql
PolicyResources
| where type == "microsoft.policyinsights/policystates"
| where properties.complianceState != "Compliant"
| summarize NonCompliantCount = count() by
    PolicyDefinition = tostring(properties.policyDefinitionName),
    ComplianceState = tostring(properties.complianceState)
| order by NonCompliantCount desc
```

### Resource Inventory by Type

```kql
Resources
| summarize Count = count() by type, location
| order by Count desc
```

### Recent Resource Changes (Drift Detection)

```kql
ResourceChanges
| extend changeTime = todatetime(properties.changeAttributes.timestamp)
| where changeTime > ago(1h)
| extend changeType = tostring(properties.changeType)
| project changeTime, changeType,
    resourceId = tostring(properties.targetResourceId),
    changedProperties = properties.changes
| order by changeTime desc
```

### Security Baseline Violations

```kql
SecurityResources
| where type == "microsoft.security/assessments"
| where properties.status.code == "Unhealthy"
| project
    AssessmentName = tostring(properties.displayName),
    Severity = tostring(properties.metadata.severity),
    ResourceId = tostring(properties.resourceDetails.Id),
    Description = tostring(properties.metadata.description)
| order by Severity asc
```

### Cost by Resource Group (Last 30 Days)

```kql
CostManagementResources
| where type == "microsoft.costmanagement/query"
| extend cost = todouble(properties.rows[0][0])
| project ResourceGroup = tostring(properties.rows[0][1]), Cost = cost
| order by Cost desc
```

## Diagnostic Settings Template

Every resource that supports diagnostics should send:
- **Logs**: `allLogs` category group to Log Analytics
- **Metrics**: `AllMetrics` to Log Analytics

## Health Check Patterns

### Storage Account
- TLS version ≥ 1.2
- HTTPS-only enabled
- Public blob access disabled
- Managed identity configured
- Diagnostic settings present

### Key Vault
- Soft delete enabled
- Purge protection enabled
- Network rules default action = Deny
- RBAC authorization enabled
- Diagnostic settings present

### SQL Database
- Azure AD-only auth enabled
- TDE enabled
- Auditing enabled
- Long-term backup retention configured

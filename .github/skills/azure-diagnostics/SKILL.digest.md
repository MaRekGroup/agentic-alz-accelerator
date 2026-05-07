<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Azure Diagnostics Skill (Digest)

KQL query templates and diagnostic patterns for Azure Landing Zone monitoring.

## Common KQL Queries

| Query | Purpose | Key Table |
|-------|---------|-----------|
| Policy Compliance Summary | Non-compliant policy states by definition | `PolicyResources` |
| Resource Inventory by Type | Resource counts by type and location | `Resources` |
| Recent Resource Changes | Drift detection (last 1h) | `ResourceChanges` |
| Security Baseline Violations | Unhealthy security assessments by severity | `SecurityResources` |
| Cost by Resource Group | Cost breakdown (last 30 days) | `CostManagementResources` |

> _See SKILL.md for full KQL query code blocks._

## Diagnostic Settings Template

Every resource that supports diagnostics should send:
- **Logs:** `allLogs` category group → Log Analytics
- **Metrics:** `AllMetrics` → Log Analytics

## Health Check Patterns

| Resource | Checks |
|----------|--------|
| Storage Account | TLS ≥ 1.2, HTTPS-only, no public blob, managed identity, diagnostics present |
| Key Vault | Soft delete, purge protection, default Deny, RBAC auth, diagnostics present |
| SQL Database | AD-only auth, TDE, auditing, long-term backup, diagnostics present |

> _See SKILL.md for full KQL query syntax and additional patterns._

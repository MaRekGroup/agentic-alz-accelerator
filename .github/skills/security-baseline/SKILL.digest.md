<!-- digest:auto-generated from SKILL.md — do not edit manually -->

# Security Baseline Skill (Digest)

Non-negotiable security rules enforced at code gen, deploy preflight, and continuous monitoring.

## Core Rules (Non-Negotiable)

| # | Rule | Bicep Property | Terraform Argument | Applies To |
|---|------|----------------|-------------------|------------|
| 1 | TLS 1.2 minimum | `minimumTlsVersion: 'TLS1_2'` | `min_tls_version = "1.2"` | Storage, App Services, SQL, Redis |
| 2 | HTTPS-only traffic | `supportsHttpsTrafficOnly: true` | `https_traffic_only_enabled = true` | Storage, App Services, Functions |
| 3 | No public blob access | `allowBlobPublicAccess: false` | `allow_nested_items_to_be_public = false` | Storage Accounts |
| 4 | Managed Identity preferred | `identity: { type: 'SystemAssigned' }` | `identity { type = "SystemAssigned" }` | All supporting resources |
| 5 | Azure AD-only SQL auth | `azureADOnlyAuthentication: true` | `azuread_authentication_only = true` | SQL Servers, SQL MI |
| 6 | Public network disabled (prod) | `publicNetworkAccess: 'Disabled'` | `public_network_access_enabled = false` | All PaaS (prod only) |

## Extended Anti-Pattern Checks

| # | Pattern | Detection | Severity |
|---|---------|-----------|----------|
| 1 | Redis non-SSL port | `enableNonSslPort: true` | High |
| 2 | FTP without FTPS | `ftpsState` not `FtpsOnly` | High |
| 3 | Remote debugging enabled | `remoteDebuggingEnabled: true` | Critical |
| 4 | Cosmos DB local auth | `disableLocalAuth: false` | Medium |
| 5 | PostgreSQL SSL disabled | `sslEnforcement` not `Enabled` | High |
| 6 | Key Vault open network | `defaultAction` not `Deny` | High |
| 7 | Wildcard CORS origins | `allowedOrigins` contains `*` | Medium |

## Enforcement Points

1. **Code Generation (Step 5)** — Agent ensures rules in generated IaC
2. **Deploy Preflight (Step 6)** — Challenger reviews + validator script
3. **Pre-commit Hook** — `lefthook.yml` runs `validate_security_baseline.py`
4. **CI Pipeline** — `5-pr-validate.yml` runs security validator
5. **Continuous Monitoring (Step 8)** — Sentinel scans for violations

## Validator

`python scripts/validators/validate_security_baseline.py infra/`

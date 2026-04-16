---
name: security-baseline
description: "Non-negotiable security rules (TLS 1.2, HTTPS-only, managed identity, private endpoints) with Bicep and Terraform enforcement. USE FOR: code generation security checks, deployment preflight validation, continuous monitoring. DO NOT USE FOR: compliance framework mapping (use azure-compliance)."
compatibility: Works with Claude Code, GitHub Copilot, VS Code, and any Agent Skills compatible tool.
license: MIT
metadata:
  author: yeselam-tesfaye
  version: "2.0"
  category: azure-security
---

# Security Baseline Skill

Domain knowledge for enforcing the Azure Landing Zone security baseline.

## Core Rules (Non-Negotiable)

These 6 rules must be enforced at every stage: code generation, deployment preflight,
pre-commit hooks, CI validation, and continuous monitoring.

### Rule 1: TLS 1.2 Minimum
- **Bicep:** `minimumTlsVersion: 'TLS1_2'`
- **Terraform:** `min_tls_version = "1.2"`
- **Applies to:** Storage Accounts, App Services, SQL Servers, Redis Cache

### Rule 2: HTTPS-Only Traffic
- **Bicep:** `supportsHttpsTrafficOnly: true`
- **Terraform:** `https_traffic_only_enabled = true`
- **Applies to:** Storage Accounts, App Services, Function Apps

### Rule 3: No Public Blob Access
- **Bicep:** `allowBlobPublicAccess: false`
- **Terraform:** `allow_nested_items_to_be_public = false`
- **Applies to:** Storage Accounts

### Rule 4: Managed Identity Preferred
- **Bicep:** `identity: { type: 'SystemAssigned' }`
- **Terraform:** `identity { type = "SystemAssigned" }`
- **Applies to:** All resources that support managed identity

### Rule 5: Azure AD-Only SQL Authentication
- **Bicep:** `azureADOnlyAuthentication: true`
- **Terraform:** `azuread_authentication_only = true`
- **Applies to:** SQL Servers, SQL Managed Instances

### Rule 6: Public Network Disabled (Production)
- **Bicep:** `publicNetworkAccess: 'Disabled'`
- **Terraform:** `public_network_access_enabled = false`
- **Applies to:** All PaaS resources in production environments

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

```bash
python scripts/validators/validate_security_baseline.py infra/
```

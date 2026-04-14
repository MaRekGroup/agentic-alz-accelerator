# Security Baseline

Non-negotiable security requirements for all generated infrastructure code.

The security baseline is enforced by the `validate_security_baseline.py` validator
(pre-commit hook + CI pipeline) and the Challenger agent at adversarial review gates.
Violations block code generation and deployment.

## Rules

| # | Rule | Bicep Property | Terraform Argument |
|---|------|----------------|-------------------|
| 1 | TLS 1.2 minimum | `minimumTlsVersion: 'TLS1_2'` | `min_tls_version = "1.2"` |
| 2 | HTTPS-only traffic | `supportsHttpsTrafficOnly: true` | `https_traffic_only_enabled = true` |
| 3 | No public blob access | `allowBlobPublicAccess: false` | `allow_nested_items_to_be_public = false` |
| 4 | Managed Identity preferred | `identity: { type: 'SystemAssigned' }` | `identity { type = "SystemAssigned" }` |
| 5 | Azure AD-only SQL auth | `azureADOnlyAuthentication: true` | `azuread_authentication_only = true` |
| 6 | Public network disabled (prod) | `publicNetworkAccess: 'Disabled'` | `public_network_access_enabled = false` |

## Extended Checks

| Pattern | Bicep | Terraform | Severity |
|---------|-------|-----------|----------|
| Redis non-SSL port | `enableNonSslPort: true` | `enable_non_ssl_port = true` | Blocks deployment |
| FTPS allowed | `ftpsState: 'AllAllowed'` | `ftps_state = "AllAllowed"` | Blocks deployment |
| Remote debugging | `remoteDebuggingEnabled: true` | `remote_debugging_enabled = true` | Blocks deployment |
| Cosmos DB local auth | `disableLocalAuth: false` | `local_authentication_disabled = false` | Blocks deployment |
| PostgreSQL SSL disabled | `sslEnforcement: 'Disabled'` | `ssl_enforcement_enabled = false` | Blocks deployment |
| Key Vault network open | `networkAcls.defaultAction: 'Allow'` | `default_action = "Allow"` | Warning |
| Wildcard CORS | `allowedOrigins: ['*']` | `allowed_origins = ["*"]` | Warning |

## Enforcement Points

1. **Code Generation (Step 5)** — Validator runs after lint/review subagents. Violations are a hard gate.
2. **Deploy Preflight (Step 6)** — Validator runs again before what-if/plan analysis.
3. **Pre-commit hook** — `lefthook.yml` runs the validator on staged `.bicep`/`.tf` files.
4. **CI pipeline** — Runs in the parallel validation suite on every PR.
5. **Continuous Monitoring (Step 8)** — Sentinel agent detects baseline drift post-deployment.

## Running the Validator

```bash
# Check all IaC files
python scripts/validators/validate_security_baseline.py infra/

# Check a specific file
python scripts/validators/validate_security_baseline.py infra/bicep/main.bicep
```
